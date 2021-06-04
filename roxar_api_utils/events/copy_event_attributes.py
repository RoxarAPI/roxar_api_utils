def copy_event_attributes(ev1, ev2):
    """Copy all attributes from one roxar event to another.
    Args:
        ev1: roxar event to copy into
        ev2: roxar event to copy attributes from
    Returns:
        An updated version of ev1. Unaltered if the two events are not of same type.
    """
    if ev1.type == ev2.type:
        for key in ev1.attribute_keys:
            ev1[key] = ev2[key]

    return ev1
