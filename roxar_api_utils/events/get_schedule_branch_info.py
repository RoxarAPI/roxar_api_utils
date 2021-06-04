import roxar
import roxar_api_utils.wells
def get_schedule_branch_info(evlist):
    """Get branch infor from Schedule data
    Args:
        evlist (list): List of Roxar events
    Returns:
        BranchedWells object
    Note:
        In a tub file, a branch for well A is defined as A%x, where x is any string.
        Also, A%x%y is a branched well of level 2
    """

    parlib = dict()

    branches = set()
    mainwells = set()
    for eve in evlist:
        if eve.type == roxar.EventType.TUBING:
            wname = eve.owner[1]
            ix1 = wname.find('%')
            if ix1 > 0:
                branches.add(wname)
                mainwells.add(wname[:ix1])

    if len(mainwells) == 0:
        return None

    for wname in mainwells:
        parlib[wname] = dict()

# Find parent for all branches in tubing set
    for wname in branches:
        ix1 = wname.rfind('%')
        if ix1 > 0:
            ix2 = wname.find('%')
            mainwell = wname[:ix2]
            par = parlib[mainwell]
            par[wname] = wname[:ix1]

    branchinfo = roxar_api_utils.wells.BranchedWells(parents=parlib)

    wtie = dict()
    for wname in branches:
        wtie[wname] = 100000.

    for eve in evlist:
        if eve.type == roxar.EventType.TUBING:
            wname = eve.owner[1]
            if wname in branches:
                wtie[wname] = min(wtie[wname], eve['MDSTART'])

    for wname in branches:
        branchinfo.set_wtie(wname, wtie[wname])

    return branchinfo
