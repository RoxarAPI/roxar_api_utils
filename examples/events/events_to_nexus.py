"""Write events in Nexus format
"""
import sys
import os
from datetime import datetime

import roxar.events

import roxar_api_utils.events
import roxar_api_utils.ioutil

# ----------------------------------------------------------------
# Script parameters

# List of input event set in Events folder
input_esets = ['Events_Set2']

# List of input flow model event set, use None if not defined
grid_model = 'FlowModel'
input_fsets = ['FlowModel_Event_Set2']

# Output files
surface_file = r'C:\Users\torb\MyData\temp\surface.inc'
runcontrol_file = r'C:\Users\torb\MyData\temp\runcontrol.inc'

# ----------------------------------------------------------------
# Start script

def _date_to_string(d):
    """Make string of date in Nexus format
    Args:
        d (datetime): Date object
    Returns:
        String with date
    """

    id = d.day
    im = d.month
    iy = d.year

    if im < 10:
        st = '0' + str(im)
    else:
        st = str(im)

    st = st + r'/'

    if id < 10:
        st = st + '0' + str(id)
    else:
        st = st + str(id)

    st = st + r'/' + str(iy)

    return st

def timedelta_to_days(dt):

    return float(dt.total_seconds())/86400.

def _write_time(fp, d, d0):
    """Write Nexus TIME keyword
    """

    st = _date_to_string(d)

    if d == d0:
        print('\n!TIME', st, file=fp)
    else:
        print('\nTIME', st, file=fp)

    return None

def _write_section(fp, title):
    """Write section titles
    """

    print(file=fp)
    print('!', 50*'-', file=fp)
    print('!', title, file=fp)
    print('!', 50*'-', file=fp)

    return None

def _write_dt(frunc, evlist):
    """Write keyword DT
    """

    qout = False
    dtauto = None
    dtmin = None
    dtmax = None
    maxinc = None
    cutfac = None
    maxnewt = None

    for ev in evlist:
        if ev.type == roxar.EventType.TIMESTEP:
            qout = True
            dtauto = ev['NEXT']
            dtmin = ev['MIN']
            dtmax = ev['MAX']
            maxinc = ev['FACTORMAX']
            cutfac = ev['FACTORFAIL']

        elif ev.type == roxar.EventType.NUMNONLINEAR:
            qout = True
            maxnewt = ev['ITERMAX']

    if qout:
        print('\nDT',end='', file=frunc)
        if dtauto is not None: print(
            ' AUTO',
            '{0:6.3f}'.format(timedelta_to_days(dtauto)),
            end='', file=frunc)
        if dtmin is not None: print(
            ' MIN',
            '{0:6.3f}'.format(timedelta_to_days(dtmin)),
            end='', file=frunc)
        if dtmax is not None: print(
            ' MAX',
            '{0:6.3f}'.format(timedelta_to_days(dtmax)),
            end='', file=frunc)
        if maxinc is not None: print(
            ' MAXINCREASE',
            '{0:5.2f}'.format(maxinc),
            end='', file=frunc)
        if cutfac is not None: print(
            ' CUTFACTOR',
            '{0:5.2f}'.format(cutfac),
            end='', file=frunc)
        if maxnewt is not None: print(
            ' MAXNEWTONS',
            '{0:4d}'.format(maxnewt),
            end='', file=frunc)
        print(file=frunc)

    return None

def _write_output(frunc, evlist):
    """Write keyword OUTPUT
    """

    qrest = False
    qfip_field = False
    qfip_reg = False

    for ev in evlist:
        if ev.type == roxar.EventType.IORESTART:
            qrest = True
            fm = ev['FREQMODE']
            restart_freq = ev['FREQUENCY']
            if fm == 'Timestep':
                restart_fm = 'DT'
            elif fm == 'Month':
                restart_fm = 'MONTHLY'
            elif fm == 'Report':
                restart_fm = 'TIMES'
            elif fm == 'Year':
                restart_fm = 'YEARLY'
            else:
                qrest = False

        elif ev.type == roxar.EventType.IOFIP:
            qfip_field = ev['FIELD']
            qfip_reg = ev['REGION']

    if qrest or qfip_field or qfip_reg:
        print('\nOUTPUT', file=frunc)
        if qrest:
            if restart_freq is not None:
                print(' RESTART  ', restart_fm, '  FREQ  ', restart_freq, file=frunc)
            else:
                print(' RESTART  ', restart_fm, file=frunc)

        if qfip_field: print(' FIELD  TIMES', file=frunc)
        if qfip_reg: print(' REGIONS  TIMES', file=frunc)
        print('ENDOUTPUT', file=frunc)

def _write_drsdt(frunc, evlist):
    """Write keyword DRSDT
    """

    for ev in evlist:
        if ev.type == roxar.EventType.NUMDELMAX:
            if ev['DELRS'] is not None:
                print('\nDRSDT  LIMIT ', ev['DELRS'], file=frunc)

    return None

def _write_runcontrol(frunc, datelist, evbydate):

    roxar_api_utils.ioutil.write_file_header(frunc, comment_start='!', name=None)


    date0 = datelist[0]
    startdat = _date_to_string(date0)
    print('START', startdat, file=frunc)

    _write_section(frunc, 'Recurrent run controls')

    for datenum,d in enumerate(datelist):
        evlist = evbydate[d]
        _write_time(frunc,d,date0)
        _write_dt(frunc,evlist)
        _write_output(frunc,evlist)
        _write_drsdt(frunc,evlist)

    print(file=frunc)
    print('STOP', file=frunc)

    return None

def _init_well_info(well_info, wname):
    """Initialize well info dictionary for well
    """

    if wname not in well_info.keys():
        winfo = dict()
        winfo['welltype'] = 'Producer'
        winfo['phase'] = 'Oil'

        well_info[wname] = winfo

    return well_info

def _write_wells(fsurf, evlist, ownerdict, well_info):
    """Write keyword WELLS
    """

    outwells = dict()
    qout = False
    for ev in evlist:

        etyp = ev.type
        wname = ev.owner[0]
        if etyp == roxar.EventType.GMEMBER: wname = ev['MEMBER']

        if wname in ownerdict['Well']:

            well_info = _init_well_info(well_info, wname)
            winfo = well_info[wname]

            if wname not in outwells.keys():
                outwells[wname] = None
                outdat = dict()
                outdat['STREAM'] = None
                outdat['BHDEPTH'] = 'NA'
                outdat['CROSSFLOW'] = '#'
                outdat['STATION'] = 'NA'         # Station NA not accepted
            else:
                outdat = outwells[wname]

            if etyp == roxar.EventType.WTYPE:
                winfo['welltype'] = ev['TYPE']
                winfo['phase'] = ev['PHASE']
                well_info[wname] = winfo
                qout = True
                if ev['TYPE'] == 'Producer':
                    outdat['STREAM'] = 'PRODUCER'
                elif ev['TYPE'] == 'Injector':
                    if ev['PHASE'] == 'Gas':
                        outdat['STREAM'] = 'GAS     '
                    elif ev['PHASE'] == 'Water':
                        outdat['STREAM'] = 'WATER   '

            elif etyp == roxar.EventType.WDREF:
                qout = True
                outdat['BHDEPTH'] = ev['DEPTH']

            elif etyp == roxar.EventType.WCROSSFL:
                qout = True
                if ev['ON']:
                    outdat['CROSSFLOW'] = 'ON'
                else:
                    outdat['CROSSFLOW'] = 'OFF'

            elif etyp == roxar.EventType.GMEMBER:
                outdat['STATION'] = ev.owner[0]

            outwells[wname] = outdat

    if qout:
        print('\nWELLS', file=fsurf)

        qstation = True
        for w in outwells.keys():
            outdat = outwells[w]
            if outdat['STATION'] == 'NA':
                qstation = False

        if qstation:
            print(' NAME       STREAM      BHDEPTH   CROSSFLOW     STATION', file=fsurf)
        else:
            print(' NAME       STREAM      BHDEPTH   CROSSFLOW', file=fsurf)

        for w in outwells.keys():
            outdat = outwells[w]
            if outdat['STREAM'] is not None:
                print(' {:10}'.format(w), end='', file=fsurf)
                print('{:10}'.format(outdat['STREAM']), end='', file=fsurf)
                print(' ', '{0:8.2f}'.format(outdat['BHDEPTH']), end='', file=fsurf)
                print('  ', '{:4}'.format(outdat['CROSSFLOW']), end='', file=fsurf)
                if qstation:
                    print('         ', '{:10}'.format(outdat['STATION']), end='', file=fsurf)
                print(file=fsurf)

        print('ENDWELLS', file=fsurf)

    return well_info

def _write_hist_rates(fsurf, evlist):
    """Write historical rates to keyword QMULT
    Returns:
        List of historical wells
    """

    qkey = True
    qout = False
    space = '  '
    hist_wells = []

    for ev in evlist:

        etyp = ev.type
        wname = ev.owner[0]
        qout = False
        outst = ' ' + wname.ljust(10)

        if etyp == roxar.EventType.WHISTRATE:
            qout = True
            hist_wells.append(ev.owner)
            if ev['SRATEO'] is not None:
                qout = True
                outst = outst + space + '{0:10.2f}'.format(ev['SRATEO'])
            else:
                outst = outst + space + 'NA        '
            if ev['SRATEG'] is not None:
                qout = True
                outst = outst + space + '{0:10.2f}'.format(ev['SRATEG'])
            else:
                outst = outst + space + 'NA        '
            if ev['SRATEW'] is not None:
                qout = True
                outst = outst + space + '{0:10.2f}'.format(ev['SRATEW'])
            else:
                outst = outst + space + 'NA'

        if qout:
            if qkey:
                print('\nQMULT', file=fsurf)
                print(' WELL            OIL         GAS         WATER', file=fsurf)
                qkey = False
            print(outst, file=fsurf)

    if not qkey:
        print('ENDQMULT', file=fsurf)

    return hist_wells

def _write_hist_control(fsurf, evlist, well_info, hist_wells):
    """Write rate control for historical wells to CONSTRAINTS
    """

    if len(hist_wells) == 0: return None

    qkey = True
    qout = False
    space = '  '

    for ev in evlist:

        etyp = ev.type
        wname = ev.owner
        qout = False
        outst = ' ' + wname.ljust(10)

        if ev.type == roxar.EventType.WCONTROL:
            if wname in hist_wells:
                qout = True
                if ev['MODE'] == 'Surface rate':
                    if ev['PHASE'] == 'From well type':
                        winfo = well_info[wname]
                        phase = winfo['phase']
                    else:
                        phase = ev['PHASE']
                    if phase == 'Oil':
                        outst = outst + space + 'QOSMAX  MULT'
                    elif phase == 'Gas':
                        outst = outst + space + 'QGSMAX  MULT'
                    elif phase == 'Water':
                        outst = outst + space + 'QWSMAX  MULT'
                    elif phase == 'Liquid':
                        outst = outst + space + 'QLSMAX  MULT'
                    else:
                        qout = False
                elif ev['MODE'] == 'Reservoir rate':
                    if ev['PHASE'] == 'Total':
                        outst = outst + space + 'QALLRMAX  MULT'
                    else:
                        qout = False

        if qout:
            if qkey:
                print('\nCONSTRAINTS', file=fsurf)
                qkey = False
            print(outst, file=fsurf)

    if not qkey:
        print('ENDCONSTRAINTS', file=fsurf)

    return None

def _write_constraints(fsurf, evlist, workover):
    """Write keyword CONSTRAINTS
    """

    qkey = True
    space = '  '

    for ev in evlist:

        etyp = ev.type
        wname = ev.owner[0]
        qout = False
        outst = ' ' + wname.ljust(10)

        if etyp == roxar.EventType.WLIMRATE:
            if ev['MAX']:
                if ev['SRATEO'] is not None:
                    qout = True
                    outst = outst + space + 'QOSMAX' + space + '{0:10.2f}'.format(ev['SRATEO'])
                if ev['SRATEG'] is not None:
                    qout = True
                    outst = outst + space + 'QGSMAX' + space + '{0:10.2f}'.format(ev['SRATEG'])
                if ev['SRATEW'] is not None:
                    qout = True
                    outst = outst + space + 'QWSMAX' + space + '{0:10.2f}'.format(ev['SRATEW'])
                if ev['SRATEL'] is not None:
                    qout = True
                    outst = outst + space + 'QLIQSMAX' + space + '{0:10.2f}'.format(ev['SRATEL'])
                if ev['RRATE'] is not None:
                    qout = True
                    outst = outst + space + 'QALLMAX' + space + '{0:10.2f}'.format(ev['RRATE'])
            else:
                if ev['SRATEO'] is not None:
                    qout = True
                    outst = outst + space + 'QOSMIN' + space + '{0:10.2f}'.format(ev['SRATEO'])
                if ev['SRATEG'] is not None:
                    qout = True
                    outst = outst + space + 'QGSMIN' + space + '{0:10.2f}'.format(ev['SRATEG'])
                if ev['SRATEW'] is not None:
                    qout = True
                    outst = outst + space + 'QWSMIN' + space + '{0:10.2f}'.format(ev['SRATEW'])
                if ev['SRATEL'] is not None:
                    qout = True
                    outst = outst + space + 'QLIQSMIN' + space + '{0:10.2f}'.format(ev['SRATEL'])
                if ev['RRATE'] is not None:
                    qout = True
                    outst = outst + space + 'QALLMIN' + space + '{0:10.2f}'.format(ev['RRATE'])

        if etyp == roxar.EventType.WLIMPRES:
            if ev['BHP'] is not None:
                qout = True
                outst = outst + space + 'BHP' + space + '{0:10.2f}'.format(ev['BHP'])
            if ev['THP'] is not None:
                qout = True
                outst = outst + space + 'THP' + space + '{0:10.2f}'.format(ev['THP'])

        if etyp == roxar.EventType.WLIMRATIO:
            if ev['WCT'] is not None:
                qout = True
                if ev['ACTION'] == 'Shut well':
                    key = 'WCTMAX'
                elif ev['ACTION'] == 'Workover':
                    if wname in workover.keys():
                        if workover[wname] == 'Worst':
                            key = 'WCTPLUG'
                        elif workover[wname] == 'Worst+':
                            key = 'WCTPLUGPLUS'
                        else:
                            qout = False
                if qout:
                    outst = outst + space + key + space + '{0:5.3f}'.format(ev['WCT'])

            elif ev['WOR'] is not None:
                qout = True
                if ev['ACTION'] == 'Shut well':
                    key = 'WORMAX'
                elif ev['ACTION'] == 'Workover':
                    if wname in workover.keys():
                        if workover[wname] == 'Worst':
                            key = 'WORPLUG'
                        elif workover[wname] == 'Worst+':
                            key = 'WORPLUGPLUS'
                        else:
                            qout = False
                else:
                    qout = False
                if qout:
                    outst = outst + space + key + space + '{0:8.2f}'.format(ev['WOR'])

            if ev['GOR'] is not None:
                qout = True
                if ev['ACTION'] == 'Target':
                    key = 'GORLIMIT'
                elif ev['ACTION'] == 'Shut well':
                    key = 'GORMAX'
                elif ev['ACTION'] == 'Workover':
                    if wname in workover.keys():
                        if workover[wname] == 'Worst':
                            key = 'GORPLUG'
                        elif workover[wname] == 'Worst+':
                            key = 'GORPLUGPLUS'
                        else:
                            qout = False
                    else:
                        qout = False
                if qout:
                    outst = outst + space + key + space + '{0:5.3f}'.format(ev['GOR'])

            if ev['LGR'] is not None:
                qout = True
                if ev['ACTION'] == 'Shut well':
                    key = 'LGRMAX'
                elif ev['ACTION'] == 'Workover':
                    if wname in workover.keys():
                        if workover[wname] == 'Worst':
                            key = 'LGRPLUG'
                        elif workover[wname] == 'Worst+':
                            key = 'LGRPLUGPLUS'
                    else:
                        qout = False
                if qout:
                    outst = outst + space + key + space + '{0:5.3f}'.format(ev['LGR'])

        if qout:
            if qkey:
                print('\nCONSTRAINTS', file=fsurf)
                qkey = False
            print(outst, file=fsurf)

    if not qkey:
        print('ENDCONSTRAINTS', file=fsurf)

    return None

def _write_station(fsurf, evlist, ownerdict, group_level, group_no):
    """Write keyword STATION
    """

    parent = dict()
    for ev in evlist:

        etyp = ev.type

        if etyp == roxar.EventType.GMEMBER:
            wg = ev['MEMBER']
            eo = ev.owner
            if wg in ownerdict['Well group']:
                parent[wg] = eo
                if eo not in parent.keys():
                    parent[eo] = 'NONE'

    if len(parent.keys()) > 0:

        maxlevel = 0
        for g in parent.keys():
            maxlevel = max(maxlevel, group_level[g])

        print('\nSTATION', file=fsurf)
        print(' NAME       NUMBER    LEVEL   PARENT ', file=fsurf)
        for lev in range(maxlevel,0,-1):
            for g in parent.keys():
                if group_level[g] == lev:
                    print(' {:10}'.format(g), end='', file=fsurf)
                    print('   ', '{:4d}'.format(group_no[g]), end='', file=fsurf)
                    print('    ', '{:4d}'.format(group_level[g]), end='', file=fsurf)
                    print('  ', '{:10}'.format(parent[g]), end='', file=fsurf)
                    print(file=fsurf)
        print('ENDSTATION', file=fsurf)

    return None

def _set_workover(workover, evlist):
    """Set workover data for each well/group
    """

    for ev in evlist:
        if ev.type == roxar.EventType.WWORKOVER:
            workover[ev.owner] = ev['TYPE']

    return workover

def _write_surface(fsurf, datelist, evbydate, ownerdict, group_level, group_no):

    well_info = dict()

    roxar_api_utils.ioutil.write_file_header(fsurf, comment_start='!', name=None)

    _write_section(fsurf, 'Fluid model for network')
    print('\nBLACKOIL', file=fsurf)

    _write_section(fsurf, 'General options')

    print('\n! Constraints will be added', file=fsurf)
    print('DONTCLEAR', file=fsurf)

    print('\n! Wells will be controlled at the wellhead', file=fsurf)
    print('WELLCONTROL WELLHEAD', file=fsurf)

    _write_section(fsurf, 'Well data')

    workover = dict()

    d0 = datelist[0]
    for d in datelist:
        evlist = evbydate[d]
#
        workover = _set_workover(workover, evlist)
        _write_time(fsurf, d, d0)
        _write_station(fsurf, evlist, ownerdict, group_level, group_no)
        well_info = _write_wells(fsurf, evlist, ownerdict, well_info)
        hist_wells = _write_hist_rates(fsurf, evlist)
        _write_hist_control(fsurf, evlist, well_info, hist_wells)
        _write_constraints(fsurf, evlist, workover)

    return None

def _get_group_level(elist, group_set):
    """Define group hierarchy - levels
    Returns:
        Dictionary of group level for 'group name'
    """

    no_groups = len(group_set)
    if no_groups == 0:
        return None

    numbered = 0

    parent = dict()
    level = dict()
    for g in group_set:
        parent[g] = None
        level[g] = None

    for ev in elist:
        if ev.type == roxar.EventType.GMEMBER:
            m = ev['MEMBER']
            if m in group_set:
                parent[m] = ev.owner[0]
            else:
                level[ev.owner[0]] = 1
                numbered += 1

    for l in range(0, no_groups):
        for g in group_set:
            if level[g] is not None:
                gp = parent[g]
                level[gp] = level[g] + 1
                numbered = numbered + 1
        if numbered == no_groups:
            break

    return level

def _write_nexus(project, input_esets=None, grid_model=None, input_fsets=None, surface_file=None, runcontrol_file=None):
    """Write Nexus keywords
    Args:
        project: RMS project
    Returns:
        None
    """

    if surface_file is None:
        fsurf = sys.stdout
    else:
        fsurf = open(surface_file, 'w')

    if runcontrol_file is None:
        frunc = sys.stdout
    else:
        frunc = open(runcontrol_file, 'w')

# Merge event sets
    elist = roxar_api_utils.events.merge_esets(project, input_esets, grid_model, input_fsets)
# Sort event list by date and type
    elist = roxar_api_utils.events.elist_sort(elist, type='DT')

# Group by dates

    datelist = []
    evbydate = dict()
    now0 = datetime(1900, 1, 1)
    now = now0
    for ev in elist:
        if ev.date > now:
            if now > now0:
                evbydate[now] = evnow
            now = ev.date
            datelist.append(now)
            evnow = []
        evnow.append(ev)
    evbydate[now] = evnow

# Get owners

    ownerdict = roxar_api_utils.events.get_elist_owners(elist)

# Set group hierarchy:

    group_level = _get_group_level(elist, ownerdict['Well group'])
    group_no = dict()
    for i,g in enumerate(ownerdict['Well group']):
        group_no[g] = i + 1

# Run control file
    _write_runcontrol(frunc, datelist, evbydate)

# Surface files:
    _write_surface(fsurf, datelist, evbydate, ownerdict, group_level, group_no)

    return None

# Main

qclist = _write_nexus(project, input_esets, grid_model, input_fsets, surface_file, runcontrol_file)

print('Output to file', surface_file)
