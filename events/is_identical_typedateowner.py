def is_identical_typedateowner(ev1, ev2):
    """Check if two events are identical in type, date, and owner.
    Args:
        ev1: roxar event
        ev2: roxar event
    Returns:
        True if the two events are identical in type, date, and owner; otherwise False.
"""
    ident = False
    if ev1.type == ev2.type:
        if ev1.date == ev2.date:
            if ev1.owner == ev2.owner:
                ident = True
    return ident
