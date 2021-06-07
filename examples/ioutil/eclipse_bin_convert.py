"""Convert content of a binary ECLIPSE file to text format
"""

import roxar_api_utils.ioutil

# --------------------------------------------------------
# Script parameters

# Input binary Eclipse file
ecl_file = r'C:\Users\torb\MyData\temp\CASE1.INIT'

# Output file
out_file = r'C:\Users\torb\MyData\temp\eclbin.txt'

# --------------------------------------------------------
# Start script

fp = open(ecl_file,'rb')
fpo = open(out_file,'w')
reader = roxar_api_utils.ioutil.EclBinReader(fp)
reader.print_all(fpo)
