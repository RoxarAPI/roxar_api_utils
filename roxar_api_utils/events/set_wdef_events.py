import roxar.events

def set_wdef_events(simwells, trajectory_type='Drilled trajectory'):
    """Define roxar events from SimMultiWells
    Args:
        simwells (SimMultiWells): Well info
    Returns:
        List of roxar events
    """

    elist = []

    for simw in simwells:
        if simw.start_date is None:
            continue
        wname = simw.name
        edate = simw.start_date

        if simw.type is not None:
            eve = roxar.events.Event.create(roxar.EventType.WTYPE, edate, [wname])
            eve['TYPE'] = simw.type
            if simw.phase is not None:
                eve['PHASE'] = simw.phase
            elist.append(eve)

        if simw.bhpref is not None:
            eve = roxar.events.Event.create(roxar.EventType.WDREF, edate, [wname])
            eve['DEPTH'] = simw.bhpref
            elist.append(eve)

        if simw.group is not None:
            eve = roxar.events.Event.create(roxar.EventType.GMEMBER, edate, [simw.group])
            eve['MEMBER'] = wname
            elist.append(eve)

        if simw.lifttab is not None:
            eve = roxar.events.Event.create(roxar.EventType.WLIFTTABLE, edate, [wname])
            eve['TABLEID'] = str(simw.lifttab)
            elist.append(eve)

        if simw.crossflow is not None:
            eve = roxar.events.Event.create(roxar.EventType.WCROSSFL, edate, [wname])
            eve['ON'] = simw.crossflow
            elist.append(eve)

        if simw.densmod is not None:
            eve = roxar.events.Event.create(roxar.EventType.WDENSMOD, edate, [wname])
            if simw.densmod == 'AVE':
                eve['TYPE'] = 'Average'
            elif simw.densmod == 'SEG':
                eve['TYPE'] = 'Segregated'
            else:
                eve['TYPE'] = simw.densmod
            elist.append(eve)

        if simw.cmode is not None:
            eve = roxar.events.Event.create(roxar.EventType.WCONTROL, edate, [wname])
            eve['MODE'] = simw.cmode
            if simw.cphase is not None:
                eve['PHASE'] = simw.cphase
            else:
                eve['PHASE'] = 'From well type'
            elist.append(eve)

        if simw.mdstart is not None:
            own = [wname, wname, trajectory_type]
            eve = roxar.events.Event.create(roxar.EventType.WSEGMOD, edate, own)
            eve['MDSTART'] = simw.mdstart
            eve['MDEND'] = 10000.
            eve['TYPE'] = 'Staggered'
            eve['GRAV'] = True
            eve['FRIC'] = True
            eve['ACCEL'] = False
            eve['MULTMOD'] = 'Homogeneous'
            elist.append(eve)

    return elist
