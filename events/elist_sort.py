import operator

def elist_sort(elist, type='D'):
    """Sort list of roxar events
    Args:
        elist: List of roxar events
        type: String defining sorting type, combination of (D=Date, T=Type, O=Owner)
    Returns:
        Sorted version of elist
    """

    if type == 'D':
        elist.sort(key=operator.attrgetter('date'))
    elif type == 'O':
        elist.sort(key=operator.attrgetter('owner'))
    elif type == 'T':
        elist.sort(key=operator.attrgetter('type'))
    elif type == 'DO':
        elist.sort(key=operator.attrgetter('date', 'owner'))
    elif type == 'DT':
        elist.sort(key=operator.attrgetter('date', 'type'))
    else:
        estring = 'Illegal sorting type: ' + type
        raise ValueError(estring)

    return elist
