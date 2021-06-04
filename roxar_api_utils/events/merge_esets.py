from .elist_sort import elist_sort

def merge_esets(project, esets=None, grmodel=None, fsets=None, real_no=0):
    """Merge multiple roxar event sets into a single list of events
    Args:
        project: Roxar API project
        esets: List of strings, containing names on event sets in folder Events to be merged
        grmodel: String with name of grid model to take event sets from. None is not used.
        fsets: List of strings with names on event sets in grid model to be merged
        real_no (int): Realisation number
    Returns:
        List of merged events, sorted by date
    """

    elist = []
    if esets is not None:
        eventsets = project.event_sets
        if len(esets) == 1:
            elist = eventsets[esets[0]].get_events(real_no)
        else:
            for name in esets:
                est = eventsets[name]
                eslist = est.get_events(real_no)
                elist.extend(eslist)

    if grmodel is not None:
        eventsets = project.grid_models[grmodel].event_sets
        for name in fsets:
            est = eventsets[name]
            eslist = est.get_events(real_no)
            elist.extend(eslist)

    elist = elist_sort(elist)

    return elist
