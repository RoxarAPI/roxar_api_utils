import sys
from datetime import datetime

import roxar_api_utils.ioutil
from .profiles import Profiles

def _pad8(array):
    """Make string array 8 character wide
    """

    new = []
    for ar in array:
        new.append(roxar_api_utils.ioutil.padblanc8(ar))

    return new

def _file_name(fileroot, no):
    """Define file name from number
    """
    if no < 10:
        filename = fileroot + '.S000' + str(no)
    elif no < 100:
        filename = fileroot + '.S00' + str(no)
    elif no < 1000:
        filename = fileroot + '.S0' + str(no)
    else:
        filename = fileroot + '.S' + str(no)
    return filename

class EclSummaryReader:
    """Reader for Eclipse binary SMSPEC file and non-unified Summary files
    Args:
        fileroot (str):  File root for reading
        errfile (file pointer): Optional opened file for error output, sys output if None
    """

    def __init__(self, fileroot, errfile=None):

        self._fileroot = fileroot
        if errfile is None:
            self._errfile = sys.stdout
        else:
            self._errfile = errfile

        filename = fileroot + '.SMSPEC'
        try:
            self._binfile = open(filename, 'rb')
        except OSError as e:
            print('\nFatal error:  Cannot open file ', filename, '\n', file=self._errfile)
            raise OSError(e)

        self._nokeys = 0
        self._nosteps = 0
        self._nofiles = 0
        self._profiles = None

    def _get_nokeys(self):
        """Get number of keys read
        """

        return self._nokeys

    def _get_nosteps(self):
        """Get number of time steps read
        """

        return self._nosteps

    def _get_nofiles(self):
        """Get number of files read
        """

        return self._nofiles


    nokeys = property(_get_nokeys, doc='Get no of Profiles vectors read')
    nosteps = property(_get_nosteps, doc='Get no of time steps read')
    nofiles = property(_get_nosteps, doc='Get no of files read')

    def read_spec(self):
        """Read ECLIPSE SMSPEC file
        Returns:
            Profiles class
        """

        binreader = roxar_api_utils.ioutil.EclBinReader(self._binfile, self._errfile)

        keywords = []
        names = []
        nums = []
        units = []
        griddim = (1, 1, 1)
        startdate = datetime(1900, 1, 1, 0, 0, 0)

        while True:
            re = binreader.readnextkey()
            if re is None:
                del binreader
                self._binfile.close()
                self._profiles = Profiles(
                    self._fileroot, keywords, names, nums, units, startdate, griddim)
                return self._profiles

            key, nval, vtype, item = re
#           print(key, nval, vtype)

            if   key == 'DIMENS  ':
                self._nokeys = item[0]
                griddim = (item[1], item[2], item[3])
            elif key == 'KEYWORDS':
                keywords = item
            elif key == 'WGNAMES ':
                names = item
            elif key == 'NUMS    ':
                nums = item
            elif key == 'UNITS   ':
                units = item
            elif key == 'STARTDAT':
                if nval == 3:
                    startdate = datetime(item[2], item[1], item[0], 0, 0, 0)
                else:
                    startdate = datetime(item[2], item[1], item[0], item[3], item[4], item[5])

            del item

        return None

    def read_summary(self):
        """Read ECLIPSE Summary files
        Returns:
            Profiles class
        """

        found = False

# Try unified first, then non-unified

        try:
            filename = self._fileroot + '.UNSMRY'
            self._binfile = open(filename, 'rb')
            binreader = roxar_api_utils.ioutil.EclBinReader(self._binfile, self._errfile)
            self._read_sum(binreader)
        except OSError:
            for fileno in range(1, 10000):
                filename = _file_name(self._fileroot, fileno)
                try:
                    self._binfile = open(filename, 'rb')
                    self._nofiles += 1
#                   print('Reading file ', self._nofiles)
                except OSError as e:
                    if not found:
                        print(
                            '\nFatal error:  Cannot open file ',
                            filename,
                            '\n',
                            file=self._errfile)
                        raise OSError(e)
                    else:
                        return self._profiles

                found = True
                binreader = roxar_api_utils.ioutil.EclBinReader(self._binfile, self._errfile)
                self._read_sum(binreader)

        return self._profiles

    def _read_sum(self, binreader):
        """Read single Summary file
        """

        while True:
            re = binreader.readnextkey()
            if re is None:
                del binreader
                self._binfile.close()
                break

            key, nval, type, item = re
#           print(fileno, key, nval, type)

            if   key == 'SEQHDR  ':
                pass
            elif key == 'MINISTEP':
                pass
            elif key == 'PARAMS  ':
                self._profiles.append_tstep(item)
                self._nosteps += 1
#               print('Reading time step ', self._nosteps)

        return None


class EclSummaryWriter:
    """Write SMSPEC and (non-unified) Summary files
    Args:
        profiles (Profiles):  Stored Profiles data set
        fileroot (str):  File root for output file
        errfile (file pointer): Optional file pointer to output error file, sys output if None
        unified (bool): True if unified Summary files should be written
    """

    def __init__(self, profiles, fileroot, errfile=None, unified=False):

        self._profiles = profiles
        self._fileroot = fileroot

        if errfile is None:
            self._errfile = sys.stdout
        else:
            self._errfile = errfile

        self._unified = unified

    def write_spec(self):
        """Write ECLIPSE SMSPEC file
        """

        filename = self._fileroot + '.SMSPEC'
        try:
            fp = open(filename, 'wb')
        except OSError as e:
            errstr = 'Cannot open SMSPEC file: ' + filename + '\n' + str(e)
            raise OSError(errstr)

        eclwriter = roxar_api_utils.ioutil.EclBinWriter(fp)
        profiles = self._profiles

        nx, ny, nz = profiles.griddim
        sd = profiles.startdate
        startdate = (sd.day, sd.month, sd.year, sd.hour, sd.minute, sd.second)

        nokeys = profiles.nokeys

        skey = 'RESTART'
        nval = 9
        styp = 'CHAR'
        restart = []
        for i in range(nval):
            restart.append('        ')
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, restart, nval, styp)

        skey = 'DIMENS'
        nval = 6
        styp = 'INTE'
        dimens = []
        dimens.append(nokeys)
        dimens.append(nx)
        dimens.append(ny)
        dimens.append(nz)
        dimens.append(0)    # Dummy, not used
        dimens.append(-1)   # Restart number
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, dimens, nval, styp)

        skey = 'KEYWORDS'
        nval = nokeys
        styp = 'CHAR'
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, _pad8(profiles.keywords), nval, styp)

        skey = 'WGNAMES'
        nval = nokeys
        styp = 'CHAR'
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, _pad8(profiles.names), nval, styp)

        skey = 'NUMS'
        nval = nokeys
        styp = 'INTE'
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, profiles.nums, nval, styp)

        skey = 'UNITS'
        nval = nokeys
        styp = 'CHAR'
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, _pad8(profiles.units), nval, styp)

        skey = 'STARTDAT'
        nval = 6
        styp = 'INTE'
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, startdate, nval, styp)

        fp.close()
        del eclwriter

        return None

    def write_summary_step(self, istep, tdata, nokeys, fp, fileno, eclwriter):
        """Write single time step to summary files
        Args:
            istep (int):  Time step number
            tdat (list of floats): Data
            nokeys (int): Number of summary keys
            froot (str): Summary file root
            fp (file pointer): Summary file
            fileno (int): File numer currently used
            eclwriter (EclBinWriter): Writer class
        """

        steps_per_file = 200

        qopen = False
        if self._unified:
            if fileno == 0:
                qopen = True
        else:
            if fileno > 0:
                idiff = istep - (fileno-1)*steps_per_file
                if idiff == steps_per_file + 1:
                    fp.close()
                    del eclwriter
                    qopen = True
            else:
                qopen = True

        if qopen:
            if self._unified:
                fileno = 1
                filename = self._fileroot + '.UNSMRY'
            else:
                fileno = fileno + 1
                filename = _file_name(self._fileroot, fileno)
            fp = open(filename, 'wb')
            eclwriter = roxar_api_utils.ioutil.EclBinWriter(fp)

            skey = 'SEQHDR'
            nval = 1
            styp = 'INTE'
            sqdat = [-1]
            eclwriter.write_key(skey, nval, styp)
            eclwriter.write_data(skey, sqdat, nval, styp)

        skey = 'MINISTEP'
        nval = 1
        styp = 'INTE'
        eclwriter.write_key(skey, nval, styp)
        stepdat = [istep]
        eclwriter.write_data(skey, stepdat, nval, styp)

        skey = 'PARAMS'
        nval = nokeys
        styp = 'REAL'
        eclwriter.write_key(skey, nval, styp)
        eclwriter.write_data(skey, tdata, nval, styp)

        return (fp, fileno, eclwriter)

    def write_summary(self):
        """Write summary files
        """

        profiles = self._profiles
        nosteps = self._profiles.nosteps
        nokeys = self._profiles.nokeys

        fp = None
        fileno = 0
        eclwriter = None
        istep = 0
        for istep in range(nosteps):
            tdata = profiles.get_step(istep)
            fp, fileno, eclwriter = self.write_summary_step(istep, tdata, nokeys, fp, fileno, eclwriter)

        return None
