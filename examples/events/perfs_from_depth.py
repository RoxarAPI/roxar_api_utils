"""Define perforations for a well based on a TVD interval.

Use with Emerald.
"""

from datetime import datetime

import roxar.events

import roxar_api_utils.wells

# --------------------------------------------------------
# Script parameters

# Output event sets
eset_out = 'Perfs'

# Event owner
event_owner = ('OP1','OP1','Drilled trajectory')

# Event date
event_date = datetime(2010, 1, 1)

# TVD interval
tvd_start = 1610.
tvd_end = 1620.

# External wellbore radius
radius = 0.15

# ---------------------------------------------------------
# Script start

def _perfs_from_tvd(tvd1, tvd2, evdate, towner, wradius, project):
    """Set perforations corresponding to given depth interval in well
    Args:
        tvd1: First TVD value
        tvd2: Second TVD value
        evdate: Event date to be used
        wowner: Well name
        wradius: Wellbore external radius
    Returns:
        List of PERF events
    Note:
        Trajectory assumed to be wowner.wowner.'Drilled trajectory'
    """
    evlist = []

    well, wb, traj = towner

    w = project.wells[well]
    sps = w.all_wellbores[wb].trajectories[traj].survey_point_series
    wtraj = sps.get_measured_depths_and_points()

    md2 = 0.

    while True:
        md1 = roxar_api_utils.wells.md_from_tvd(tvd1, sps, wtraj, abs(md2))
        md2 = roxar_api_utils.wells.md_from_tvd(tvd2, sps, wtraj, abs(md1))

        if md1 < 0 and md2 < 0 :
            break    # Interval above well

        ev = roxar.events.Event.create(roxar.EventType.PERF, evdate, towner)
        ev['MDSTART'] = float(abs(md1))
        ev['MDEND'] = float(abs(md2))
        ev['RADIUS'] = wradius
        evlist.append(ev)

        if md2 < 0:
            break

    return evlist

# Main
evlist = _perfs_from_tvd(tvd_start, tvd_end, event_date, event_owner, radius, project)

# Set RMS event set:
eset = project.event_sets.create(eset_out)
eset.set_events(evlist)
print('RMS event set created:', eset_out)
