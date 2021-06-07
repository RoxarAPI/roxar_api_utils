"""Read CSV file with well definition data and store as events
"""
import roxar.events
import roxar_api_utils.ioutil
import roxar_api_utils.flow
import roxar_api_utils.events

# ----------------------------------------------------------------------------------------
# Script parameters

# Output event set. Set overwrite flag False if data should be merged into existing set.
eset_out = 'CSVData'
overwrite = True

# Input CSV file name
csv_file_name = r'C:\Users\torb\MyData\temp\x_well_summary.csv'

# Date format in CSV file, as python strftime string.
# %Y = Four-digit year,
# %m = Two-digit-month
# %d = Two-digit-day
date_format = '%d.%m.%Y'
#   date_format = '%d-%m-%Y'
#   date_format = '%Y-%m-%d'

# ----------------------------------------------------------------------------------------
# Script start

simwells = roxar_api_utils.flow.SimMultiWells()

aliasdict = simwells.read_csv(csv_file_name, date_format)
aliasinfo = roxar_api_utils.ioutil.NameAlias(alias_dict=aliasdict)

elist = roxar_api_utils.events.set_wdef_events(simwells)

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

