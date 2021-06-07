"""Read Schedule .net file and store as events
"""

from datetime import datetime

import roxar_api_utils.events

# ----------------------------------------------------------------------------------------
# Script parameters

# Output event set. Set overwrite flag False if data should be merged into existing set.
eset_out = 'ScheduleGroups'
overwrite = True

# Schedule net file
net_file_name = r'C:\Users\torb\MyData\temp\temp.net'

# Define symbolic dates (year,moth,date) as dictionary
symbdate = dict()
symbdate['SOS'] = datetime(1990, 1, 1)

# ------------------------------------------------------------------------------------------
# Script start

elist = roxar_api_utils.events.read_schedule_net(net_file_name, symbdate)

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
