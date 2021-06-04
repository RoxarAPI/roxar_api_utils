def copy_for_owners(elist, owner_list, rename_dict=None):
    """Copy Roxar events for a list of owners, eventually with owner renaming
    Args:
        elist: List of roxar events
        owner_list: List of owner to be copied from
        rename_dict: Dictionary of new owner names, for key equal to old name
    Returns:
        List of roxar events copied
    """

    newlist = []

    if rename_dict is None:
        for eve in elist:
            if eve.owner in owner_list:
                newlist.append(eve)
    else:
        for eve in elist:
            eow = eve.owner
            if eow in owner_list:
                eve.owner = rename_dict.get(eow, eow)
                newlist.append(eve)

    return newlist
