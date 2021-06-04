import roxar
import roxar.events
def get_elist_owners(elist):
    """Get a dict of event owners present in the event set
    Args:
        elist: List of roxar events - events to be checked
    Returns:
        Dictionary of set of strings with owner names.  Dict keys = owner type.
    Note:
        Dict key 'AllWells' returns all wells, defined from well and
        trajectory events
    """

    ownerdict = dict()
    ownerdict['Well'] = set()
    ownerdict['Well group'] = set()
    ownerdict['Trajectory'] = set()
    ownerdict['Simulator model'] = set()
    ownerdict['AllWells'] = set()
    ownerdict['Wellbores'] = set()

    for eve in elist:
        evdet = roxar.events.Event.details(eve.type)
        if evdet['owner_type'] == 'Well':
            ownerdict['Well'].add(eve.owner[0])
            ownerdict['AllWells'].add(eve.owner[0])
        elif evdet['owner_type'] == 'Trajectory':
            ownerdict['Trajectory'].add(tuple(eve.owner))
            ownerdict['AllWells'].add(eve.owner[0])
            ownerdict['Wellbores'].add(eve.owner[1])
        else:
            ownerdict[evdet['owner_type']].add(eve.owner[0])

    return ownerdict
