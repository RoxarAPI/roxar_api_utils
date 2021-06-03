"""Write/read profile data as text file
"""

import numpy as np
from datetime import datetime

from .profiles import Profiles
from .keyword_check import is_rate
from .keyword_check import is_cumulative
from .profiles_interpolation import profiles_interpolation

def _dat_str(day, month, year):
    """Create date string
    """
    dd = int(day)
    if dd < 10:
        sd = '0' + str(dd)
    else:
        sd = str(dd)

    mm = int(month)
    if mm < 10:
        sm = '0' + str(mm)
    else:
        sm = str(mm)

    sy = str(int(year))

    return sd + '.' + sm + '.' + sy

def _next_item(line):
    """Return next item in line
    """
    line = line.lstrip()
    if line == '':
        return (None,None)

    ib1 = line.find('"')
    ib2 = line.find("'")

    ib = -1
    if ib1 == 0:
        ib = 0
        sep = '"'
    elif ib2 == 0:
        ib = 0
        sep = "\'"

    if ib == 0:
        ie = line[1:].find(sep)
        if ie >= 0:
            item = line[1:ie+1]
            item = item.strip()
            ib = ie + 3
            if ib <= len(line):
                rest = line[ie+3:]
            else:
                rest = ''
        else:
            errmes = 'Missing quotation mark.'
            raise ValueError(errmes)
    else:
        ie = 10000
        if line[0] == ',':
            line = line[1:]
        ie1 = line.find(',')
        ie2 = line.find(' ')
        if ie1 > 0:
            ie = min(ie, ie1)
        if ie2 > 0:
            ie = min(ie, ie2)
        ie = min(ie,len(line))
        item = line[0:ie]
        rest = line[ie+1:]

    return (item,rest)

def _split_line(line):
    """Split a line in terms, but take care of quotation marks
    """
    terms = []
    while True:
        item,line = _next_item(line)
        if item is not None:
            terms.append(item)
        else:
            break
    return terms

def write_welldata_txt(profiles,outfile):
    """Write profiles well data in column format which can be read by RMS
    """

    try:
        fp = open(outfile, 'w')
    except OSError as e:
        raise OSError(e)

    allkeys = ('WOPR',
    'WGPR',
    'WWPR',
    'WOIR',
    'WGIR',
    'WWIR',
    'WOPRH',
    'WGPRH',
    'WWPRH',
    'WOPT',
    'WGPT',
    'WWPT',
    'WOIT',
    'WGIT',
    'WWIT',
    'WEFF',
    'WBHP',
    'WTHP')

    if profiles.backwards:
        print( '# Backwards constant\n#', file=fp)
    else:
        print( '# Forwards constant\n#', file=fp)

    print('WELL      DATE  ',end='', file=fp)

    vday = profiles.get_vector('DAY')
    vmonth = profiles.get_vector('MONTH')
    vyear = profiles.get_vector('YEAR')
    if vday is None or vmonth is None or vyear is None:
        fp.close()
        errmes = 'Missing DAY/MONTH/YEAR keywords in profiles data.'
        print('\n', errmes, '\n')
        raise ValueError()
    day = vday.profdata
    month = vmonth.profdata
    year = vyear.profdata

    wellset = profiles.wellset()
    keys = []
    units = []
    for i,key in enumerate(allkeys):
        if key in profiles.keywords:
            keys.append(key)
            ix = profiles.keywords.index(key)
            units.append(profiles.units[ix])
            print(key, '  ', end='', file=fp)
    print(file=fp)
    print('""        ""   ', end='',file=fp)
    for key in units:
        if key == '':
            key = '""'
        print(key, '  ', end='', file=fp)
    print(file=fp)

    for well in sorted(wellset):
        for i in range(profiles.nosteps):
            print( '"', well, '"', sep='', end='', file=fp)
            sdat = _dat_str(day[i], month[i], year[i])
            print('  ',sdat, end='', file=fp)

            for key in keys:
                vdat = profiles.get_vector(key,well)
                if vdat is None:
                    wdat = 0.
                else:
                    wdat = vdat.profdata[i]
                print( '  ', wdat, end='', file=fp)
            print(file=fp)

    fp.close()

    return None

def read_welldata_txt(infile):
    """Read profiles well data in column format
    """

    try:
        fp = open(infile, 'r')
    except OSError as e:
        print( '\nError opening file ', infile, '\n')
        raise OSError(e)

    allkeys = ('WELL',
    'DATE',
    'WOPR',
    'WGPR',
    'WWPR',
    'WOPRH',
    'WGPRH',
    'WWPRH',
    'WOPT',
    'WGPT',
    'WWPT',
    'WEFF',
    'WBHP',
    'WTHP')

    unit_line = False
    sdat = dict()
    wellset= set()
    dateset = set()
    keywords = []
    units = []
    line_no = 0
    no_keys = 0
    backw = True

    while True:
        try:
            line = fp.readline()
            line_no += 1
        except IOError as e:
            fp.close()
            errmes = '\nError reading line ' + str(line_no) + '.'
            print(errmes)
            print(str(e), '\n')
            raise IOError()

        if not line:
            break
        line = line.replace('\n', '')
        line = line.replace('\r', '')

        ic = line.find('#')
        if ic >0:
            line = line[0:ic-1]

        try:
            terms = _split_line(line)
        except ValueError as e:
            fp.close()
            errmes = '\nError reading line ' + str(line_no) + '.'
            print(errmes)
            print(str(e), '\n')
            raise

        if line == '':
            pass
        elif ic == 0:
            if len(terms) > 1:
                if terms[1] == 'Backwards':
                    backw = True
                elif terms[1] == 'Forwards':
                    backw = False
        elif terms[0] in allkeys:
            unit_line = True
            for t in terms:
                if t in allkeys:
                    if t != 'WELL' and  t != 'DATE':
                        keywords.append(t.upper())
                else:
                    fp.close()
                    errmes = '\nError reading line ' + str(line_no) + '.'
                    print(errmes)
                    errmes = 'Non-supported keyword ' + t + '.\n'
                    print(errmes)
                    raise ValueError()
            no_keys = len(keywords) + 2

        elif unit_line:
            units = terms
            if len(units) != no_keys:
                errmes = '\nError reading line ' + str(line_no) + '.'
                print(errmes)
                errmes = ('Incorrect number of units specified.'
                    + '\n'
                    + 'Expected '
                    + str(no_keys)
                    + ', found '
                    + str(len(terms))
                    + '.\n')
                print(errmes)
                raise ValueError()
            unit_line = False

        else:
            try:
                if len(terms) != no_keys:
                    fp.close()
                    errmes = '\nError reading line ' + str(line_no) + '.'
                    print(errmes)
                    errmes = ('Unexpected number of data items.'
                    + '\n'
                    + 'Expected '
                    + str(no_keys)
                    + ', found '
                    + str(len(terms))
                    + '.')
                    print(errmes, '\n')
                    raise IOError()

                wname = terms[0]
                wellset.add(wname)
                sd,sm,sy = terms[1].split('.')
                dd = int(sd)
                mm = int(sm)
                yy = int(sy)
                nowdate = datetime(yy,mm,dd)
                dateset.add(nowdate)
                if wname in sdat:
                    dt = nowdate - prevdate
                    nowtime = nowtime + dt.days
                else:
                    nowtime = 0.
                datlin = [nowdate,nowtime]
                for i in range(2,len(terms)):
                    datlin.append(float(terms[i]))
                if wname in sdat:
                    sdat[wname].append(datlin)
                else:
                    sdat[wname] = [datlin,]
                prevdate = nowdate
            except ValueError as e:
                fp.close()
                errmes = '\nError reading line ' + str(line_no) + '.'
                print(errmes, '\n', str(e), '\n')
                raise

    if len(dateset) == 0:
        fp.close()
        errmes = 'No time step data found'
        raise ValueError(errmes)

    datelist = list(dateset)
    datelist.sort()

    no_steps = len(datelist)
    vtime = np.zeros(no_steps)
    vday = np.zeros(no_steps)
    vmonth = np.zeros(no_steps)
    vyear = np.zeros(no_steps)
    for i, d in enumerate(datelist):
        if i == 0:
            t = 0.
        else:
            dt = datelist[i]- datelist[i-1]
            t = t + dt.days
        vtime[i] = t
        vday[i] = d.day
        vmonth[i] = d.month
        vyear[i] = d.year

    startd = datelist[0]
    profiles = Profiles(profid='TEXT', startdate=startd, backwards=backw)
    profiles.set_vector('TIME', vtime, unit='DAYS')
    profiles.set_vector('DAY', vday, unit=' ')
    profiles.set_vector('MONTH', vmonth, unit=' ')
    profiles.set_vector('YEAR', vyear, unit=' ')

    for iw, wname in enumerate(wellset):
        sumdat = sdat[wname]
        nos = len(sumdat)
        vt = np.zeros(nos)
        for i in range(nos):
            vdat = sumdat[i]
            vt[i] = vdat[1]
        for ik, key in enumerate(keywords):
            vs = np.zeros(nos)
            for i in range(nos):
                vdat = sumdat[i]
                vs[i] = vdat[ik+2]

            if is_rate(key):
                if backw:
                    itype = 'B'
                else:
                    itype = 'F'
            elif is_cumulative(key):
                itype = 'V'
            else:
                itype = 'L'

            vsall = np.zeros(no_steps)

            for i, t in enumerate(vtime):
                vsall[i] = profiles_interpolation(t, vt, vs, itype)

            profiles.set_vector(key, vsall, name=wname, num=iw, unit=units[ik+2])

    fp.close()

    return profiles
