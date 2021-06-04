def get_events(elist, etype=None, edate=None, eowner=None):
    """Return list of all roxar events matching type, date, and/or owner in a list of events
    Args:
        elist: List of roxar events to be searched
        etype: String, event type to be matched.  None if not used.
        edate: Datetime, event date to be matched. None if not used.
        eowner: String, event owner to be matched.  None if not used.
    Returns:
        List of roxar events matching.  None is no events match.
    """

    eventlist = []

    if etype is None:
        if eowner is None:
            if edate is None:
                return elist

            else:
                for eve in elist:
                    if eve.date == edate:
                        eventlist.append(eve)

        else:
            if edate is None:
                for eve in elist:
                    if eve.owner == eowner:
                        eventlist.append(eve)

            else:
                for eve in elist:
                    if eve.date == edate:
                        if eve.owner == eowner:
                            eventlist.append(eve)

    else:
        if eowner is None:
            if edate is None:
                for eve in elist:
                    if eve.type == etype:
                        eventlist.append(eve)

            else:
                for eve in elist:
                    if eve.type == etype:
                        if eve.date == edate:
                            eventlist.append(eve)

        else:
            if edate is None:
                for eve in elist:
                    if eve.type == etype:
                        if eve.owner == eowner:
                            eventlist.append(eve)

            else:
                for eve in elist:
                    if eve.type == etype:
                        if eve.date == edate:
                            if eve.owner == eowner:
                                eventlist.append(eve)

    if len(eventlist) == 0:
        return None
    else:
        return eventlist
