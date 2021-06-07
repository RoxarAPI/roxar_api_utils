"""
Find the Measured Depths for specific TVDs
"""

import roxar_api_utils.wells

tvd_start = 1610.0
tvd_end   = 1620.0

wb = project.wells['OP1'].all_wellbores['OP1']
sps = wb.trajectories['Drilled trajectory'].survey_point_series
mdps = sps.get_measured_depths_and_points()

md1 = roxar_api_utils.wells.md_from_tvd(tvd_start, sps, mdps, 0.0)
md2 = roxar_api_utils.wells.md_from_tvd(tvd_end, sps, mdps, abs(md1))

print('TVD {}: MD {}'.format(tvd_start, md1))
print('TVD {}: MD {}'.format(tvd_end, md2))
