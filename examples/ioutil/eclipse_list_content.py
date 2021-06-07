"""List keywords in a binary file from ECLIPSE to standard output
"""

import roxar_api_utils.ioutil

# --------------------------------------------------------
# Script parameters

ecl_file = r'C:\Users\torb\MyData\Eclipse\CASE1\CASE1.INIT'

# --------------------------------------------------------
# Start script

fp = open(ecl_file, 'rb')
reader = roxar_api_utils.ioutil.EclBinReader(fp)
reader.list_all()

