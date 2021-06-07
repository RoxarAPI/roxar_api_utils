"""Make a copy of an event set and change all well names according to alias infomation
"""

import roxar
import roxar.events
import roxar_api_utils.ioutil
import roxar_api_utils.events

# --------------------------------------------------------------------------
# Script parameters

# Input event set
input_eset = 'All'

# Output event set
output_eset = 'All_alias'

# File name for alias file
file_name = r'C:\Users\torb\MyData\temp\well_alias.txt'

# Flag for inverse name translation. Set to true if from ECLIPSE name to RMS name.
is_inverse = False

# --------------------------------------------------------------------------
# Script start

aliasinfo = roxar_api_utils.ioutil.NameAlias(file_name)

elist = project.event_sets[input_eset].get_events()
if is_inverse:
    newlist = roxar_api_utils.events.copy_alias_inverse(elist, aliasinfo)
else:
    newlist = roxar_api_utils.events.copy_alias(elist, aliasinfo)

evset   = project.event_sets.create(output_eset)
evset.set_events(newlist, 0)
print('RMS event set created:', output_eset)
