import struct
import sys

# =========================================================================================
# ROFF READER CLASS
# =========================================================================================

class RoffReader:
    """Reader for binary ROFF file
    Args:
        filename: ROFF file name as string
        errfile: File pointer to file for error messages
    """

    def __init__(self, infile, errfile=None):

        # Settings for error handling:

        if errfile is None:
            errfile = sys.stdout
        self._errfile = errfile
        self._ok = True

        # Settings for current input file:
        self._roffname = infile
        self._decode = 'ascii'
        try:
            self._roff = open(infile, 'rb')
        except OSError as e:
            print('\nFatal error: Cannot open file ', infile, '\n', file=self._errfile)
            raise OSError(e)

        # Check binary
        try:
            cval = self._roff.read(8)
            cc = cval.decode(self._decode)
            if cc != 'roff-bin':
                errstr = '\nFatal error: Not a binary ROFF file ' + infile + '\n'
                raise ValueError(errstr)

            self._roff.read(1)

        except:
            errstr = '\nFatal error: Not correct binary ROFF file ' + infile + '\n'
            raise ValueError(errstr)

        # Format strings for byte-swapping
        self._fform = '>f'
        self._dform = '>d'
        self._iform = '>i'

        # Storage of input values
        self._grid = None

        self._filetype = ''

    def next_key(self):
        """Read next keyword in binary ROFF file
        Returns:
            keyword, data type, number of values, and values
        """

        alltypes = ('int', 'float', 'double', 'bool', 'byte', 'char')
        key = None
        vtype = None
        nval = 0
        val = None

        string = self._readc()
        if   string == '':
            pass
        elif string == 'tag':
            tagname = self._readc()
            if tagname != 'eof':
                key = tagname
                vtype = 'tag'
        elif string == 'endtag':
            key = string
            vtype = 'endtag'

        elif string in alltypes:
            key, vtype, val = self._readval(string)
            nval = 1
        elif string == 'array':
            key, vtype, nval, val = self._readarray()
        else:
            errstr = 'Unexpected tag/key: ' + string
            raise ValueError(errstr)


        return (key, vtype, nval, val)

    def _readval(self, vtype):
        """Read single value of arbitrary type
        Args:
            tagname - string - Roff tag name
            type    - string - Roff data type
        """

        key = self._readc()

        if key == 'byteswaptest':
            vtype = 'str'
            val = self._byteswaptest()

        elif vtype == 'int':
            val = self._readi()

        elif vtype == 'float':
            val = self._readf()

        elif vtype == 'double':
            val = self._readd()

        elif vtype == 'bool':
            val = self._readb()

        elif vtype == 'byte':
            val = self._readby()

        elif vtype == 'char':
            val = self._readc()
            vtype = 'str'

        else:
            errstr = 'Unknown data type : ' + vtype
            raise ValueError(errstr)

        return (key, vtype, val)

    def _readarray(self):
        """Read array of arbitrary type
        Args:
            tagname - string - Roff tag name
        """

        vtype = self._readc()
        key = self._readc()
        nval = self._readi()
        val = None

        if nval <= 0:
            return (key, vtype, nval, val)

        if vtype == 'int':
            val = self._readai(nval)

        elif vtype == 'float':
            val = self._readaf(nval)

        elif vtype == 'double':
            val = self._readad(nval)

        elif vtype == 'bool':
            val = self._readab(nval)
        elif vtype == 'byte':
            val = self._readaby(nval)
            vtype = 'int'

        elif vtype == 'char':
            val = self._readac(nval)
            vtype = 'str'

        else:
            errstr = 'Unknown data type : ' + vtype
            raise ValueError(errstr)

        return (key, vtype, nval, val)

    def _readc(self):
        """Read next string up to terminating char, skip comments
        """

        end = ('\n', '\0')

        string = ''
        while True:
            cval = self._roff.read(1)
            if not cval:
                break
            try:
                cc = cval.decode(self._decode)
            except:
                errstr = 'Cannot decode character as ascii. Incorrect file format? ' + string
                raise ValueError(errstr)

            if cc in end:
                if string == '':
                    break
                elif self._iscomment(string):
                    string = ''
                else:
                    break
            else:
                string += cc

        return string

    def _iscomment(self, string):
        """Check if string is comment
        Args:
            string - string - to test as comment
        Returns:
            Logical, True if string is comment
        """
        return bool(string.startswith('#') and string.endswith('#'))

    def _readi(self):
        """Read next integer
        """
        cval = self._roff.read(4)
        val = struct.unpack(self._iform, cval)[0]
        return val

    def _readf(self):
        """Read next float
        """
        cval = self._roff.read(4)
        val = struct.unpack(self._fform, cval)[0]
        return val

    def _readd(self):
        """Read next double
        """
        cval = self._roff.read(8)
        val = struct.unpack(self._dform, cval)[0]
        return val

    def _readb(self):
        """Read next bool
        """
        cval = self._roff.read(1)
        val = struct.unpack('?', cval)[0]
        return val

    def _readby(self):
        """Read next byte
        """
        return self._roff.read(1)

    def _readac(self, nval):
        """Read array of nval strings
        Args:
            nval - int - number of values expected
        """
        val = []
        for itr in range(0, nval):
            cval = self._readc()
            val.append(cval)
        return val

    def _readai(self, nval):
        """Read array of nval ints
        Args:
            nval - int - number of values expected
        """
        val = []
        for itr in range(0, nval):
            cval = self._roff.read(4)
            itm = struct.unpack(self._iform, cval)[0]
            val.append(itm)
        return val

#    def _readaby(self, nval):
#        """
#        Read array of nval ints
#
#        Args:
#            nval - int - number of values expected
#
#        """
#        val = []
#        for itr in range(0, nval):
#            cval = self._roff.read(1)
#            val.append(cval)
#        return val

    def _readaf(self, nval):
        """Read array of nval floats
        Args:
            nval - int - number of values expected
        """
        val = []
        for itr in range(0, nval):
            cval = self._roff.read(4)
            itm = struct.unpack(self._fform, cval)[0]
            val.append(itm)
        return val

    def _readad(self, nval):
        """Read array of nval doubles
        Args:
            nval - int - number of values expected
        """
        val = []
        for itr in range(0, nval):
            cval = self._roff.read(8)
            itm = struct.unpack(self._dform, cval)[0]
            val.append(itm)

        return val

    def _readab(self, nval):
        """Read array of nval bools
        Args:
            nval - int - number of values expected
        """
        val = []
        for itr in range(0, nval):
            cval = self._roff.read(1)
            itm = struct.unpack('?', cval)[0]
            val.append(itm)
        return val

    def _readaby(self, nval):
        """Read array of nval bytes
        Args:
            nval - int - number of values expected
        """
        val = []
        for itr in range(0, nval):
            bval = self._roff.read(1)
            kval = int.from_bytes(bval, byteorder=sys.byteorder)
            #k  = struct.unpack('>H',  b'\x00' + bval)[0]
            val.append(kval)

        return val

    def _byteswaptest(self):
        """Read next integer, test for byteswap
        """

        cval = self._roff.read(4)
        val1 = struct.unpack('>i', cval)[0]
        val2 = struct.unpack('<i', cval)[0]
        if val1 == 1:
            self._iform = '>i'
            self._fform = '>f'
            self._dform = '>d'
            typ = 'Big endiand'

        elif val2 == 1:
            self._iform = '<i'
            self._fform = '<f'
            self._dform = '<d'
            typ = 'Little endian'
        else:
            typ = 'xxx'
            errstr = 'Byte-swap test failed ' + str(val1) + ' ' + str(val2)
            raise ValueError(errstr)

        return typ
