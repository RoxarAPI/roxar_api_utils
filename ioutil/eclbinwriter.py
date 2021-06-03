import struct
import sys

from .padblanc8 import padblanc8

class EclBinWriter:
    """Base class for writing Eclipse binary file
    Args:
        binfile: File pointer for binary file opened for write
        errfile: Optional file pointer for file opened for error messages.  Default standard output.
    Note:
        Endian check included for windows/linux.
    """

    def __init__(self, binfile, errfile=None):

        self._binfile = binfile

        if errfile is None:
            errfile = sys.stdout
        self._errfile = errfile

# Always big endian for Eclipse
        self._iform = '>i'
        self._fform = '>f'
        self._dform = '>d'

# Block size for writing
        self._blki = 1000
        self._blkf = 1000
        self._blkd = 1000
        self._blkq = 1000
        self._blkc = 105

    def write_key(self, key, nval, ktype):
        """Write keyword line to file.
        Args:
            key (char): Keyword
            ktype (char): Keyword ktype (int, float, doub, ...)
            nval (int): Number of data values in keyword
        Note:
            No check on character length
        """

        try:
            skey = padblanc8(key)
            self._binfile.write(struct.pack(self._iform, 16))
            self._binfile.write(skey.encode('ascii'))
            self._binfile.write(struct.pack(self._iform, nval))
            self._binfile.write(ktype.encode('ascii'))
            self._binfile.write(struct.pack(self._iform, 16))
        except:
            errstr = 'Cannot write keyword ' + key
            raise IOError(errstr)

        return None

    def write_data(self, key, dval, nval, ktype):
        """Write data items to file
        Args:
            nval: Values to be read
        Returns:
            List of nval string items
        Note:
            No check on character length
        """

        if nval < 0:
            errstr = 'Incorrect number of data items ' + str(nval) + ' for keyword ' + key
            raise ValueError(errstr)

        try:
            if ktype == 'CHAR':
                blength = self._blkc

                nblk = int(nval/blength)
                if nblk*blength < nval:
                    nblk = nblk + 1
                for ib in range(0, nblk):
                    ibeg = ib*blength
                    iend = min(ibeg + blength, nval)
                    nv = iend - ibeg
                    self._binfile.write(struct.pack(self._iform, nv*8))
                    for iv in range(nv):
                        self._binfile.write(dval[ibeg+iv].encode('ascii'))
                    self._binfile.write(struct.pack(self._iform, nv*8))

            elif ktype == 'INTE':
                blength = self._blki

                nblk = int(nval/blength)
                if nblk*blength < nval:
                    nblk = nblk + 1
                for ib in range(0, nblk):
                    ibeg = ib*blength
                    iend = min(ibeg + blength, nval)
                    nv = iend - ibeg
                    self._binfile.write(struct.pack(self._iform, nv*4))
                    for iv in range(nv):
                        self._binfile.write(struct.pack(self._iform, dval[ibeg+iv]))
                    self._binfile.write(struct.pack(self._iform, nv*4))

            elif ktype == 'REAL':
                blength = self._blkf

                nblk = int(nval/blength)
                if nblk*blength < nval:
                    nblk = nblk + 1
                for ib in range(0, nblk):
                    ibeg = ib*blength
                    iend = min(ibeg + blength, nval)
                    nv = iend - ibeg
                    self._binfile.write(struct.pack(self._iform, nv*4))
                    for iv in range(nv):
                        self._binfile.write(struct.pack(self._fform, dval[ibeg+iv]))
                    self._binfile.write(struct.pack(self._iform, nv*4))

            elif ktype == 'DOUB':
                blength = self._blkd

                nblk = int(nval/blength)
                if nblk*blength < nval:
                    nblk = nblk + 1
                for ib in range(0, nblk):
                    ibeg = ib*blength
                    iend = min(ibeg + blength, nval)
                    nv = iend - ibeg
                    self._binfile.write(struct.pack(self._iform, nv*8))
                    for iv in range(nv):
                        self._binfile.write(struct.pack(self._dform, dval[ibeg+iv]))
                    self._binfile.write(struct.pack(self._iform, nv*8))
            elif ktype == 'LOGI':
                blength = self._blkq

                nblk = int(nval/blength)
                if nblk*blength < nval:
                    nblk = nblk + 1
                for ib in range(0, nblk):
                    ibeg = ib*blength
                    iend = min(ibeg + blength, nval)
                    nv = iend - ibeg
                    self._binfile.write(struct.pack(self._iform, nv*4))
                    for iv in range(nv):
                        lval = 0
                        if dval[ibeg+iv]:
                            lval = 1
                        self._binfile.write(struct.pack(self._iform, lval))
                    self._binfile.write(struct.pack(self._iform, nv*4))

            elif ktype == 'MESS':
                pass
            else:
                errstr = 'Incorrect data ktype ' + ktype + ' for keyword ' + key
                raise ValueError(errstr)

        except:
            errstr = 'Cannot write data for keyword ' + key
            raise IOError(errstr)

        return None
