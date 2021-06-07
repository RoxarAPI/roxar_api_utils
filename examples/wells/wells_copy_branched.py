"""Read file with branch info and create copy of branched well trajectories

Wells are assumed to be organised flat in the data tree.
For branched wells defined in the input text file, trajectories are copied
into new (branched) wells in the data tree.
Well names for branched wells are constructed from old names by adding a name prefix
to the well/wellbore name.

Copied sidetracks will have survey points only below the branch tie-in point.

Example:
Well A,B, and C are defined in the data tree.
The branch info file states that B and C are branches to well A.
The name prefix is defined as 'B_'.
The script then creates a copy well named B_A, with wellbore B_A, B_B, B_C.
"""

import numpy as np

import roxar.wells

import roxar_api_utils.wells


# -----------------------------------------------------------------------
# Script parameters

# Input branch file
file_name = r'C:\Users\torb\MyData\temp\well_branches.txt'

# Prefix for branched wells
name_prefix = 'BR_'

# Trajectory definition
trajectory_type = 'Drilled trajectory'

# ------------------------------------------------------------------------
# Start script

def _find_tie(parents, trajtype):
    md_tie = dict()

    for bname in parents.keys():
        md_tie[bname] = 0.0

        if bname in project.wells.keys():
            well2 = project.wells[bname]
            track2 = well2.wellbore.trajectories[trajtype]
            points2 = track2.survey_point_series.get_survey_points()

            parname = parents[bname]
            if parname in project.wells.keys():
                well1 = project.wells[parname]
                track1 = well1.wellbore.trajectories[trajtype]
                points1 = track1.survey_point_series.get_survey_points()

                if well1.wellhead != well2.wellhead:
                    print('Non-matching well heads ', bname, parname)
                    continue
                if well1.rkb != well2.rkb:
                    print('Non-matching rkb ', bname, parname)
                    continue

                mdbreak = 0.0
                for i, p in enumerate(points1):
                    if np.all(p != points2[i]):
                        break
                    mdbreak = p[0]

                md_tie[bname] = mdbreak
            else:
                md_tie[bname] = 0.0
        else:
            md_tie[bname] = 0.0

    return md_tie

def _create_branched(wellname, branchinfo):

    if wellname not in branchinfo.get_branched_wells():
        return md_tie
    parents = branchinfo.get_parents(wellname)
    prefx = branchinfo.prefix
    trajtype = branchinfo.traj_type

    newname = prefx + wellname
    if wellname in project.wells.keys():
        oldwell = project.wells[wellname]
    else:
        print('Well not found: ', wellname)
        return None

    topwell = project.wells.create(newname)
    roxar_api_utils.wells.copy_well(topwell, oldwell)

    # Find tie-in point for each branch
    md_tie = _find_tie(parents, trajtype)

    # Find branches per branch-level:
    branch_lev = branchinfo.get_branch_names_leveled(wellname)
    nlev = len(branch_lev)

    # Copy branches
    for ilev in range(0, nlev):
        for bname in branch_lev[ilev]:
            if bname in project.wells.keys():
                oldwell = project.wells[bname]
                wbore_name = prefx + bname

                if parents[bname] == wellname:
                    parwellb = topwell.wellbore
                else:
                    parname = prefx + parents[bname]
                    try:
                        parwellb = topwell.all_wellbores[parname]
                    except KeyeError as e:
                        errmes = 'Cannot find parent wellbore ' + parname + '\n' + str(e)
                        print(errmes)
                        md_tie[bname] = 0.0
                        return md_tie
                partrack = parwellb.trajectories[trajtype]
                try:
                    wbore = parwellb.wellbores.create(wbore_name)
                    roxar_api_utils.wells.copy_trajectories(
                        wbore, oldwell.wellbore, partrack, md_tie[bname])
                except ValueError as e:
                    errmes = 'Cannot create wellbore ' + wbore_name + '\n' + str(e)
                    print(errmes)
                    return md_tie
                    #raise ValueError(errmes)
            else:
                print('Branch not found: ', bname)
                md_tie[bname] = 0.0

    return md_tie

def _verify_rms_wells(wname, branchinfo):
    """Verify that all branches are RMS wells

    """

    if wname not in branchinfo.get_branched_wells():
        print('Well', wname, 'is not in the list of wells to be copied')
        return True
    parents = branchinfo.get_parents(wname)

    if wname in project.wells:
        for parent in parents:
            if parent not in project.wells:
                print('Parents for', wname, parent, 'does not exist so', wname, ' will not be copied')
                return False
    else:
        print('Well', wname, 'does not exist in this project and cannot be copied')
        return False

    return True



# Main function
branchinfo = roxar_api_utils.wells.BranchedWells(file_name)
branchinfo.prefix = name_prefix
branchinfo.traj_type = trajectory_type
wellset = branchinfo.get_branched_wells()

# Delete existing branched wells
for name in wellset:
    newname = name_prefix + name
    if newname in project.wells.keys():
        del project.wells[newname]

# Copy branched wells
nbr = 0
for name in wellset:
    is_ok = _verify_rms_wells(name, branchinfo)
    if is_ok:
        md_tie = _create_branched(name, branchinfo)
        newname = name_prefix + name
        print('Branched well created: ', newname)
        nbr += 1

print('\nCreated', nbr, 'branched wells')
