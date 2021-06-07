"""Read data from Summary files, calculate watercut, and write result as a new set of Summary files
"""

import roxar_api_utils.profiles
import numpy as np

# --------------------------------------------------------------------------
# Script parameters

# File root for input ECLIPSE Summary files
froot_input = r'C:\Users\torb\MyData\testdata\IO\EclSim\ex15\HETRO'

# File root for output ECLIPSE Summary files
froot_output = r'C:\Users\torb\MyData\temp\summary\TEST'

# --------------------------------------------------------------------------
# Start script

# Read Summary files
reader = roxar_api_utils.profiles.EclSummaryReader(froot_input)
profiles = reader.read_spec()
profiles = reader.read_summary()

nofiles = reader.nofiles
nokeys = reader.nokeys
nosteps = reader.nosteps
print(
    'No of Summary files read: ',
    nofiles,
    '. No of keys: ',
    nokeys,
    '. No of time steps: ',
    nosteps,
    '.',
    sep='')

# Get set of well names:
wset = profiles.wellset()

# Calculate watercut for all wells with oil and water rate present:
for well in wset:
    wopr = profiles.get_vector('WOPR', well)
    wwpr = profiles.get_vector('WWPR', well)
    if wopr is not None and wwpr is not None:
        wlpr = wopr.profdata + wwpr.profdata
        wwct = np.zeros(nosteps)
        for i in range(nosteps):
            if wlpr[i] > 0: wwct[i] = wwpr.profdata[i]/wlpr[i]

    profiles.set_vector('WWCT', wwct, well, wopr.num, 'SM3/SM3')

# Write result to Summary files
print('Writing Summary files....')
writer = roxar_api_utils.profiles.EclSummaryWriter(profiles, froot_output, None, True)
writer.write_spec()
writer.write_summary()
print('Print OK')
