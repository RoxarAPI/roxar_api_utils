"""Read OFM data and output as ECLIPSE unfied summary files
"""

import roxar_api_utils.profiles

# ---------------------------------------------------------------------------
# Script parameters

# File root for output Summary files
froot_output = r'C:\Users\torb\MyData\temp\summary\TEST'

# Input OFM\Schedule file
vol_file = r'C:\Users\torb\MyData\temp\x_ofm.vol'

# Date format, if *DATE keyword is used in input file.
date_format = 'dd.MM.yyyy'

# Alias file for renaming wells.  Use None if not used
alias_file = None
#    alias_file = r'C:\Users\torb\MyData\temp\x_rename_wells.txt'

# Value for undefined values in file.
# If None, the previous time step value is used, which is Schedule default
undef_value = None

# Flag for setting negative volumes/pressures to zero
set_nonnegative = True

# Flag for doing shift OFM --> Constant backwards.  Set False if no conversion
time_shift = False

# ----------------------------------------------------------------------------
# Script starts

profiles = roxar_api_utils.profiles.read_ofm(
    vol_file, date_format, alias_file, undef_value, set_nonnegative, time_shift)

print(profiles)

# Write result to Summary files
print('Writing Summary files....')
writer = roxar_api_utils.profiles.EclSummaryWriter(profiles, froot_output, None, True)
writer.write_spec()
writer.write_summary()
print('Summary files written OK')
