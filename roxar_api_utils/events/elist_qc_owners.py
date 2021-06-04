import roxar
import roxar.events

def elist_qc_owners(elist):
    """Return a list of all events with non-standard event owners
    Args:
        elist: List of roxar events
    Returns:
        List of flawed events
    """

    errlist = []
    for eve in elist:
        evdet = roxar.events.Event.details(eve.type)
        if evdet['owner_type'] == 'Simulator model':
            if eve.owner[0] != 'Simulator':
                errlist.append(eve)
        elif evdet['owner_type'] == 'Trajectory':
            if len(eve.owner) != 3:
                errlist.append(eve)

    return errlist
