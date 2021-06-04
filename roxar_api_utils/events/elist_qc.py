import sys
from datetime import timedelta

import roxar
import roxar.events

from .get_elist_owners import get_elist_owners
from .get_events import get_events
from .verify_event_attributes import verify_event_attributes
from .elist_qc_owners import elist_qc_owners

def check_events(project, elist, silent=False, filep=None):
    """Perform basic quality control of a list of events
    Args:
        project: Roxar API project
        elist: List of roxar events
        silent: True if no printed messages should be produced
        filep:  Optional opened text file for output. Use standard output if None
    """

    if filep is None:
        filep = sys.stdout

# List of incorrect events
    errlist = []

# Sort event list by date and owner
#    elist = elist_sort(elist, type='DO')

# Get owners, dates, event types
    wellset = set()  # Wells defined as event owners
    groupset = set()  # Groups defined as event owners
    trajset = set()  # Trajectories defined as event owners
    wtrajset = set()  # Wells defined with trajectory owners
    typeset = set()
    dateset = set()
    for ev in elist:
        evdet = roxar.events.Event.details(ev.type)
        typeset.add(ev.type)
        dateset.add(ev.date)
        if evdet['owner_type'] == 'Well':
            wellset.add(ev.owner[0])
        elif evdet['owner_type'] == 'Well group':
            groupset.add(ev.owner[0])
        elif evdet['owner_type'] == 'Trajectory':
            trajset.add(tuple(ev.owner))
            well, wellbore, traj = ev.owner
            wtrajset.add(well)

# Get date info
    datelist = sorted(list(dateset))
    datemin = datelist[0]
    datemax = datelist[-1]

    dtmin = timedelta(1e6)
    dtmax = timedelta(0)
    for i in range(1, len(datelist)):
        dt = datelist[i] - datelist[i-1]
        dtmin = min(dt, dtmin)
        dtmax = max(dt, dtmax)

# Get wells and trajectories in Wells container
    rmswells, rmstrajs = _get_rms_wells(project)

# Initial statistics
    if not silent:
        _print_line(filep, 'Number of events total', wint=len(elist))
        _print_line(filep, 'Number of event types', wint=len(typeset))
        _print_line(filep, 'Start date', wdate=datemin)
        _print_line(filep, 'End date', wdate=datemax)
        _print_line(filep, 'Minimum time delta between dates', wdt=dtmin)
        _print_line(filep, 'Maximum time delta between dates', wdt=dtmax)
        _print_line(filep, 'Number of different dates', wint=len(datelist))
        _print_line(filep, 'Number of event wells', wint=len(wellset))
        _print_line(filep, 'Number of wells in Wells folder', wint=len(rmswells))
        _print_line(filep, 'Number of event trajectories', wint=len(trajset))
        _print_line(filep, 'Number of trajectories in Wells folder', wint=len(rmstrajs))
        _print_line(filep, 'Number of event well groups', wint=len(groupset))

# Split event set into dictionary holding individual events
    edict = _event_split(elist)

# Check for branched wells:
    _check_branched_well(wtrajset, trajset, silent, filep)

# Check for multi-segment wells:
    multiseg_traj_set = _check_multiseg_well(edict, silent, filep)

# Check event owners:
    print(file=filep)
    es = elist_qc_owners(elist)
    errlist.extend(es)
    if not silent:
        _print_line(filep, 'Number of events with non-standard owner', wint=len(es))

    _check_missing_well(wellset, trajset, wtrajset, rmswells, rmstrajs, silent, filep)

# Check for missing events:
    _check_missing_events(
        edict, wellset, trajset, wtrajset, groupset, multiseg_traj_set, silent, filep)

# Check attributes choices:
    es = verify_event_attributes(elist)
    errlist.extend(es)
    if not silent:
        _print_line(filep, 'Number of events with non-standard attributes', wint=len(es))

# Check for missing attributes definitions:
    es = _check_missing_attributes(elist, edict, silent, filep)
    errlist.extend(es)

# Check specific events:
    es = _check_perfs(edict, wellset, trajset, wtrajset, silent, filep)
    errlist.extend(es)

# Check specific events:
    es = _check_cperfs(edict, wellset, trajset, wtrajset, silent, filep)
#    errlist.extend(es)    # Cannot add grid events to regular event set

    es = _check_wsegs(edict, wellset, trajset, wtrajset, silent, filep)
#    errlist.extend(es)

    return errlist

def _get_rms_wells(project):
    """Get wells and trajectories from RMS wells folder
    """

    wset = set()
    tset = set()
    for well in project.wells:
        wset.add(well.name)
        for wb in well.all_wellbores:
            for tr in wb.trajectories:
                tname = (well.name, wb.name, tr.name)
                tset.add(tname)

    return (wset, tset)

def _check_missing_well(wellset, trajset, wtrajset, rmswells, rmstrajs, silent, filep):
    """Check if wells and trajectories exist in the project
    """

    err1 = set()
    for w in wellset:
        if w not in rmswells:
            err1.add(w)

    err2 = set()
    for traj in trajset:
        if traj not in rmstrajs:
            err2.add(traj)

    if not silent:
        _print_line(filep, 'Wells not defined in project', wset=err1, refset=wellset)
        _print_line(filep, 'Trajectories not defined in project', wset=err2, refset=trajset)

    return None

def _check_branched_well(wtrajset, trajset, silent, filep):
    """Check if event owner is branched well
    """

    branched = set()
    for tr in trajset:
        well, wellbore, traj = tr
        if well != wellbore:
            branched.add(well)

    if len(branched) > 0:
        if not silent:
            _print_line(filep, 'Branched wells', wset=branched, refset=wtrajset)

    return None

def _check_multiseg_well(edict, silent, filep):
    """Check if well has multiseg definition
    """

    multiseg_traj_set = None
    if len(edict[roxar.EventType.WSEGMOD]) > 0:
        multiseg_well_set = set()
        multiseg_traj_set = set()
        for e in edict[roxar.EventType.WSEGMOD]:
            well, wellbore, traj = e.owner
            multiseg_well_set.add(well)
            multiseg_traj_set.add(tuple(e.owner))

        if not silent:
            _print_line(filep, 'Number of multi-segment wells', wint=len(multiseg_well_set))

    return multiseg_traj_set

def _check_missing_events(
        edict, wellset, trajset, wtrajset, groupset, multiseg_traj_set, silent, filep):
    """Check for missing events
    """

    clist = [roxar.EventType.WTYPE,
             roxar.EventType.WCONTROL,
             roxar.EventType.WLIMRATE,
             roxar.EventType.WLIMPRES,
             roxar.EventType.WHISTRATE,
             roxar.EventType.WHISTPRES]

    for c in clist:
        wcontr = edict[c]
        if len(wcontr) > 0:
            odict = get_elist_owners(wcontr)
            wset2 = odict['Well']
            diff = wellset - wset2
        else:
            diff = wellset

        if not silent:
            line = 'Wells not defined with keyword ' + str(c)
            _print_line(filep, line, wset=diff, refset=wellset)


    gmem = edict[roxar.EventType.GMEMBER]
    if len(gmem) > 0:
        wset2 = set()
        for gm in gmem:
            wset2.add(gm['MEMBER'])
        diff = wellset - wset2
    else:
        diff = wellset

    if not silent:
        _print_line(
            filep,
            'Wells not defined with keyword GMEMBER',
            wset=diff,
            refset=wellset)

    if len(edict[roxar.EventType.GCONTROL]) > 0:
        odict = get_elist_owners(edict[roxar.EventType.GCONTROL])
        gset2 = odict['Well group']
        diff = groupset - gset2
    else:
        diff = groupset

    if not silent:
        _print_line(
            filep,
            'Groups not defined with GCONTROL',
            wset=diff,
            refset=groupset)

    wset3 = set()
    clist = [roxar.EventType.WLIMRATE, roxar.EventType.WLIMPRES, roxar.EventType.WLIMRATIO]
    for c in clist:
        evset = edict[c]
        if len(evset) > 0:
            for ev in evset:
                if   ev['ACTION'] == 'Boost':
                    evtype = roxar.EventType.WBOOST
                elif ev['ACTION'] == 'Cutback':
                    evtype = roxar.EventType.WCUTBACK
                elif ev['ACTION'] == 'Workover':
                    evtype = roxar.EventType.WWORKOVER
                else:
                    evtype = None

                if evtype is not None and evtype not in edict.keys():
                    wset3.add(ev.owner[0])

    if not silent:
        _print_line(filep, 'Wells with missing action event', wset=wset3, refset=wellset)

    wset5 = set()
    if len(wtrajset) > len(wellset):
        wset5 = wtrajset - wellset
    if not silent:
        _print_line(filep, 'Trajectories without well events', wset=wset5, refset=wtrajset)

    wset4 = set()
    clist = [roxar.EventType.GLIMRATE, roxar.EventType.GLIMPRES, roxar.EventType.GLIMRATIO]
    for c in clist:
        evset = edict[c]
        if len(evset) > 0:
            for ev in evset:
                if ev['ACTION'] == 'Boost':
                    evtype = roxar.EventType.GBOOST
                elif ev['ACTION'] == 'Cutback':
                    evtype = roxar.EventType.GCUTBACK
                elif ev['ACTION'] == 'Workover':
                    evtype = roxar.EventType.GWORKOVER
                else:
                    evtype = None

                if evtype is not None and evtype not in edict.keys():
                    wset4.add(ev.owner[0])

    if not silent:
        _print_line(filep, 'Groups with missing action event', wset=wset4, refset=groupset)


    if multiseg_traj_set is not None:
        is_ok = dict()
        for tr in multiseg_traj_set:
            is_ok[tr] = False
        for ev in edict[roxar.EventType.TUBING]:
            is_ok[tuple(ev.owner)] = True

        wset6 = set()
        for ow, val in is_ok.items():
            if not val:
                wset6.add(ow)

        if not silent:
            _print_line(filep, 'Trajectories with missing tubing events', wset=wset6, refset=wtrajset)

    return None

def _check_missing_attributes(elist, edict, silent, filep):
    """Check for missing attributes
    """
    errlist = []
    checks = []
    no = dict()

# Check general missing

    key = roxar.EventType.WTYPE
    atts = ['TYPE', 'PHASE']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.WCONTROL
    atts = ['MODE', 'PHASE']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.PERF
    atts = ['MDSTART', 'MDEND', 'RADIUS']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.SQUEEZE
    atts = ['MDSTART', 'MDEND']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.WLIMRATE
    atts = ['TYPEW', 'ACTION']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.WLIMPRES
    atts = ['TYPEW', 'ACTION']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.WLIMRATIO
    atts = ['ACTION']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.WGUIDERATE
    atts = ['RATE']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.WEFFICIENCY
    atts = ['FACTOR']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GCONTROL
    atts = ['TYPE', 'MODE', 'RATETYPE']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GLIMRATE
    atts = ['TYPE', 'ACTION']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GLIMRATIO
    atts = ['ACTION']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GGUIDERATE
    atts = ['TYPE', 'PHASE', 'CONTROL']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GBALRATE
    atts = ['TYPE', 'GROUP']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GBALPRES
    atts = ['TYPE', 'REGIONID', 'PRES']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GEFFICIENCY
    atts = ['FACTOR']
    checks.append((key, atts))
    no[key] = 0

    key = roxar.EventType.GSUPPLYMOD
    atts = ['CAUSE', 'PHASE']
    checks.append((key, atts))
    no[key] = 0

    for ev in elist:
        for c in checks:
            key, atts = c
            if ev.type == key:
                flaw = False

                for a in atts:
                    if ev[a] is None:
                        flaw = True
                if flaw:
                    no[key] = no[key] + 1
                    errlist.append(ev)

    if len(edict[roxar.EventType.GLIMRATE]) > 0:
        for ev in edict[roxar.EventType.GLIMRATE]:
            if ev['ACTION'] is not None and ev['ACTION'] != 'Target' and ev['ACTION'] != 'End run':
                if ev['WELLS'] is None:
                    no[roxar.EventType.GLIMRATE] = no[roxar.EventType.GLIMRATE] + 1
                    errlist.append(ev)

    if len(edict[roxar.EventType.GCONTROL]) > 0:
        for ev in edict[roxar.EventType.GCONTROL]:
            if ev['TYPE'] == 'Injection' and ev['RATETYPE'] == 'Surface rate':
                if ev['PHASE'] is None:
                    no[roxar.EventType.GCONTROL] = no[roxar.EventType.GCONTROL] + 1
                    errlist.append(ev)

    if not silent:
        for c in checks:
            key = c[0]
            line = 'Number of incomplete ' + str(key) + ' events'
            if not silent:
                _print_line(filep, line, wint=no[key])

    return errlist

def _check_perfs(edict, wellset, trajset, wtrajset, silent, filep):
    """Check PERF/SQUEEZE events
    """

    errlist = []

    errset1 = wellset - wtrajset
    if not silent:
        print(file=filep)
        _print_line(filep, 'Wells not defined with PERF events', wset=errset1, refset=wellset)

    if len(edict[roxar.EventType.PERF]) > 0:
        errset1 = set()
        errset2 = set()
        errset3 = set()

        for t in trajset:
            eperf = get_events(edict[roxar.EventType.PERF], eowner=list(t))
            if eperf is not None:
                for ev in eperf:
                    if ev['MDSTART'] is None or ev['MDEND'] is None:
                        errlist.append(ev)
                        w, wb, traj = t
                        errset1.add(w)
                    elif ev['MDSTART'] >= ev['MDEND']:
                        errlist.append(ev)
                        w, wb, traj = t
                        errset1.add(w)
                    else:
# Check for overlapping intervals
                        for ev2 in eperf:
                            if ev2['MDSTART'] < ev2['MDEND']:
                                del1 = (ev['MDSTART'] - ev2['MDSTART'])*(ev2['MDEND']-ev['MDSTART'])
                                del2 = (ev['MDEND']   - ev2['MDSTART'])*(ev2['MDEND']-ev['MDEND'])
                                if del1 > 0 or del2 > 0:
                                    errlist.append(ev)
                                    w, wb, traj = t
                                    errset2.add(w)

                    if ev['RADIUS'] is None:
                        errlist.append(ev)
                        w, wb, traj = t
                        errset3.add(w)

        if not silent:
            _print_line(
                filep,
                'PERF events with MDSTART >= MDEND',
                wset=errset1,
                refset=wtrajset)
            _print_line(
                filep,
                'PERF events with MD overlapping',
                wset=errset2,
                refset=wtrajset)
            _print_line(
                filep,
                'PERF events with missing radius',
                wset=errset3,
                refset=wtrajset)

    if len(edict[roxar.EventType.SQUEEZE]) > 0:
        errset1 = set()
        for ev in edict[roxar.EventType.SQUEEZE]:
            if ev['MDSTART'] is None or ev['MDEND'] is None:
                errlist.append(ev)
                w, wb, traj = ev.owner
                errset1.add(w)
            elif ev['MDSTART'] >= ev['MDEND']:
                errlist.append(ev)
                w, wb, traj = ev.owner
                errset1.add(w)

        if not silent:
            _print_line(
                filep,
                'SQUEEZE events with MDSTART >= MDEND',
                wset=errset1,
                refset=wtrajset)

    return errlist


def _check_cperfs(edict, wellset, trajset, wtrajset, silent, filep):
    """Check CPERF events
    """

    errlist = []

    if len(edict[roxar.EventType.CPERF]) > 0:
        errset1 = set()
        errset2 = set()

        for t in trajset:
            eperf = get_events(edict[roxar.EventType.CPERF], eowner=list(t))
            if eperf is not None:
                for ev in eperf:
                    if ev['MDSTART'] is None or ev['MDEND'] is None:
                        errlist.append(ev)
                        w, wb, traj = t
                        errset1.add(w)
                    elif ev['MDSTART'] >= ev['MDEND']:
                        errlist.append(ev)
                        w, wb, traj = t
                        errset1.add(w)
                    else:
# Check for overlapping intervals
                        for ev2 in eperf:
                            if ev2['MDSTART'] < ev2['MDEND']:
                                del1 = (ev['MDSTART'] - ev2['MDSTART'])*(ev2['MDEND']-ev['MDSTART'])
                                del2 = (ev['MDEND']   - ev2['MDSTART'])*(ev2['MDEND']-ev['MDEND'])
                                if del1 > 0 or del2 > 0:
                                    errlist.append(ev)
                                    w, wb, traj = t
                                    errset2.add(w)

        if not silent:
            _print_line(
                filep,
                'CPERF events with MDSTART >= MDEND',
                wset=errset1,
                refset=wtrajset)
            _print_line(
                filep,
                'CPERF events with MD overlapping',
                wset=errset2,
                refset=wtrajset)

    return errlist

def _print_line(
        filep, line, wint=None, wstring=None, wset=None,
        wfloat=None, wdate=None, wdt=None, refset=None):
    """Print line with quality information to output
    """
    length_line = 60

    lk = length_line - len(line)
    print(line, lk*' ', sep='', end='', file=filep)

    if wint is not None:
        if wint == 0:
            print('None', file=filep)
        else:
            print(wint, file=filep)

    elif wfloat is not None:
        print(wfloat, file=filep)

    elif wstring is not None:
        print(wstring, file=filep)

    elif wdate is not None:
        print(wdate.strftime("%d. %b %Y %H:%M:%S"), file=filep)

    elif wdt is not None:
        print(wdt, file=filep)

    elif wset is not None:
        for obj in wset:
            if isinstance(obj, tuple):
                length_names = 1
            else:
                length_names = 5
            break
        if wset == set():
            print('None', file=filep)
        else:
            st = ''
            if refset is not None and len(refset) > 3:
                diff = refset - wset
                if diff == set():
                    st = 'All'
            if st != 'All':
                llist = sorted(list(wset))
                lenlist = len(llist)
                if lenlist < length_names:
                    st = ", ".join(str(l) for l in llist)
                else:
                    st = ", ".join(str(l) for l in llist[0:length_names])
                    rest = lenlist - length_names
                    nochunk = int((rest)/length_names)
                    if nochunk*length_names < rest:
                        nochunk = nochunk + 1
                    for i in range(nochunk):
                        st = st + ','
                        print(st, file=filep)
                        ib = (i+1)*length_names
                        ie = min(ib + length_names, lenlist)
                        st = ", ".join(str(l) for l in llist[ib:ie])
                        print(length_line*' ', end='', file=filep)


            print(st, file=filep)

    return None

def _event_split(elist):
    """Split event list into dictionary of event keywords
    """
    eventdict = dict()
    dictkeys = (roxar.EventType.WLIMRATE,
                roxar.EventType.WLIMPRES,
                roxar.EventType.WLIMRATIO,
                roxar.EventType.WHISTRATE,
                roxar.EventType.WHISTPRES,
                roxar.EventType.WCONTROL,
                roxar.EventType.WTYPE,
                roxar.EventType.WSEGMOD,
                roxar.EventType.WSEGSEG,
                roxar.EventType.GCONTROL,
                roxar.EventType.GMEMBER,
                roxar.EventType.GLIMRATE,
                roxar.EventType.GLIMPRES,
                roxar.EventType.GLIMRATIO,
                roxar.EventType.PERF,
                roxar.EventType.CPERF,
                roxar.EventType.SQUEEZE,
                roxar.EventType.TUBING)

    for d in dictkeys:
        eventdict[d] = []

    for ev in elist:
        if ev.type in dictkeys:
            eventdict[ev.type].append(ev)

    return eventdict

def _check_wsegs(edict, wellset, trajset, wtrajset, silent, filep):
    """Check events involved in multi-seg modelling
    """

    errlist = []

# Check for missing TUBING
    errset = set()
    for e in edict[roxar.EventType.WSEGMOD]:
        eowner = e.owner
        well, wellbore, traj = eowner
        mtmin = 100000.
        mtmax = 0.
        is_ok = False
        for et in edict[roxar.EventType.TUBING]:
            if et.owner == eowner:
                is_ok = True
                mtmin = min( et['MDSTART'], mtmin)
                mtmax = max( et['MDEND'], mtmax)

        if is_ok:
            if e['MDSTART'] < mtmin:
                errset.add(well)
            elif e['MDEND'] > mtmax:
                errset.add(well)

    if not silent:
        _print_line(
            filep,
            'Wells with missing TUBING coverage',
            wset=errset,
            refset=wtrajset)

# Check for overlapping TUBING

    errset1 = set()
    errset2 = set()
    for t in trajset:
        ewseg = get_events(edict[roxar.EventType.TUBING], eowner=list(t))
        if ewseg is not None:
            is_inc = len(ewseg)*[0]
            for i, ev in enumerate(ewseg):
                if ev['MDSTART'] is None or ev['MDEND'] is None:
                    w, wb, traj = t
                    errset1.add(w)
                    if is_inc[i] == 0:
                        errlist.append(ev)
                        is_inc[i] = 1
                elif ev['MDSTART'] >= ev['MDEND']:
                    w, wb, traj = t
                    errset1.add(w)
                    if is_inc[i] == 0:
                        errlist.append(ev)
                        is_inc[i] = 1
                else:
# Check for overlapping intervals
                    for j, ev2 in enumerate(ewseg):
                        if ev2['MDSTART'] < ev2['MDEND']:
                            del1 = (ev['MDSTART'] - ev2['MDSTART'])*(ev2['MDEND']-ev['MDSTART'])
                            del2 = (ev['MDEND']   - ev2['MDSTART'])*(ev2['MDEND']-ev['MDEND'])
                            if del1 > 0 or del2 > 0:
                                w, wb, traj = t
                                errset2.add(w)
                                if is_inc[j] == 0:
                                    errlist.append(ev2)
                                    is_inc[j] = 1

    if not silent:
        _print_line(
            filep,
            'TUBING events with MDSTART >= MDEND',
            wset=errset1,
            refset=wtrajset)
        _print_line(
            filep,
            'TUBING events with MD overlapping',
            wset=errset2,
            refset=wtrajset)

# Check for overlapping WSEGSEG

    errset1 = set()
    errset2 = set()
    for t in trajset:
        ewseg = get_events(edict[roxar.EventType.WSEGSEG], eowner=list(t))
        if ewseg is not None:
            is_inc = len(ewseg)*[0]
            for i, ev in enumerate(ewseg):
                if ev['MDSTART'] is None or ev['MDEND'] is None:
                    w, wb, traj = t
                    errset1.add(w)
                    if is_inc[i] == 0:
                        errlist.append(ev)
                        is_inc[i] = 1
                elif ev['MDSTART'] >= ev['MDEND']:
                    w, wb, traj = t
                    errset1.add(w)
                    if is_inc[i] == 0:
                        errlist.append(ev)
                        is_inc[i] = 1
                else:
# Check for overlapping intervals
                    for j, ev2 in enumerate(ewseg):
                        if ev2['MDSTART'] < ev2['MDEND']:
                            del1 = (ev['MDSTART'] - ev2['MDSTART'])*(ev2['MDEND']-ev['MDSTART'])
                            del2 = (ev['MDEND']   - ev2['MDSTART'])*(ev2['MDEND']-ev['MDEND'])
                            if del1 > 0 or del2 > 0:
                                w, wb, traj = t
                                errset2.add(w)
                                if is_inc[j] == 0:
                                    errlist.append(ev2)
                                    is_inc[j] = 1

    if not silent:
        _print_line(
            filep,
            'WSEGSEG events with MDSTART >= MDEND',
            wset=errset1,
            refset=wtrajset)
        _print_line(
            filep,
            'WSEGSEG events with MD overlapping',
            wset=errset2,
            refset=wtrajset)

# Check for incorrect segment connections and missing attributes

    errset1 = set()
    errset2 = set()
    errset3 = set()
    for t in trajset:
        ewseg = get_events(edict[roxar.EventType.WSEGSEG], eowner=list(t))
        w, wb, traj = t
        if ewseg is not None:
            seglist = []
            for i, ev in enumerate(ewseg):
                segno = ev['NO']
                att = ev['ATTACH']
                seglist.append(segno)

                if att is not None:
                    if segno == att:
                        errset1.add(w)
                        errlist.append(ev)

                if ev['RADIUS'] is None or ev['RADIUS'] <= 0:
                    errset2.add(w)
                    errlist.append(ev)

                if ev['ROUGH'] is None or ev['ROUGH'] <= 0:
                    errset2.add(w)
                    errlist.append(ev)

                segset = set(seglist)
                if len(segset) < len(seglist):
                    errset3.add(w)
                if seglist != list(range(seglist[0], seglist[0]+len(seglist))):
                    errset3.add(w)

    if not silent:
        _print_line(
            filep,
            'WSEGSEG events attached to itself',
            wset=errset1,
            refset=wtrajset)
        _print_line(
            filep,
            'WSEGSEG wells with incorrect segment number sequence',
            wset=errset3,
            refset=wtrajset)
        _print_line(
            filep,
            'WSEGSEG events lacking data for radius or roughness',
            wset=errset2,
            refset=wtrajset)

    return errlist




