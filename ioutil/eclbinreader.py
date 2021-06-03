import struct
import sys

class EclBinReader:
    """Base class for reading Eclipse binary file
    Args:
        binfile: File pointer for binary file opened for read
        errfile: Optional file pointer for file opened for error messages.  Default standard output.
    Note:
        Endian check included for windows/linux.
    """

    def __init__(self, binfile, errfile=None):

        self._binfile = binfile

        if errfile is None:
            errfile = sys.stdout
        self._errfile = errfile

# Format statement for endian reading

        cval = binfile.read(4)
        val1 = struct.unpack('>i', cval)[0]
        val2 = struct.unpack('<i', cval)[0]
        if val1 < 20:
            self._iform = '>i'
            self._fform = '>f'
            self._dform = '>d'

        elif val2 < 20:
            self._iform = '<i'
            self._fform = '<f'
            self._dform = '<d'

        else:
            errstr = 'Byte-swap test failed ' + str(val1) + ' ' + str(val2)
            raise ValueError(errstr)

# Go to first position in file again:
        binfile.seek(0)

# Block size for reading
        self._blki = 1000
        self._blkf = 1000
        self._blkd = 1000
        self._blkq = 1000
        self._blkc = 105

    def _read_nchar(self, nval):
        """Read nv characters from file
        Args:
            nv - int - Number of characters
        """
        item = ''
        for itr in range(0, nval):
            cval = self._binfile.read(1)
            if not cval:
                break
            try:
                ccc = cval.decode('ascii')
            except:
                errstr = 'Cannot decode character as ascii. Incorrect file format?'
                raise ValueError(errstr)

            item += ccc

        return item

    def readkey(self):
        """Read keyword line from file.
        Returns:
            Tuple with Eclipse keyword as string, number of data values, and data type.
        """

        cval = self._binfile.read(4)
        if not cval:
            return (None, None, None)

        key = self._read_nchar(8)

        cnval = self._binfile.read(4)
        nval = struct.unpack(self._iform, cnval)[0]

        ktype = self._read_nchar(4)

        self._binfile.read(4)

        return (key, nval, ktype)

    def readchar(self, nval):
        """Read multiple character items from file
        Args:
            nval: Values to be read
        Returns:
            List of nval string items
        """

        items = []
        ival = 0
        for itr in range(0, nval):
            if ival == 0:
                self._binfile.read(4)
            dat = self._read_nchar(8)
            items.append(dat)
            ival += 1
            if ival == self._blkc:
                self._binfile.read(4)
                ival = 0

        if ival > 0:
            self._binfile.read(4)

        return items

    def readint(self, nval):
        """Read multiple integer values from file
        Args:
            nval: Values to be read
        Returns:
            List of nval integers
        """

        items = []
        ival = 0
        for itr in range(0, nval):
            if ival == 0:
                self._binfile.read(4)
            cdat = self._binfile.read(4)
            dat = struct.unpack(self._iform, cdat)[0]
            items.append(dat)
            ival += 1
            if ival == self._blki:
                self._binfile.read(4)
                ival = 0

        if ival > 0:
            self._binfile.read(4)

        return items

    def readfloat(self, nval):
        """Read multiple float values from file
        Args:
            nval: Values to be read
        Returns:
            List of nval floats
        """

        items = []
        ival = 0
        for itr in range(0, nval):
            if ival == 0:
                self._binfile.read(4)
            cdat = self._binfile.read(4)
            dat = struct.unpack(self._fform, cdat)[0]
            items.append(dat)
            ival += 1
            if ival == self._blkf:
                self._binfile.read(4)
                ival = 0

        if ival > 0:
            self._binfile.read(4)

        return items

    def readdouble(self, nval):
        """Read nval double values from file
        Args:
            nval: Values to be read
        Returns:
            List of nval doubles
        """

        items = []
        ival = 0
        for itr in range(0, nval):
            if ival == 0:
                self._binfile.read(4)
            cdat = self._binfile.read(8)
            dat = struct.unpack(self._dform, cdat)[0]
            items.append(dat)
            ival += 1
            if ival == self._blkd:
                self._binfile.read(4)
                ival = 0

        if ival > 0:
            self._binfile.read(4)

        return items

    def readlogi(self, nval):
        """Read nval boolean values from file
        Args:
            nval: Values to be read
        Returns:
            List of nval boolean values
        """

        items = []
        ival = 0
        for itr in range(0, nval):
            if ival == 0:
                self._binfile.read(4)
            cdat = self._binfile.read(4)
            dat = struct.unpack(self._iform, cdat)[0]
            if dat == 0:
                tdat = False
            else:
                tdat = True
            items.append(tdat)
            ival += 1
            if ival == self._blkq:
                self._binfile.read(4)
                ival = 0

        if ival > 0:
            self._binfile.read(4)

        return items

    def readnextkey(self):
        """Read data for next keyword
        Returns:
            Tuple with key, number of values, data type, and data list
        Raises:
            ValueError if incorrect data type found in file
        """

        key, nval, ktype = self.readkey()
        if not key:
            return None
#       print('string :', key, ' ', nval, ' ', ktype)
        if ktype == 'CHAR':
            item = self.readchar(nval)
        elif ktype == 'INTE':
            item = self.readint(nval)
        elif ktype == 'REAL':
            item = self.readfloat(nval)
        elif ktype == 'DOUB':
            item = self.readdouble(nval)
        elif ktype == 'LOGI':
            item = self.readlogi(nval)
        elif ktype == 'MESS':
            nval = 0
            item = None
        else:
            errstr = 'Incorrect data type found: ' + ktype + ', keyword ' + key
            raise ValueError(errstr)

        return (key, nval, ktype, item)

    def list_all(self, outfile=None):
        """List keywords in a binary ECLIPSE file
        Args:
            outfile (file pointer): Opened file for output
        Raises:
            ValueError if incorrect data type found in file
        """

        if outfile is None:
            outfile = sys.stdout

        while True:
            key, nval, ktype = self.readkey()
            if not key:
                return None
            print(key, nval, ktype, file=outfile)
            if ktype == 'CHAR':
                item = self.readchar(nval)
            elif ktype == 'INTE':
                item = self.readint(nval)
            elif ktype == 'REAL':
                item = self.readfloat(nval)
            elif ktype == 'DOUB':
                item = self.readdouble(nval)
            elif ktype == 'LOGI':
                item = self.readlogi(nval)
            elif ktype == 'MESS':
                nval = 0
                item = None
            else:
                errstr = 'Incorrect data type found: ' + ktype + ', keyword ' + key
                raise ValueError(errstr)

            del item

        return None

    def print_all(self, outfile=None):
        """Convert an Eclipse binary file to a text file
        Args:
            outfile (file pointer): Open file for output
        Raises:
            ValueError if incorrect data type found in file
        """

        if outfile is None:
            outfile = sys.stdout

        while True:
            key, nval, ktype = self.readkey()
            if not key:
                return None
#            print(key, nval, ktype)
            print(key, nval, ktype, file=outfile)
            if ktype == 'CHAR':
                item = self.readchar(nval)
            elif ktype == 'INTE':
                item = self.readint(nval)
            elif ktype == 'REAL':
                item = self.readfloat(nval)
            elif ktype == 'DOUB':
                item = self.readdouble(nval)
            elif ktype == 'LOGI':
                item = self.readlogi(nval)
            elif ktype == 'MESS':
                nval = 0
                item = None
            else:
                errstr = 'Incorrect data type found: ' + ktype + ', keyword ' + key
                raise ValueError(errstr)

            if nval > 0:
                ibeg = 0
                while ibeg < nval:
                    iend = min(ibeg + 10, nval)
                    for j in range(ibeg, iend):
                        print(item[j], '  ', end='', file=outfile)
                    ibeg = iend
                    print(file=outfile)

            del item

        return None
