"""Read WELSPECS data from ECLIPSE input file
"""

import roxar_api_utils.ioutil

# --------------------------------------------------------
# Script parameters

# Input ECLIPSE file
infile = r'C:\Users\torb\MyData\temp\test.data'

# --------------------------------------------------------
# Start script

def _read_welspecs(reader):
    """Read data in keyword WELSPECS
    """

    no_data = '*???*'

    while True:

        try:
            wname = reader.readstr(no_data)
            if wname is no_data : break
            gname = reader.readstr(no_data)
            if gname is no_data : gname = 'FIELD'
            ix,jy = reader.readinta(2)
            refdepth = reader.readfloat(-1.)
            phase = reader.readstru('OIL')
            dradius = reader.readfloat(0.0)
            inflow = reader.readstru('STD')
            shut = reader.readstru('SHUT')
            crossflow = reader.readyesno('YES')
            ipres = reader.readint(1)
            density = reader.readstru(no_data)
            ifip = reader.readint(0)
            reader.readslash()

            print(wname, gname, ix, jy, refdepth, phase)

        except ValueError:
            reader.writeerror('Value error')
        except IOError:
            reader.writeerror('IO error')

    reader.readslash()

    return

# Main

errfile = None
reader = roxar_api_utils.ioutil.KeyDataReader(infile, errfile)

doread = True
keys_found = 0
while doread:
    try:
        key = reader.nextkey()
    except ValueError:
        reader.fine()
        raise
    except IOError:
        reader.fine()
        raise

    if key is None: break
    keys_found += 1

    if key == 'WELSPECS':
        print('Reading key', key)
        _read_welspecs(reader)

reader.fine()
