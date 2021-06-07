"""Read Schedule .tub file and store as events.  Also create branch-file.
"""
from datetime import datetime

import roxar_api_utils.events

# -------------------------------------------------
# Script parameters

# Output event set.  Set overwrite flag to False to merge with existing events.
eset_out = 'ScheduleTub'
overwrite = True

# Output branch file name.  Use None to prevent output
branch_file_name = r'C:\Users\torb\MyData\Troll\work\well_branches_tub.txt'

# Schedule tubing file name
tub_file_name = r'C:\Users\torb\MyData\Troll\161116_from_henrik\T-HM-W2015-02.tub'

# Date for start of simulation (year, month, date)
start_simulation = datetime(1990, 1, 1)

# ------------------------
# Start script

elist = roxar_api_utils.events.read_schedule_tub(tub_file_name, start_simulation)
print('Tub file read:', tub_file_name)

if len(elist) == 0:
    print('No events created.')
elif overwrite:
    eset = project.event_sets.create(eset_out)
    eset.set_events(elist)
    print('RMS event set created:', eset_out)
else:
    eset = project.event_sets.create(eset_out)
    oldlist = eset.get_events()
    oldlist.extend(elist)
    eset.set_events(oldlist)
    print('RMS event set updated:', eset_out)

# Get branch info:
if branch_file_name is not None:
    branchinfo = roxar_api_utils.events.get_schedule_branch_info(elist)
    branchinfo.write_txt(branch_file_name)
    print('Branch file written:', branch_file_name)
