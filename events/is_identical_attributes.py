def is_identical_attributes(ev1, ev2):
    """Check if all defined attributes of two roxar events are identical.
    Args:
        ev1: roxar event to be compared
        ev2: roxar event to be compared
    Returns:
        True if identical attributes; False if not or if non-identical event types.
    Note:
        Date and owner not checked.
    """
    if ev1.type == ev2.type:
        for key in ev1.attribute_keys:
            if ev1[key] is not None:
                if ev1[key] != ev2[key]:
                    return False
        return True
    else:
        return False
