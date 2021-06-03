from .get_elist_dateint import get_elist_dateint

def elist_dateshift(elist=None, date0=None, owner=None):
    """Set new start date for list of events
    Args:
        elist (list): list of roxar events
        date0 (datetime): new start date for events
        owner (str): optional owner of events to be shifted.  None shifts all.
    Returns:
        Time-shifted list of roxar events
    """

    date0_org, dum = get_elist_dateint(elist, owner)
    delt = date0 - date0_org

    if owner is None:
        for i, eve in enumerate(elist):
            newdate = eve.date + delt
            elist[i].date = newdate

    else:
        for i, eve in enumerate(elist):
            if eve.owner == owner:
                newdate = eve.date + delt
                elist[i].date = newdate

    return elist
