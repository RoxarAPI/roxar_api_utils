"""Perform QC for multiple event sets, including flow model event sets
"""
import sys
import os
from datetime import datetime

import roxar_api_utils.events

# ----------------------------------------------------------------
# Script parameters

# List of input event set in Events folder
input_esets = ['Events_Set2']

# Grid model and list of input flow model event set, use None if not defined
grid_model = 'FlowModel'
input_fsets = ['FlowModel_Event_Set2']

# Output event set with incorrect events; use None if not defined
output_eset = 'QC'

# Output text file with QC results, use None for output to RMS console
output_file = r'C:\Users\torb\MyData\temp\events_qc.txt'

# ------------------------------------------------------------------
# Script starts

def _events_qc(project, input_esets=None, grid_model=None, input_fsets=None, output_file=None):
    """Quality control on collections of event sets
    Args:
        project: RMS project
    Returns:
        List of Roxar events flagged as possibly incorrect
    """

    if output_file is None:
        ofil = sys.stdout
    else:
        ofil = open(output_file, 'w')

# Write header
    today = datetime.now()
    user = os.getlogin()

    print('Event set QC', file=ofil)
    print(today.strftime("%d. %b %Y"), 'by user', user, file=ofil)
    print('Sets included:', file=ofil)
    for s in input_esets:
        print('   ', s, file=ofil)
    if grid_model is not None:
        for s in input_fsets:
            print('   ', s, '  (', grid_model, ')', file=ofil)
    print(file=ofil)

# Merge event sets
    elist = roxar_api_utils.events.merge_esets(project, input_esets, grid_model, input_fsets)
# QC
    qclist = roxar_api_utils.events.check_events(project, elist, silent=False, filep=ofil)

    return qclist

# Main
qclist = _events_qc(project, input_esets, grid_model, input_fsets, output_file)

if output_file is not None:
    print('Output to file', output_file)

# Store result
if qclist is not None and len(qclist) > 0:
    setnames = project.event_sets
    new = setnames.create(output_eset)
    new.set_events(qclist, 0)
    print('\nRMS event set created:', output_eset)
