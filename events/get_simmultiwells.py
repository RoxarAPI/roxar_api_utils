from datetime import datetime

import roxar
import roxar.events

def get_simmultiwells(simwells, elist):
    """Get data for the SimMultiWells class from event set
    Args:
        simwells (SimMultiWells):  Well data
        elist (event set): Input events
    Note: Start date for a well is defined as first date with no-zero rates, if these exists
    """

    for eve in elist:
        evdet = roxar.events.Event.details(eve.type)
        if evdet['owner_type'] == 'Well' or evdet['owner_type'] == 'Trajectory':
            wname = eve.owner[0]
            simw = simwells.get_well(wname)
            if simw is None:
                simw = simwells.add_well_name(wname)
                simw.start_date = datetime(2050, 1, 1)
                simw.phase = None
                simw.type = None
                simw.cphase = None
                simw.cmode = None

        if eve.type == roxar.EventType.WHISTRATE:
            rat = 0.0
            if eve['SRATEO'] is not None:
                rat = max(rat, eve['SRATEO'])
            if eve['SRATEW'] is not None:
                rat = max(rat, eve['SRATEW'])
            if eve['SRATEG'] is not None:
                rat = max(rat, eve['SRATEG'])
            if eve['SRATEL'] is not None:
                rat = max(rat, eve['SRATEL'])
            if rat > 0 and eve.date < simw.start_date:
                simw.start_date = eve.date
        elif eve.type == roxar.EventType.WLIMRATE:
            rat = 0.0
            if eve['SRATEO'] is not None:
                rat = max(rat, eve['SRATEO'])
            if eve['SRATEW'] is not None:
                rat = max(rat, eve['SRATEW'])
            if eve['SRATEG'] is not None:
                rat = max(rat, eve['SRATEG'])
            if eve['SRATEL'] is not None:
                rat = max(rat, eve['SRATEL'])
            if eve['RRATE']  is not None:
                rat = max(rat, eve['RRATE'])
            if rat > 0 and eve.date < simw.start_date:
                simw.start_date = eve.date

            if eve.date >= simw.start_date:
                if eve['TYPEW'][0] == 'I':
                    simw.type = 'Injector'
                    if eve['SRATEO'] is not None and eve['SRATEO'] > 0:
                        simw.phase = 'Oil'
                    if eve['SRATEW'] is not None and eve['SRATEW'] > 0:
                        simw.phase = 'Water'
                    if eve['SRATEG'] is not None and eve['SRATEG'] > 0:
                        simw.phase = 'Gas'
                else:
                    simw.type = 'Producer'

    for simw in simwells:
        if simw.start_date > datetime(2049, 1, 1):
            simw.start_date = datetime(1900, 1, 1)
        if simw.type is None:
            simw.type = 'Producer'
        if simw.phase is None:
            simw.phase = 'Oil'

    for eve in elist:
        evdet = roxar.events.Event.details(eve.type)
        if evdet['owner_type'] == 'Well' or evdet['owner_type'] == 'Trajectory':
            wname = eve.owner[0]
            simw = simwells.get_well(wname)
            if simw is None:
                simw = simwells.add_well_name(wname)
                simw.start_date = eve.date
                simw.phase = None
                simw.type = None
                simw.cphase = None
                simw.cmode = None
            else:
                if simw.start_date < datetime(1910, 1, 1):
                    simw.start_date = eve.date

        if eve.type == roxar.EventType.WTYPE:
            simw.type = eve['TYPE']
            if simw.phase is None and eve['PHASE'] is not None:
                simw.phase = eve['PHASE']
        elif eve.type == roxar.EventType.WDENSMOD:
            simw.densmod = eve['TYPE']
        elif eve.type == roxar.EventType.WLIFTTABLE:
            try:
                simw.lifttab = int(eve['TABLEID'])
            except:
                errmes = 'Failed to read table id in event WLIFTTABLE' + str(eve['TABLEID'])
                raise ValueError(errmes)
        elif eve.type == roxar.EventType.WCROSSFL:
            simw.crossflow = eve['ON']
        elif eve.type == roxar.EventType.WSEGMOD:
            simw.is_wseg = True
            if eve['MDSTART'] is not None:
                if simw.mdstart is None:
                    simw.mdstart = 100000.
                simw.mdstart = min(simw.mdstart, eve['MDSTART'])
        elif eve.type == roxar.EventType.WSEGSEG:
            simw.is_wseg = True
            if eve['BRANCH'] is not None:
                simw.no_branches = max(simw.no_branches, eve['BRANCH'])
            if eve['MDSTART'] is not None:
                if simw.mdstart is None:
                    simw.mdstart = 100000.
                simw.mdstart = min(simw.mdstart, eve['MDSTART'])
        elif eve.type == roxar.EventType.WDREF:
            simw.bhpref = eve['DEPTH']
        elif eve.type == roxar.EventType.WCONTROL:
            if eve.date >= simw.start_date:
                simw.cmode = eve['MODE']
                phase = eve['PHASE']
                if simw.cphase is None:
                    simw.cphase = phase
                elif simw.cphase != phase:
#                    print( 'Change in well control phase for well', simw.name,end='' )
#                    print( ' from', simw.cphase, 'to', phase )
                    simw.cphase = phase

                if phase == 'Liquid':
                    phase = 'Oil'
                    if simw.type is None:
                        simw.type = 'Producer'
                elif phase == 'Total':
                    phase = 'Oil'
                    if simw.type is None:
                        simw.type = 'Producer'
                if simw.phase is None:
                    simw.phase = phase

    for eve in elist:
        if eve.type == roxar.EventType.GMEMBER:
            gname = eve.owner[0]
            wname = eve['MEMBER']
            simw = simwells.get_well(wname)
            if simw is not None:
                simw.group = gname
            else:
                simwells.add_group(wname, gname)

    return simwells
