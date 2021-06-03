def get_elist_dates(elist):
    """Get sorted list of event dates defined in list of events
    Args:
        eset: List of roxar events
    Returns:
        Sortedt list of datetime objects
    """

    eset = set()
    for eve in elist:
        eset.add(eve.date)
    return sorted(list(eset))
