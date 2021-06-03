from datetime import datetime
from datetime import timedelta
import re
import calendar

import numpy as np

import roxar_api_utils.ioutil
from .profiles import Profiles
from .keyword_check import is_rate
from .profiles_interpolation import profiles_interpolation

def read_ofm(
        file_name,
        date_format,
        alias_file=None,
        undef_value=None,
        set_nonnegative=True,
        time_shift=True,
        read_type='A'):
    """Read OFM text file
    Args:
        file_name (str): OFM text file name
        date_format (str): Data format specification, as in 'DD.MM.YYYY'
        alias_file (str): Optional file name for well name alias list, None if not used
        undef_value (float):  Values to replace OFM undefined values, us one for OFM default.
        set_nonnegative (Bool): Replace negative values with zero
        time_shift (Bool):  True if time shift to Constant Backwards
        read_type (A=All, P=Production, I=Injection)
    Returns:
        roxar_api_utils Profiles object with data read
    """

    allwells, alldata, dat_order, options = _read_vol_file(
        file_name, date_format, undef_value, set_nonnegative, time_shift)

    if alias_file is not None:
        aliasinfo = roxar_api_utils.ioutil.NameAlias(alias_file)
    else:
        aliasinfo = None

    options['time_shift'] = time_shift
    options['read_type'] = read_type

    return _set_profiles(allwells, alldata, dat_order, aliasinfo, options)

def _read_key(line, options, read_order, dat_order, volmul, volprev, line_no):
    """Read keywords in file
    """

# Not supported keys:
    not_sup = ['*FILE', '*TABLENAME', '*YY/MM']
    weff_keys = ['DAYS', 'OIDAY', 'GIDAY', 'WIDAY', 'UPTIME']
    skip_keys = ['DAY', 'MONTH', 'YEAR', 'DATE', 'WELL']

    for k in not_sup:
        if line.find(k) >= 0:
            errmes = 'Keyword not supported ' + k + ' in line ' + str(line_no)
            raise ValueError(errmes)

    if max(line.find('*DAY'), line.find('*DATE')) >= 0:
        terms = line.split()
        ival = -1
        if options['undef'] is None:
            undef = 0.
        else:
            undef = options['undef']

        for t in terms:
            t = t.replace('*', '')
            if t == 'GIDAYS':
                t = 'GIDAY'
            elif t == 'OIDAYS':
                t = 'OIDAY'
            elif t == 'WIDAYS':
                t = 'WIDAY'
            elif t == 'WATR':
                t = 'WATER'
            elif t == 'WATE':
                t = 'WATER'

            read_order.append(t)
            if t not in skip_keys:
                ival += 1
                dat_order[t] = ival
                volprev.append(undef)
                volmul.append(1.)
                if t in weff_keys:
                    options['hasweff'] = True


        if options['hasweff']:
            ival += 1
            dat_order['WEFF'] = ival
            volprev.append(undef)

        if options['units'] == 'f':
            if options['mmscf']:
                if 'GAS' in dat_order.keys():
                    volmul[dat_order['GAS']] = 1000.
                if 'GINJ' in dat_order.keys():
                    volmul[dat_order['GINJ']] = 1000.

            if options['mstb']:
                if 'OIL' in dat_order.keys():
                    volmul[dat_order['OIL']] = 1000.
                if 'OINJ' in dat_order.keys():
                    volmul[dat_order['OINJ']] = 1000.
                if 'WATER' in dat_order.keys():
                    volmul[dat_order['WATER']] = 1000.
                if 'WINJ' in dat_order.keys():
                    volmul[dat_order['WINJ']] = 1000.

        else:
            if options['gkilosm3']:
                if 'GAS' in dat_order.keys():
                    volmul[dat_order['GAS']] = 1000.
                if 'GINJ' in dat_order.keys():
                    volmul[dat_order['GINJ']] = 1000.

            if options['lkilosm3']:
                if 'OIL' in dat_order.keys():
                    volmul[dat_order['OIL']] = 1000.
                if 'OINJ' in dat_order.keys():
                    volmul[dat_order['OINJ']] = 1000.
                if 'WATER' in dat_order.keys():
                    volmul[dat_order['WATER']] = 1000.
                if 'WINJ' in dat_order.keys():
                    volmul[dat_order['WINJ']] = 1000.

    if line.find('*METRIC') >= 0:
        options['units'] = 'm'
    elif line.find('*FIELD') >= 0:
        options['units'] = 'f'

    if line.find('*DAILY') >= 0:
        options['freq'] = 'd'
    elif line.find('*MONTHLY') >= 0:
        options['freq'] = 'm'
    elif line.find('*YEARLY') >= 0:
        options['freq'] = 'y'

    if line.find('*MSM3') >= 0:
        if line.find(' GAS') >= 0:
            options['gkilosm3'] = True
        if line.find(' LIQUID') >= 0:
            options['lkilosm3'] = True

    if line.find('*MSTB') >= 0:
        options['mstb'] = True

    if line.find('*MMSCF') >= 0:
        options['mmscf'] = True

    if line.find('*UCRATES') >= 0:
        options['ucrates'] = True

    if line.find('*UUCRATES') >= 0:
        options['ucrates'] = False

    if line.find('*UPTIME_FRACTIONS') >= 0:
        options['wefrac'] = True

    if line.find('*HRS_IN_DAYS') >= 0:
        options['wehrs'] = True

    if line.find('*MNS_IN_YEARS') >= 0:
        options['wemonths'] = True

    if line.find('*CUMULATIVE') >= 0:
        options['cumu'] = True

    if line.find('*ZERO_MISSING') >= 0:
        options['undef'] = 0.0

    if line.find('*IGNORE_MISSING') >= 0:
        options['undef'] = None

    return (options, read_order, dat_order, volmul, volprev)

def _check_separator(line, read_order):
    """Identify data separators, tabs or blanks
    """

    temp = line.strip()
    lread = len(read_order)
    terms1 = re.split('\t', temp)
#    terms2 = re.split(' ', temp)
    if len(terms1) == lread:
        use_tabs = True
        print('Information: Reading tab-separated table.')
    else:
        use_tabs = False
        print('Information: Reading white-space-separated table.')

    return use_tabs

def _read_data(line, date_format, read_order, options, volmul, volprev, well_name, line_no):
    """Read data line
    """
    line = re.sub(' +', ' ', line)

    if options['tabsep']:
        if line.find(' ') >= 0:
            print('Warning: Blank space in tab separated table, in line', line_no)
        line = line.replace(' ', '\t')
        terms = re.split('\t', line)
    else:
        terms = line.split()

    lread = len(read_order)
    lterms = len(terms)
    if lterms > lread:
        errmes = (
            'Warning: Superfluous data items ignored in line '
            + str(line_no)
            + '. Found '
            + str(lterms)
            + ', expected '
            + str(lread)
            + '.')
        print(errmes)
    elif lterms < lread:
        errmes = (
            'Incorrect number of data items in line '
            + str(line_no)
            + '. Found '
            + str(lterms)
            + ', expected '
            + str(lread)
            + '.')
        raise ValueError(errmes)

    day = 1
    month = 1
    year = 1900
    vdate = datetime(year, month, day)
    voldat = list(volprev)
    ival = -1
    has_date = False

    for i in range(lread):
        t = terms[i]
        if t == '':
            ival = ival + 1
        else:

            if read_order[i] == 'DAY':
                day = int(t)
            elif read_order[i] == 'MONTH':
                month = int(t)
            elif read_order[i] == 'YEAR':
                year = int(t)
            elif read_order[i] == 'DATE':
                vdate = roxar_api_utils.ioutil.string_to_datetime(t, date_format)
                has_date = True
            elif read_order[i] == 'WELL':
                well_name = t.strip()
            else:
                if not has_date:
                    vdate = datetime(year, month, day)
                ival += 1
                voldat[ival] = float(t)*volmul[ival]

# WEFF placeholder
    if options['hasweff']:
        ival += 1
        voldat[ival] = 1.0

    if options['nonneg']:
        voldat = [max(val, 0.) for val in voldat]

    return well_name, vdate, voldat

def _add_final_step(datelist, vollist, freq):
    """Add extra date at end of each well data sequence
    """

    l = len(datelist) - 1
    lastdate = datelist[l]
    lastlist = vollist[l]

    if freq == 'd':
        d = lastdate + timedelta(days=1)
    elif freq == 'm':
        newday = lastdate.day
        delta = 1
        newmonth = (((lastdate.month - 1) + delta) % 12) + 1
        newyear = lastdate.year + (((lastdate.month - 1) + delta) // 12)
        if newday > calendar.mdays[newmonth]:
            newday = calendar.mdays[newmonth]
            if newyear % 4 == 0 and newmonth == 2:
                newday += 1
        d = datetime(newyear, newmonth, newday, 0, 0, 0)
    elif freq == 'y':
        newyear = lastdate.year + 1
        newmonth = lastdate.month
        newday = lastdate.day  # Not treating Feb 29
        d = datetime(newyear, newmonth, newday, 0, 0, 0)
    else:
        errstr = 'Incorrect date frequency'
        raise ValueError(errstr)

    datelist.append(d)
    vollist.append(lastlist)

    return (datelist, vollist)

def _read_vol_file(file_name, date_format, undef_value, set_nonnegative, time_shift):
    """Read vol file
    """

    try:
        pfil = open(file_name, 'r')
    except OSError as e:
        raise OSError(e)

    well_name = 'xxx'

    options = dict()
    options['units'] = 'm'        # Metric
    options['freq'] = 'm'         # d = Daily, m=Monthly (OFM default), y=yearly
    options['gkilosm3'] = False
    options['lkilosm3'] = False
    options['mstb'] = False
    options['mmscf'] = False
    options['wehrs'] = False
    options['wemonths'] = False
    options['wefrac'] = False
    options['cumu'] = False
    options['ucrates'] = False
    options['nonneg'] = set_nonnegative
    options['undef'] = undef_value
    options['hasweff'] = False
    options['tabsep'] = False
    options['timeshift'] = time_shift

    vollist = []
    datelist = []
    volprev = []
    dateprev = datetime(1900, 1, 1)
    volmul = []
    read_order = []
    dat_order = dict()
    alldata = dict()
    dataread = False
    do_read = True
    line_no = 0
    allwells = []
    check_sep = True

    while True:
        try:
            line = pfil.readline()
            line_no += 1
        except IOError as e:
            errstr = 'Error reading OFM file, line ' + str(line_no) + '\n' + str(e)
            raise IOError(errstr)

        if not line:
            break
        line = line.replace('\n', '')
        line = line.replace('\r', '')

        temp = line.lstrip()
        ic = temp.find('--')  # Schedule comments
        if ic > 0:
            ic -= 1
            temp = temp[0:ic]
        temp = temp.rstrip(' ')
        utemp = temp.upper()

        if utemp == '':
            pass    # Skip blank lines
        elif ic == 0:
            pass    # Skip Schedule comments
        elif utemp.startswith('\*'):
            pass    # Skip comments
        elif utemp.find('*READOFF') >= 0:
            do_read = False
        elif utemp.find('*READON') >= 0:
            do_read = True
        elif not do_read:
            pass
        elif utemp.find('*NAME') >= 0:
            if dataread:
                if time_shift:
                    alldata[well_name] = _add_final_step(datelist, vollist, options['freq'])
                else:
                    alldata[well_name] = (datelist, vollist)
                datelist = []
                vollist = []
                dateprev = datetime(1900, 1, 1)
                dataread = False

            well_name = temp[5:].strip()
            allwells.append(well_name)

        elif utemp.find('*') >= 0:
            options, read_order, dat_order, volmul, volprev = _read_key(
                utemp, options, read_order, dat_order, volmul, volprev, line_no)
        else:
            if check_sep:
                options['tabsep'] = _check_separator(temp, read_order)
                check_sep = False

            wname, vdat, voldat = _read_data(
                temp, date_format, read_order, options, volmul, volprev, well_name, line_no)
            if wname != well_name:
                if dataread:
                    if time_shift:
                        alldata[well_name] = _add_final_step(datelist, vollist, options['freq'])
                    else:
                        alldata[well_name] = (datelist, vollist)
                    datelist = []
                    vollist = []
                    dateprev = datetime(1900, 1, 1)
                well_name = wname
                allwells.append(well_name)

            dataread = True

            if options['hasweff']:
                voldat = _process_weff(vdat, voldat, dat_order, options)
            if options['freq'] == 'm':
                voldat = _process_monthly(vdat, voldat, dat_order)
            elif options['freq'] == 'y':
                voldat = _process_yearly(vdat, voldat, dat_order)

            if vdat > dateprev:
                vollist.append(voldat)
                datelist.append(vdat)
                dateprev = vdat
            else:
                errmes = 'Incorrect date order found in line ' + str(line_no) + '.'
                raise ValueError(errmes)

            if options['undef'] is None:
                volprev = voldat


    if dataread:
        if time_shift:
            alldata[well_name] = _add_final_step(datelist, vollist, options['freq'])
        else:
            alldata[well_name] = (datelist, vollist)

    return (allwells, alldata, dat_order, options)

def _process_weff(vdat, voldat, dat_order, options):

    iweff = dat_order['WEFF']

    if not options['wefrac']:
        if options['freq'] == 'd':
            if options['wehrs']:
                for k in ('DAYS', 'GIDAY', 'OIDAY', 'WIDAY'):
                    if k in dat_order.keys():
                        voldat[dat_order[k]] = voldat[dat_order[k]]/24.
        elif options['freq'] == 'm':
            days_in_month = float(calendar.monthrange(vdat.year, vdat.month)[1])
            print( 'days in month: ',days_in_month,vdat.month )

            for k in ('DAYS', 'GIDAY', 'OIDAY', 'WIDAY'):
                if k in dat_order.keys():
                    print( 'dat_order = ',k, ':', voldat[dat_order[k]] )
                    voldat[dat_order[k]] = voldat[dat_order[k]]/days_in_month
                    print( 'dat_order = ',k, ':', voldat[dat_order[k]] )
                    print()
        elif options['freq'] == 'y':
            if options['wemonths']:
                for k in ('DAYS', 'GIDAY', 'OIDAY', 'WIDAY'):
                    if k in dat_order.keys():
                        voldat[dat_order[k]] = voldat[dat_order[k]]/12.

    if 'UPTIME' in dat_order.keys():
        voldat[iweff] = voldat[dat_order['UPTIME']]
    elif ('GIDAY' in dat_order.keys()
          and 'GINJ' in dat_order.keys()
          and voldat[dat_order['GINJ']]) > 0.:
        voldat[iweff] = voldat[dat_order['GIDAY']]
    elif ('OIDAY' in dat_order.keys()
          and 'OINJ' in dat_order.keys()
          and voldat[dat_order['OINJ']]) > 0.:
        voldat[iweff] = voldat[dat_order['OIDAY']]
    elif ('WIDAY' in dat_order.keys()
          and 'WINJ' in dat_order.keys()
          and voldat[dat_order['WINJ']]) > 0.:
        voldat[iweff] = voldat[dat_order['WIDAY']]
    elif 'DAYS' in dat_order.keys():
        voldat[iweff] = voldat[dat_order['DAYS']]

# Adjust rates for well efficiency
    if options['ucrates'] and voldat[iweff] > 0:
        for k in ('GAS', 'OIL', 'WATER', 'GINJ', 'OINJ', 'WINJ'):
            if k in dat_order.keys():
                voldat[dat_order[k]] = voldat[dat_order[k]]/voldat[iweff]

    return voldat

def _process_monthly(vdat, voldat, dat_order):

    days_in_month = float(calendar.monthrange(vdat.year, vdat.month)[1])
    rate_keys = ('GAS', 'OIL', 'WATER', 'GINJ', 'OINJ', 'WINJ')

    for k in rate_keys:
        if k in dat_order.keys():
            voldat[dat_order[k]] = voldat[dat_order[k]]/days_in_month

    return voldat

def _process_yearly(vdat, voldat, dat_order):

    y1 = datetime(vdat.year, 1, 1)
    y2 = datetime(vdat.year+1, 1, 1)
    dy = y2 - y1
    days_in_year = dy.days
    rate_keys = ('GAS', 'OIL', 'WATER', 'GINJ', 'OINJ', 'WINJ')

    for k in rate_keys:
        if k in dat_order.keys():
            voldat[dat_order[k]] = voldat[dat_order[k]]/days_in_year

    return voldat

def _set_val(profiles, vtime, indx, vollist, vt, keyword, wname, iw, zunit, options):

    if is_rate(keyword):
        if options['timeshift']:
            itype = 'B'
        else:
            itype = 'F'
    else:
        itype = 'L'

    no_steps = vt.size
    vq = np.zeros(no_steps)

    if options['timeshift']:
        for i in range(no_steps-1):
            vi = vollist[i]
            vq[i+1] = vi[indx]
    else:
        for i in range(no_steps):
            vi = vollist[i]
            vq[i] = vi[indx]

    vqall = np.zeros(vtime.size)
    for i, t in enumerate(vtime):
        vqall[i] = profiles_interpolation(t, vt, vq, itype)

    profiles.set_vector(keyword, vqall, name=wname, num=iw, unit=zunit)
    return profiles

def _set_profiles(allwells, alldata, dat_order, aliasinfo, options):
    """Store data as Profiles object
    """

    dateset = set()
    for w in allwells:
        datelist, vollist = alldata[w]
        dateset.update(datelist)

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


    if options['time_shift']:
        backw = True
    else:
        backw = False

    read_prod = False
    read_inje = False
    if options['read_type'] == 'P':
        read_prod = True
    elif options['read_type'] == 'I':
        read_inje = True
    else:
        read_prod = True
        read_inje = True

    startd = datelist[0]
    profiles = Profiles(profid='OFM', startdate=startd, backwards=backw)
    profiles.set_vector('TIME', vtime, unit='DAYS')
    profiles.set_vector('DAY', vday, unit=' ')
    profiles.set_vector('MONTH', vmonth, unit=' ')
    profiles.set_vector('YEAR', vyear, unit=' ')

    dkeys = dict()
    if options['cumu']:
        zunit = 'SM3'
        if read_prod:
            if 'GAS' in dat_order.keys():
                dkeys['GAS'] = ('WGPT', zunit)
            if 'OIL' in dat_order.keys():
                dkeys['OIL'] = ('WOPT', zunit)
            if 'WATER' in dat_order.keys():
                dkeys['WATER'] = ('WWPT', zunit)
        if read_inje:
            if 'GINJ' in dat_order.keys():
                dkeys['GINJ'] = ('WGIT', zunit)
            if 'OINJ' in dat_order.keys():
                dkeys['OINJ'] = ('WOIT', zunit)
            if 'WINJ' in dat_order.keys():
                dkeys['WINJ'] = ('WWIT', zunit)
    else:
        zunit = 'SM3/D'
        if read_prod:
            if 'GAS' in dat_order.keys():
                dkeys['GAS'] = ('WGPR', zunit)
            if 'OIL' in dat_order.keys():
                dkeys['OIL'] = ('WOPR', zunit)
            if 'WATER' in dat_order.keys():
                dkeys['WATER'] = ('WWPR', zunit)
        if read_inje:
            if 'GINJ' in dat_order.keys():
                dkeys['GINJ'] = ('WGIR', zunit)
            if 'OINJ' in dat_order.keys():
                dkeys['OINJ'] = ('WOIR', zunit)
            if 'WINJ' in dat_order.keys():
                dkeys['WINJ'] = ('WWIR', zunit)

    if 'BHP' in dat_order.keys():
        dkeys['BHP'] = ('WBHP', 'BARS')
    if 'THP' in dat_order.keys():
        dkeys['THP'] = ('WTHP', 'BARS')
    if 'WEFF' in dat_order.keys():
        dkeys['WEFF'] = ('WEFF', ' ')

    iw = 0
    for w in allwells:
        iw = iw + 1
        datelist, vollist = alldata[w]
        no_steps = len(datelist)
        if aliasinfo is not None:
            wname = aliasinfo.get_alias(w)
        else:
            wname = w

        vt = np.zeros(no_steps)
        for i, d in enumerate(datelist):
            if i == 0:
                dt = datelist[0] - startd
                t = dt.days
            else:
                dt = datelist[i] - datelist[i-1]
                t = t + dt.days
            vt[i] = t

        for k, val in dkeys.items():
            indx = dat_order[k]
            zkey, zunit = val
            profiles = _set_val(profiles, vtime, indx, vollist, vt, zkey, wname, iw, zunit, options)

        del vt

    return profiles
