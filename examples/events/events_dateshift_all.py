"""Time shift all events in an event set, by defining a new start date
"""

from datetime import datetime

import roxar_api_utils.events

# --------------------------------------------------------
# Script parameters

# Input event set:
eset_input = "Events_Set1"

# Output event set:
eset_output = "SHIFTED"

# New start date for event set
date0 = datetime(2010, 1, 1)

# ---------------------------------------------------------
# Start script


eslist = project.event_sets[eset_input].get_events()
eslist = roxar_api_utils.events.elist_dateshift(eslist, date0)

new = project.event_sets.create(eset_output)
new.set_events(eslist)
print('RMS event set created:', eset_output)
