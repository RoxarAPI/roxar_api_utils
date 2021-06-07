"""Read binary ROFF file and convert to text format.

Note:
    Output is NOT a text ROFF file
"""
import os
import sys

this_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
roxar_api_utils_top = os.path.join(this_dir, '..', '..')
sys.path.append(roxar_api_utils_top)

import roxar_api_utils.ioutil

# --------------------------------------------------------
# Script parameters

# Input ROFF file
infile = 'test.roff'

# Output text file
outfile = 'test.txt'

# --------------------------------------------------------
# Start script

reader = roxar_api_utils.ioutil.RoffReader(infile)
with open(outfile, 'w') as fp:
    while True:
        key, type, nval,val = reader.next_key()
        if key is None:
            break

        if type == 'tag':
            print(type, key, file=fp)
        elif type == 'endtag':
            print(type, file=fp)
        else:
            print(key, type, nval, file=fp)
            if val is not None: print(val, file=fp)

print('Output to file', outfile)
