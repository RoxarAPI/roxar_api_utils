"""Read Schedule event file and store as an RMS event set

When reading perforations, these are given perforation id A, B, C, ... in the order read.
"""
from datetime import datetime

import roxar_api_utils.events

# ---------------------------------------------------------------------------------
# Script parmeters
#

# Output event set.  Set overwrite flag to False if events should be merged into existing set.
eset_out = 'ScheduleEvents'
overwrite = True

# Schedule events file
file_name = r'C:\Users\torb\MyData\temp\schedule.ev'

# Define symbolic dates as dictionary(year,moth,date)
symbdate = dict()
symbdate['SOS'] = datetime(1990, 1, 1)
# symbdate['EOH'] = datetime(2016, 1, 1)

# ---------------------------------------------------------------------------------
# Start script

elist = roxar_api_utils.events.read_schedule_ev(file_name, symbdate)
print('Event file read:', file_name)

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
