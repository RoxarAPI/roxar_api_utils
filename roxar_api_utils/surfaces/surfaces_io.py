import sys

import numpy as np

import roxar

class RoxarSurfReader:
    """"Reader for Roxar surfaces
    Args:
        filename (str): Roxar suface data file name
        errfile (file pointer): Open file for error messages, standard output if None
    """
    def __init__(self, infile, errfile=None):
        self._filename = infile
        if errfile is None:
            self._errfile = sys.stdout
        else:
            self._errfile = errfile

        try:
            self._infile = open(infile, 'rb')
        except OSError as e:
            print('\nFatal error:  Cannot open file', infile, '\n', file=self._errfile)
            raise OSError(e)

        # check if it is a binary file read the 2 int if -996 then it is binary file
        rec = np.fromfile(self._infile, dtype='>i4,>i4', count=1)
        if rec[0][1] == -996:
            self._is_binary = True
        else:
            self._is_binary = False
        self._infile.close()


    def _read_roxar_binary(self):
        """Read the Roxar surface binary file
        Returns:
            RegularGrid2d or none
        """

        try:
            self._infile = open(self._filename, 'rb')
        except OSError as e:
            print('\nFatal error:  Cannot open file', self._filename, '\n', file=self._errfile)
            raise OSError(e)

        try:
            finn = self._infile
            # read first segment of data
            # dtype allows you to specify how to parse the data coming in
            # f4 indicates one float value, taking up 4 bytes (float32)
            # > indicates to convert the bytes from 'big-endian' format into 'little-endian'
            # 6>f4 indicates to create a subarray with 6 elements of the above format
            rec = np.fromfile(finn, dtype='>i4, >i4, >i4, 6>f4, >i4', count=1)
            if rec[0][1] != -996:
                print(
                    '\nFatal error: File has incorrect flag',
                    self._infile, '\n',
                    file=self._errfile)
                return None

            # get the number of data rows and statistics on the data
            nrow = rec[0][2]
            xmin = rec[0][3][0]
            xmax = rec[0][3][1]
            ymin = rec[0][3][2]
            ymax = rec[0][3][3]
            xinc = rec[0][3][4]
            yinc = rec[0][3][5]

            # read next segment to get rotation angle and other info
            # i4 indicates one int value, taking up 4 bytes (int32)
            rec = np.fromfile(finn, dtype='>i4, >i4, 3>f4, >i4', count=1)
            ncol = rec[0][1]
            if ncol <= 0 or nrow <= 0:
                print(
                    '\nFatal error: Rows or columns less than 0',
                    self._infile,
                    '\n',
                    file=self._errfile)
                return None

            rotoangle = rec[0][2][0]
            rotox = rec[0][2][1]
            rotoy = rec[0][2][2]

            # read segment and discard
            rec = np.fromfile(finn, dtype='>i4, 7>i4, >i4', count=1)

            # create an empty masked array with the right number or rows and cols
            # 'f8' is float64 (float of 8 bytes in size)
            #  < indicates that the array created will have bytes order of little-endian
            data = np.ma.empty((nrow, ncol), '<f8')

            # create a format to be used for each row
            fmt = '>i4, %d>f4, >i4' % ncol

            # for as many rows as were specified in the data,
            #     read each segment
            #     it should match the above format
            #     place the data into an array
            for i in range(nrow):
                rec = np.fromfile(finn, dtype=fmt, count=1)
                data[i] = rec[0][1]

            # transpose the axes of the array so that what is in the first axis gets
            # ordered on the 2nd axis, and vice versa
            # the file was read by rows, but the array needs rows in the 2nd axis
            data_tr = np.ma.transpose(data)

            # create a Roxar API Regular Grid 2D to store the data in
            grid = roxar.RegularGrid2D.create(
                float(xmin),
                float(ymin),
                float(xinc),
                float(yinc),
                int(ncol),
                int(nrow),
                float(rotoangle))

            # create a new array which is masked for values greater than 1e+30
            data_tr = np.ma.masked_where(data_tr >= 1e+30, data_tr)

            # set the mask manually, if not already set (necessary for API 1.0)
            if type(data_tr.mask) == np.bool_:
                m = np.zeros(data.size)
                ma = np.ma.make_mask(m, shrink=False)
                data_tr.mask = ma
            grid.set_values(data_tr)
            return grid
        finally:
            self._infile.close()

    def _read_roxar_text(self):
        """Read the Roxar surface text file
        Returns:
            RegularGrid2d or None
        """
        self._infile = open(self._filename, 'r')
        try:
            finn = self._infile

            line = finn.readline()
            cols = line.split()

            if cols[0] != '-996':
                print(
                    '\nFatal error: File has incorrect flag',
                    self._infile,
                    '\n',
                    file=self._errfile)
                return None
            nrow = int(cols[1])
            xinc = cols[2]
            yinc = cols[3]

            line = finn.readline()
            cols = line.split()
            xmin = cols[0]
            ymin = cols[2]

            line = finn.readline()
            cols = line.split()
            ncol = int(cols[0])
            rotoangle = cols[1]

            if ncol <= 0 or nrow <= 0:
                print(
                    '\nFatal error: Rows or columns less than 0',
                    self._infile,
                    '\n',
                    file=self._errfile)
                return None

            line = finn.readline() # nothing is used in this line old annotations stuff from IrapClassic

            # read the rest of the file is the data
            data = np.fromfile(finn, dtype=np.float64, sep=' ')
            data_tr = np.ma.reshape(data, (ncol, nrow), order='F')
            data_tr = np.ma.masked_where(data_tr >= 9999900.0, data_tr)

            # create a Roxar API Regular Grid 2D to store the data in
            grid = roxar.RegularGrid2D.create(
                float(xmin),
                float(ymin),
                float(xinc),
                float(yinc),
                int(ncol),
                int(nrow),
                float(rotoangle))

            # set the mask manually, if it is not already set
            if type(data_tr.mask) == np.bool_:
                m = np.zeros(data.size)
                ma = np.ma.make_mask(m, shrink=False)
                data_tr.mask = ma
            grid.set_values(data_tr)
            return grid
        finally:
            self._infile.close()

    def read_roxar(self):
        """Read Roxar surface in text or binary format
        Return
            RegularSurface2D or None
        """

        if self._is_binary:
            return self._read_roxar_binary()
        else:
            return self._read_roxar_text()


def read_roxar_surface(infile, errfile=None):
    """Read Roxar surface file.
    Args:
        infile (str): Input file name
        errfile (file pointer): Open error file
    Returns:
        RegularGrid2D if OK, else None
    Note:
        The software fill find out if the input file
        is a text or binary file
    """

    if errfile is None:
        errfile = sys.stdout

    reader = RoxarSurfReader(infile, errfile)
    return reader.read_roxar()
