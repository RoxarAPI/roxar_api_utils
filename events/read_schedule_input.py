"""Functions for reading Schedule input files: net, cnt, tub, ev
"""
from datetime import datetime

import roxar
import roxar.events

def _get_wellname(schedname):
    """Based on Schedule well name, including branch symbol, return well and wellbore names
    """

    iloc = schedname.find('%')
    if iloc > 0:
        well_name = schedname[:iloc]
    else:
        well_name = schedname

    return well_name

def _check_rest(datestr, symb):
    """Check if date contains mixed symbols like SOS + 1 MONTH
    """
    rest = datestr.strip(symb)
    rest = rest.strip()
    if rest != '':
        errmes = 'Error reading Schedule file.  Cannot handle date string ' + datestr
        raise ValueError(errmes)
    return None

def _read_date(datestr, line_no, symbdate):
    """Read date from Schedule input files
    """

    for key, value in symbdate.items():
        estr = '\"' + key + '\"'
        ix1 = datestr.find(estr)
        if ix1 >= 0:
            _check_rest(datestr, estr)
            return value

        estr = "\'" + key + "\'"
        ix1 = datestr.find(estr)
        if ix1 >= 0:
            _check_rest(datestr, estr)
            return value

        ix1 = datestr.find(key)
        if ix1 >= 0:
            _check_rest(datestr, key)
            return value

    sepdef = (r'.', r'-', r'*', r'+', r':', r';', '\\', r'/')
    dateok = False
    for sep in sepdef:
        ix1 = datestr.find(sep)
        if ix1 >= 0:
            terms = datestr.split(sep)
            try:
                day = int(terms[0])
                month = int(terms[1])
                year = int(terms[2])
                dateok = True
                break
            except:
                errmes = 'Cannot read date format: ' + datestr + ' found in line ' + str(line_no) + '.'
                raise ValueError(errmes)

    if not dateok:
        ida = 0
        imo = 3
        iye = 6
        try:
            day = int(datestr[ida:ida+2])
            month = int(datestr[imo:imo+2])
            year = int(datestr[iye:iye+4])
        except:
            errmes = 'Cannot read date format: ' + datestr + ' found in line ' + str(line_no) + '.'
            raise ValueError(errmes)

    return datetime(year, month, day)

def _read_items(line, nitem, line_no):
    """Interpret data in line, including repeated counts
    """

    nval = 0
    line = line.replace(',', ' ')
    terms = line.split()
    qtxt = False

# First handle quotations
    ite = []
    for trm in terms:
        if trm.startswith('/'):
            break

        elif trm.startswith("\'"):
            if trm.endswith("\'"):
                trm = trm.replace("\'", '')
                ite.append(trm)
                nval += 1
            else:
                txt = trm
                qtxt = True

        elif trm.startswith('\"'):
            if trm.endswith('\"'):
                trm = trm.replace('\"', '')
                ite.append(trm)
                nval += 1
            else:
                txt = trm
                qtxt = True

        elif qtxt:
            txt = txt + trm
            if txt.endswith("\'"):
                txt = txt.replace("\'", '')
                ite.append(txt)
                nval += 1
                qtxt = False
            elif txt.endswith('\"'):
                txt = txt.replace('\"', '')
                ite.append(txt)
                nval += 1
                qtxt = False
        else:
            ite.append(trm)

# Handle repeated counts:

        items = []
        nval = 0
        for trm in ite:
            iloc = trm.find('*')
            if iloc >= 0:
                if trm == '*':
                    items.append(trm)
                    nval += 1
                else:
                    scount = trm.replace('*', '')
                    try:
                        ncount = int(scount)
                    except ValueError as e:
                        errmes = 'Error reading Schedule file, line ' + str(line_no) + ': ' + trm
                        raise ValueError(errmes)
                    for itr in range(ncount):
                        items.append('*')
                        nval += 1
            else:
                items.append(trm)
                nval += 1


        if nval < nitem:
            for itr in range(nval, nitem):
                items.append('*')

    return items

def _read_float(item, line_no):

    val = None
    if item != '*':
        try:
            val = float(item)
        except ValueError:
            errmes = (
                'Failed to read float value in Schedule file, line '
                + str(line_no)
                + ': '
                + item)
            raise ValueError(errmes)

    return val

def _read_int(item, line_no):

    val = None
    if item != '*':
        try:
            val = int(item)
        except ValueError:
            errmes = (
                'Failed to read integer value in Schedule file, line '
                + str(line_no)
                + ': '
                + item)
            raise ValueError(errmes)

    return val


def read_schedule_net(file_name, symbdate):
    """Read Schedule net file with well group definitions
    Args:
        file_name (str): File name for event file
        symbdate (dictionary of datetime): Dates for symbolic dates, like SOS
    """

    try:
        pfil = open(file_name, 'r')
    except OSError as e:
        errmes = 'Error opening file ' + file_name + '\n' + str(e)
        raise OSError(errmes)

    event_date = symbdate['SOS']
    elist = []

    line_no = 0
    while True:
        try:
            line = pfil.readline()
        except IOError:
            errmes = 'Error reading Schedule net file, line ' + str(line_no + 1)
            raise IOError(errmes)

        if not line:
            break
        line_no += 1

        temp = line.strip()
        ic2 = temp.find('*')
        if temp == '':
            pass    # Skip blank lines
        elif temp.startswith('--'):
            pass    # Skip comments starting with --
        else:
            terms = temp.split()
            if terms[0] == '*DATE':
                event_date = _read_date(terms[1], line_no, symbdate)
            elif terms[0] == '*GROUPNODE':
                is_leaf = False
            elif terms[0] == '*LEAFNODE':
                is_leaf = True
            elif ic2 >= 0:
                errstr = 'Unexpected keyword: ' + terms[0]
                raise ValueError(errstr)
            else:
                trm0 = terms[0].strip("\'")
                trm1 = terms[1].strip("\'")
                eve = roxar.events.Event.create(roxar.EventType.GMEMBER, event_date, [trm1])
                eve['MEMBER'] = trm0
                elist.append(eve)

                if is_leaf:    #Default well info
                    eve = roxar.events.Event.create(roxar.EventType.WTYPE, event_date, [trm0])
                    eve['TYPE'] = 'Producer'
                    eve['PHASE'] = 'Oil'
                    elist.append(eve)

    pfil.close()

    return elist

def read_schedule_ev(file_name, symbdate, trajectory_type='Drilled trajectory'):
    """Read Schedule event file
    Args:
        file_name (str): File name for event file
        symbdate (dictionary of datetime): Dates for symbolic dates, like SOS
        trajectory_type (str): RMS trajectory definition
    """

    try:
        pfil = open(file_name, 'r')
    except OSError as e:
        errmes = 'Error opening file ' + file_name + '\n' + str(e)
        raise OSError(errmes)

    event_date = symbdate['SOS']
    elist = []
    well_name = 'xxx'
    wellbore_name = well_name
#    unit = 'METRIC'   Currently not used
    line_no = 0
    wperfno = dict()
    is_wconhist = False

    def_mdstart = 0.
    def_mdend = 10000.

    wells_def_mdstart = []   # List of wells with defaulted MDSTART
    wells_def_mdend = []

    while True:
        try:
            line = pfil.readline()
        except IOerror:
            errmes = 'Error reading Schedule event file, line ' + str(line_no + 1)
            raise IOError(errmes)

        if not line:
            break
        line_no = line_no + 1

        temp = line.strip()
        utemp = temp.upper()

        if temp == '':
            pass    # Skip blank lines
        elif temp.startswith('--'):
            pass    # Skip comments starting with --
        else:
            terms = utemp.split()
            no_terms = len(terms)
            if terms[0] == 'WELLNAME':
                terms = temp.split()
                well_name = _get_wellname(terms[1])
                wellbore_name = terms[1]
                wperfno[wellbore_name] = 0
            elif terms[0] == 'UNITS':
                pass
#                unit = terms[1]    # Currently not used
            elif no_terms > 1:
                if no_terms > 2 and terms[2].find('(') >= 0:
                    id2 = 0
                    for i in range(2,no_terms):
                        if terms[i].find(')') >= 0:
                            id2 = i + 1
                            id3 = id2 + 1
                            id4 = id3 + 1
                            id5 = id4 + 1
                            id6 = id5 + 1
                            break
                    if id2 == 0:
                        errmes = 'Missing left bracket in line ' + str(line_no)
                        raise ValueError(errmes)
                else:
                    id2 = 2
                    id3 = 3
                    id4 = 4
                    id5 = 5
                    id6 = 6

                if is_wconhist:
                    is_wconhist = False
                    rdat = _read_items(temp, 9, line_no)
#                    is_open = rdat[0]   # Currently not used
#                    rtype = rdat[1]     # Currently not used
                    srateo = _read_float(rdat[2], line_no)
                    sratew = _read_float(rdat[3], line_no)
                    srateg = _read_float(rdat[4], line_no)
                    ivfp = _read_int(rdat[5], line_no)
                    alq = _read_float(rdat[6], line_no)
                    vthp = _read_float(rdat[7], line_no)
                    vbhp = _read_float(rdat[8], line_no)
                    if vthp is not None or vbhp is not None:
                        eve = roxar.events.Event.create(
                            roxar.EventType.WHISTPRES, event_date, [well_name])
                        if vthp is not None:
                            eve['THP'] = vthp
                        if vbhp is not None:
                            eve['BHP'] = vbhp
                        elist.append(eve)
                    if srateo is not None or sratew is not None or srateg is not None:
                        eve = roxar.events.Event.create(
                            roxar.EventType.WHISTRATE, event_date, [well_name])
                        if srateo is not None:
                            eve['SRATEO'] = srateo
                        if sratew is not None:
                            eve['SRATEW'] = sratew
                        if srateg is not None:
                            eve['SRATEG'] = srateg
                        elist.append(eve)
                    if ivfp is not None:
                        eve = roxar.events.Event.create(
                            roxar.EventType.WLIFTTABLE, event_date, [well_name])
                        eve['TABLEID'] = str(ivfp)
                        elist.append(eve)
                    if alq is not None:
                        eve = roxar.events.Event.create(
                            roxar.EventType.WLIFTGAS, event_date, [well_name])
                        eve['RATEG'] = alq
                        elist.append(eve)
                elif terms[1] == 'PERFORATION':
                    event_date = _read_date(terms[0], line_no, symbdate)
                    traj_name = [well_name, wellbore_name, trajectory_type]
                    eve = roxar.events.Event.create(roxar.EventType.PERF, event_date, traj_name)
                    try:
                        if terms[id2] == '*':
                            eve['MDSTART'] = def_mdstart
                            wells_def_mdstart.append(wellbore_name)
                        else:
                            eve['MDSTART'] = float(terms[id2])
                        if terms[id3] == '*':
                            eve['MDEND'] = def_mdend
                            wells_def_mdend.append(wellbore_name)
                        else:
                            eve['MDEND'] = float(terms[id3])
                        if terms[id4] != '*':
                            eve['RADIUS'] = 0.5*float(terms[id4])
                        if terms[id5] != '*':
                            eve['SKIN'] = float(terms[id5])
                        eve['PERFID'] = chr(wperfno[wellbore_name] + ord('A'))
                        wperfno[wellbore_name] += 1
                        if no_terms > id6 and terms[id6].startswith('--'):
                            iloc = line.find('--')
                            com = line[iloc+2:]
                            com = com.lstrip()
                            com = com.strip('\n')
                            eve['COMMENT'] = com
                    except ValueError:
                        errstr = 'Failed to read PERFORATION data in line ' + str(line_no)
                        raise ValueError(errstr)

                    elist.append(eve)

                elif terms[1] == 'BAREFOOT':
                    event_date = _read_date(terms[0], line_no, symbdate)
                    traj_name = [well_name, wellbore_name, trajectory_type]
                    eve = roxar.events.Event.create(roxar.EventType.PERF, event_date, traj_name)
                    try:
                        if terms[id2] == '*':
                            eve['MDSTART'] = def_mdstart
                        else:
                            eve['MDSTART'] = float(terms[id2])
                        eve['MDEND'] = def_mdend
                        eve['RADIUS'] = 0.5*float(terms[id3])
                        eve['SKIN'] = float(terms[id4])
                        if no_terms > id5 and terms[id5].startswith('--'):
                            iloc = line.find('--')
                            com = line[iloc+2:]
                            com = com.lstrip()
                            com = com.strip('\n')
                            eve['COMMENT'] = com
                    except ValueError:
                        errstr = 'Failed to read BAREFOOT data in line ' + str(line_no)
                        raise ValueError(errstr)

                    elist.append(eve)

                elif terms[1] == 'SQUEEZE':
                    event_date = _read_date(terms[0], line_no, symbdate)
                    traj_name = [well_name, wellbore_name, trajectory_type]
                    eve = roxar.events.Event.create(roxar.EventType.SQUEEZE, event_date, traj_name)
                    try:
                        if terms[id2] == '*':
                            eve['MDSTART'] = def_mdstart
                        else:
                            eve['MDSTART'] = float(terms[id2])
                        if terms[id3] == '*':
                            eve['MDEND'] = def_mdend
                        else:
                            eve['MDEND'] = float(terms[id3])
                        if no_terms > id4 and terms[id4].startswith('--'):
                            iloc = line.find('--')
                            com = line[iloc+2:]
                            com = com.lstrip()
                            com = com.strip('\n')
                            eve['COMMENT'] = com
                    except ValueError:
                        errstr = 'Failed to read SQUEEZE data in line ' + str(line_no)
                        raise ValueError(errstr)

                    elist.append(eve)

                elif terms[1] == 'PLUG':
                    event_date = _read_date(terms[0], line_no, symbdate)
                    traj_name = [well_name, wellbore_name, trajectory_type]
                    eve = roxar.events.Event.create(roxar.EventType.SQUEEZE, event_date, traj_name)
                    try:
                        if terms[id2] == '*':
                            eve['MDSTART'] = def_mdstart
                        else:
                            eve['MDSTART'] = float(terms[id2])
                        eve['MDEND'] = def_mdend
                        if no_terms > id3 and terms[id3].startswith('--'):
                            ix = line.find('--')
                            com = line[ix+2:]
                            com = com.lstrip()
                            com = com.strip('\n')
                            eve['COMMENT'] = com
                    except ValueError:
                        errstr = 'Failed to read PLUG data in line ' + str(line_no)
                        raise ValueError(errstr)

                    elist.append(eve)

                elif terms[1] == 'BHP':
                    event_date = _read_date(terms[0], line_no, symbdate)
                    eve = roxar.events.Event.create(
                        roxar.EventType.WHISTPRES, event_date, [well_name])
                    try:
                        eve['BHP'] = float(terms[id2])
                    except ValueError:
                        errstr = 'Failed to read BHP data in line ' + str(line_no)
                        raise ValueError(errstr)
                    elist.append(eve)

                elif terms[1] == 'VFP':
                    event_date = _read_date(terms[0], line_no, symbdate)
                    eve = roxar.events.Event.create(
                        roxar.EventType.WLIFTTABLE, event_date, [well_name])
                    try:
                        eve['TABLEID'] = str(terms[id2])
                    except ValueError:
                        errstr = 'Failed to read VFP data in line ' + str(line_no)
                        raise ValueError(errstr)
                    elist.append(eve)

                elif terms[1] == 'KEYWORD':
                    event_date = _read_date(terms[0], line_no, symbdate)
                    if terms[2] == 'WCONHIST':
                        is_wconhist = True

    if len(wells_def_mdstart) > 0:
        print('Perforation MDSTART defaulted in', len(wells_def_mdstart), 'wells.')
    if len(wells_def_mdend) > 0:
        print('Perforation MDEND defaulted in', len(wells_def_mdend), 'wells.')

    pfil.close()

    return elist

def read_schedule_tub(file_name, event_date, trajectory_type='Drilled trajectory'):
    """Read Schedule tub file and store data as RMS events
    Args:
        file_name (str): File name for Schedule tub file
        event_date (datetime): Event date for output events
        trajectory_type (str): RMS trajectory definition
    Returns:
        List of roxar events
    Note:
        The Schedule tub file defines casing/tubing data for wells.
        The tub file does not contain time data for the data,
        so an input event date is used for all output.
    """

    try:
        pfil = open(file_name, 'r')
    except OSError as e:
        errmes = 'Error opening file ' + file_name + '\n' + str(e)
        raise OSError(errmes)

    elist = []
    line_no = 0
    is_casing = False

    while True:
        try:
            line = pfil.readline()
        except IOError:
            errmes = 'Error reading Schedule tub file, line ' + str(line_no+1)
            raise IOError(errmes)

        if not line:
            break
        line_no += 1

        temp = line.strip()
        terms = temp.split()
        if temp == '':
            pass    # Skip blank lines
        elif temp.startswith('--'):
            pass    # Skip comments starting with --
        elif terms[0] == 'CASING':
            is_casing = True
            line_casing = 0
            well_name = _get_wellname(terms[1])
            wellbore_name = terms[1]
            traj_name = [well_name, wellbore_name, trajectory_type]
            mdstart = 0.
            mdend = 0.
            diam = 0.
            rough = 0.
        elif terms[0] == 'PACKER':
            pass    # Ignore data for now
        elif terms[0] == 'INFLOW':
            pass    # Ignore data for now
        elif terms[0] == 'CHOKE':
            pass    # Ignore data for now
        elif is_casing:
            if len(terms) == 1:
                mdend = float(terms[0])
                eve = roxar.events.Event.create(roxar.EventType.TUBING, event_date, traj_name)
                eve['MDSTART'] = mdstart
                eve['MDEND'] = mdend
                eve['RADIUSI'] = 0.5*diam
                eve['ROUGH'] = rough
                elist.append(eve)
                is_casing = False

            elif len(terms) > 2:
                line_casing += 1
                mdend = float(terms[0])
                diam = float(terms[1])
                rough = float(terms[2])
                if line_casing > 2:
                    eve = roxar.events.Event.create(roxar.EventType.TUBING, event_date, traj_name)
                    eve['MDSTART'] = mdstart
                    eve['MDEND'] = mdend
                    eve['RADIUSI'] = 0.5*diam
                    eve['ROUGH'] = rough
                    elist.append(eve)
                mdstart = mdend
        else:
            print('Unknown keyword found in', line_no, ':', terms[0])
            print('Reading of tub file aborted')
            break

    pfil.close()

    return elist

def read_schedule_cnt(file_name):
    """Read Schedule cnt file with well file definitions
    Args:
        file_name (str): File name for Schedule cnt file
    Returns:
        Dictionary of well files
    """

    try:
        infil = open(file_name, 'r')
    except OSError as e:
        errmes = 'Error opening file ' + file_name + '\n' + str(e)
        raise OSError(errmes)

    line_no = 0
    file_list = dict()

    while True:
        try:
            line = infil.readline()
        except IOError:
            errmes = 'Error reading Shedule cnt file, line ' + str(line_no + 1)
            raise IOError(errmes)

        if not line:
            break
        line_no = line_no + 1

        temp = line.strip()

        if temp == '':
            pass    # Skip blank lines
        elif temp.startswith('--'):
            pass    # Skip comments starting with --
        else:
            terms = temp.split()
            no_terms = len(terms)
            if no_terms > 3:
                if terms[0] == 'FILE' and terms[2] == 'WELLNAME':
                    file_list[terms[3]] = terms[1]

    infil.close()
    return file_list
