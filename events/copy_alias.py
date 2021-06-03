import roxar
import roxar.events

def copy_alias(elist, aliasinfo):
    """Copy event list and transfer owners according to NameAlias
    Args:
        elist (List of events): Event list
        aliasinfo (NameAlias): Alias information
    Returns:
        Copy of event list
    """

    newlist = []

    for eold in elist:
        enew = roxar.events.Event.duplicate(eold)
        evdet = roxar.events.Event.details(eold.type)
        if evdet['owner_type'] == 'Well':
            wname = eold.owner[0]
            awname = aliasinfo.get_alias(wname)
            if awname is not None:
                enew.owner = [awname]
            if eold.type == roxar.EventType.WIFSHUT:
                if eold['FWELL'] is not None:
                    aname = aliasinfo.get_alias(eold['FWELL'])
                    if aname is not None:
                        enew['FWELL'] = aname
        elif evdet['owner_type'] == 'Trajectory':
            wname = eold.owner[0]
            wbname = eold.owner[1]
            trtype = eold.owner[2]
            awname = aliasinfo.get_alias(wname)
            awbname = aliasinfo.get_alias(wbname)
            if awname is None:
                awname = wname
            if awbname is None:
                awbname = wbname
            enew.owner = [awname, awbname, trtype]
        elif eold.type == roxar.EventType.GMEMBER:
            if eold['MEMBER'] is not None:
                aname = aliasinfo.get_alias(eold['MEMBER'])
                if aname is not None:
                    enew['MEMBER'] = aname
        elif eold.type == roxar.EventType.IORFT:
            if eold['NAME'] is not None:
                aname = aliasinfo.get_alias(eold['NAME'])
                if aname is not None:
                    enew['NAME'] = aname

        newlist.append(enew)

    return newlist

def copy_alias_inverse(elist, aliasinfo):
    """Copy event list and transfer owners according to inverse NameAlias
    Args:
        elist (List of events): Event list
        aliasinfo (NameAlias): Alias information
    Returns:
        Copy of event list
    """

    newlist = []

    for eold in elist:
        enew = roxar.events.Event.duplicate(eold)
        evdet = roxar.events.Event.details(eold.type)
        if evdet['owner_type'] == 'Well':
            wname = eold.owner[0]
            awname = aliasinfo.get_alias_inverse(wname)
            if awname is not None:
                enew.owner = [awname]
            if eold.type == roxar.EventType.WIFSHUT:
                if eold['FWELL'] is not None:
                    aname = aliasinfo.get_alias_inverse(eold['FWELL'])
                    if aname is not None:
                        enew['FWELL'] = aname
        elif evdet['owner_type'] == 'Trajectory':
            wname = eold.owner[0]
            wbname = eold.owner[1]
            trtype = eold.owner[2]
            awname = aliasinfo.get_alias_inverse(wname)
            awbname = aliasinfo.get_alias_inverse(wbname)
            if awname is None:
                awname = wname
            if awbname is None:
                awbname = wbname
            enew.owner = [awname, awbname, trtype]
        elif eold.type == roxar.EventType.GMEMBER:
            if eold['MEMBER'] is not None:
                aname = aliasinfo.get_alias_inverse(eold['MEMBER'])
                if aname is not None:
                    enew['MEMBER'] = aname
        elif eold.type == roxar.EventType.IORFT:
            if eold['NAME'] is not None:
                aname = aliasinfo.get_alias_inverse(eold['NAME'])
                if aname is not None:
                    enew['NAME'] = aname

        newlist.append(enew)

    return newlist
