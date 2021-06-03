import roxar.events
def verify_event_attributes(elist):
    """Identify roxar events where attribute choices do not match the predefined.
    Args:
        elist: List of roxar events - events to be checked
    Returns:
        List of roxar events where attribute choices do not match the predefined
    """
    errlist = []
    for eve in elist:
        isok = True
        evdet = roxar.events.Event.details(eve.type)
        attdets = evdet['attribute_details']
        if len(attdets) > 0:
            for att in attdets:
                attname = att['key']
                if len(att['choices']) > 0 and eve[attname] is not None:
                    isok = False
                    for cho in att['choices']:
                        if cho == eve[attname]:
                            isok = True

        if not isok:
            errlist.append(eve)

    return errlist
