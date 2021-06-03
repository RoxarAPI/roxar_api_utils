def get_elist_dateint(elist, owner=None):
    """Get start and end date for list of events
    Args:
        eset (list): list of roxar events
        owner: optional owner of event to check.  Use None if all.
    Returns:
        datetime object with start and end date
    Note:
        If owner not found, returns dateint for the whole set
    """

    date0 = elist[0].date
    date1 = date0

    if owner is None:
        for eve in elist:
            date0 = min(date0, eve.date)
            date1 = max(date1, eve.date)

    else:
        for eve in elist:
            if eve.owner == owner:
                date0 = min(date0, eve.date)
                date1 = max(date1, eve.date)

    return (date0, date1)
