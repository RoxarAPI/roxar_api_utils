"""
Reader for keyword-based data file of ECLIPSE type

Updated June 14, 2016

"""

import collections
import sys
import os

# ========================================================================================
# TEXT READER CLASS
# ========================================================================================

class KeyDataReader:
    """Base class keyword reader

    Args:
        filename: String with data file name
        errfile: File pointer for output of error messages

    """

    def __init__(self, infile, errfile=None):

# Settings for error handling:

        if errfile is None:
            errfile = sys.stdout
        self._errfile = errfile
        self._ok = True
        self._erritm = ''
        self._errors = 0
        self._warnings = 0

# Settings for current input file:
        self._currentname = infile
        self._currentline = 0
        try:
            self._currentfile = open(infile, 'r')
        except OSError as e:
            print('\nFatal error:  Cannot open file ', infile, '\n', file=self._errfile)
            raise OSError(e)

# Settings for all input files:
        self._incdepth = 0
        self._filenames = [infile]
        self._files = [self._currentfile]
        self._linenos = [0]

# Settings for reading queue
        self._currentkey = ''
        self._qlength = 0
        self._que = collections.deque()
        self._slash = False

    def _get_current_key(self):
        return self._currentkey

    current_key = property(_get_current_key, doc='Get current keyword read')

    def _get_read_slash(self):
        return self._slash

    def _set_read_slash(self, slash):
        self._slash = slash
        return None

# Dulicate name, do not use
    has_read_slash = property(_get_read_slash, _set_read_slash, doc='Get/set flag for slash read')

    def _get_isok(self):
        return self._ok

    def _set_isok(self, is_ok=True):
        self._ok = is_ok
        return None

    isok = property(_get_isok, _set_isok, doc='Flag for reading ok')


    def _ignore_hyp(self, tval):
        """Replace text within hyphens with white space

        """

        tout = tval
        while True:
            ic = tout.find("\'")
            if ic >= 0:
                t2 = tout[ic+1:]
                ic2 = t2.find("\'")
                if ic2 >= 0:
                    ic2 = ic2 + 2
                    ic3 = ic + ic2
                    sub = tout[ic:ic3]
                    repl = ic2*' '
                    tout = tout.replace(sub, repl)
                else:
                    break
            else:
                break

        return tout


    def _nextline(self):
        """
        Returns next line from current file.

        Returns:
            tuple - data items in next line read

        Note:
            Strips comments. Strips text after slash. Strip blanks inside of quotation marks.

        """

        read = True
        while read:
            line = self._currentfile.readline()
            if not line:
                return None

            self._currentline += 1

# Remove comments
            temp = line.strip()
# Ignore text inside hyphens
            temp2 = self._ignore_hyp(temp)
            ic = temp2.find('--')
            isl = temp2.find('/')
            if temp == '':
                read = True
            elif ic == 0:
                read = True
            elif isl >= 0:
                temp = temp[0:isl+1]
                read = False
            elif ic > 0:
                ic -= 1
                temp = temp[0:ic]
                read = False
            else:
                read = False

# Split line in terms

        terms = []
        while True:
            t, temp = self._linsplit(temp)
            if t is None:
                break
            else:
                terms.append(t)

        return terms

    def _linsplit(self, line):
        """
        Return first term in line based on blanks,  commas, quotations

        """

        line = line.lstrip()
        line = line.lstrip(',')
        leng = len(line)
        item = None
        rest = ''

        if leng == 0:
            return (item, rest)

        il1 = line.find("\'")

        if il1 == 0:
            linred = line[1:]
            il2 = linred.find("\'")
            if il2 >= 0:
                item = line[0:il2+2]
                if il2+2 < leng:
                    rest = line[il2+3:]

            else:
                errstr = 'Missing quotation mark'
                self.writeerror(errstr)

        else:
            tmp = line.replace(',', ' ')
            il2 = tmp.find(' ')
            terms = tmp.split()
            item = terms[0]
            if il2 > 0:
                rest = line[il2+1:]

        return (item, rest)


    def _nextitem(self):
        """
        Return next data item from queue and maintain queue

        Returns:
            string - next data item

        """

        if self._qlength == 0:
            terms = self._nextline()
            if terms is None:
                return None

            for it in terms:
                if it.startswith("\'") and it.endswith("\'"):
                    endslash = False
                else:
                    isl = it.find('/')
                    if isl > 0:
                        endslash = True
                        it = it.strip('/')
                    else:
                        endslash = False

                if it.startswith("\'") and it.endswith("\'"):
                    iast = -1
                else:
                    iast = it.find('*')
                    lit = len(it)

                if iast >= 0:
                    if it == '*':
                        self._que.append(it)
                    elif iast == 0:
                        self.writeerror('Incorrect use of repeated count')
                    else:
                        try:
                            itm = it[0:iast]
                            rep = int(itm)
                        except ValueError:
                            errstr = 'Incorrect format for repeated count: ' + itm + '*'
                            self.writeerror(errstr)
                            rep = 0
                        except IOError:
                            self.writeerror('IO error')
                            rep = 0

                        if iast == lit-1:
                            itm = '*'
                        else:
                            itm = it[iast+1:]

                        if rep > 0:
                            for kitr in range(0, rep):
                                self._que.append(itm)

                else:
                    self._que.append(it)

                if endslash:
                    self._que.append('/')

            self._qlength = len(self._que)

        item = self._que.popleft()
        self._qlength -= 1
        return item


    def _qflush(self):
        """
        Flush reading queue, ignoring all remaining data on line

        """

        self._que.clear()
        self._qlength = 0
        return None


    def nextkey(self):
        """
        Returns next keyword.  Handles include files.

        Returns:
            Keyword as string

        """

        is_ok = True
        while is_ok:
            key = self._nextitem()
            if key is not None:
                key = key.upper()
            self._currentkey = key
            self._qflush()

            if key is not None:

                if key == 'INCLUDE':
                    name = self.readstr()
                    oname = name
                    if name is not None:
                        inc = self._incdepth
                        if inc == 2:
                            raise IOError('Too many INCLUDE levels')

                        slash = self._nextitem()
                        if slash != '/':
                            self.writeerror('Missing slash')

                        if not os.path.isabs(name):
                            folder = os.path.dirname(self._currentname)
                            name = os.path.join(folder, name)

                        try:
                            self._currentfile = open(name, 'r')
                        except OSError as e:
                            errstr = 'Cannot open INCLUDE file ' + oname + '\n' + str(e)
                            self.writeerror(errstr)

                        self._linenos[inc] = self._currentline
                        self._currentline = 0

                        self._incdepth += 1
                        self._currentname = name
                        self._filenames.append(name)
                        self._files.append(self._currentfile)
                        self._linenos.append(0)

                    else:
                        print('Unexpected end-of-file following keyword INCLUDE',
                              file=self._errfile)
                        raise ValueError()

                elif key == 'ENDINC':
                    self._currentfile.close()
                    if self._incdepth == 0:
                        return None
                    else:
                        inc = self._incdepth
                        del self._filenames[inc]
                        del self._files[inc]
                        del self._linenos[inc]

                        inc -= 1
                        self._incdepth = inc
                        self._currentline = self._linenos[inc]
                        self._currentfile = self._files[inc]
                        self._currentname = self._filenames[inc]

                elif key == '/':
                    pass

                else:
                    return key

            else:
                self._currentfile.close()
                if self._incdepth == 0:
                    return None
                else:
                    inc = self._incdepth
                    del self._filenames[inc]
                    del self._files[inc]
                    del self._linenos[inc]

                    inc -= 1
                    self._incdepth = inc
                    self._currentline = self._linenos[inc]
                    self._currentfile = self._files[inc]
                    self._currentname = self._filenames[inc]

        return None


    def readslash(self):
        """
        Read data up to next slash, and ignore all data read.

        Returns:
            True if slash found

        """

        if self._slash:
            self._slash = False
            return True

        while True:
            itm = self._nextitem()
            if itm is None:
                self.writeerror('Missing slash')
                return False
            elif itm == '/':
                self._slash = False
                return True


    def readfloat(self, default=None):
        """
        Read float value from input stream.

        Args:
            default: Float default value

        Returns:
            Float value read

        """

        if self._slash:
            if default is None:
                default = 0.
            return default

        val = 0.

        try:

            item = self._nextitem()
            if item == '*':
                if default is not None:
                    val = default
                else:
                    self.writeerror('No default value defined')

            elif item == '/':
                self._slash = True
                if default is not None:
                    val = default
                else:
                    self.writeerror('Missing value(s)')

            else:
                val = float(item)

        except ValueError:
            errstr = 'Expected float, reading ' + str(item)
            self.writeerror(errstr)

        return val


    def readfloata(self, nval):
        """
        Read array of float values from input stream

        Args:
            nval: Number of values(int)

        Returns:
            List of float values read

        Note:
            No defaults given

        """

        val = []
        try:
            if nval > 0:
                for it in range(0, nval):
                    itm = self.readfloat()
                    val.append(itm)
        except ValueError as e:
            self.writeerror()
            raise ValueError(e)

        return val



    def readint(self, default=None):
        """Read single integer value from input stream

        Args:
            default: Integer default value

        Returns:
            Integer value read

        """

        if self._slash:
            if default is None:
                default = 0
            return default

        val = 0

        try:
            item = self._nextitem()
            if item == '*':
                if default is not None:
                    val = default
                else:
                    self.writeerror('No default value defined')

            elif item == '/':
                self._slash = True
                if default is not None:
                    val = default
                else:
                    self.writeerror('Missing value')

            else:
                val = int(item)

        except ValueError:
            errstr = 'Expected integer, reading ' + str(item)
            self.writeerror(errstr)

        return val


    def readinta(self, nval):
        """
        Read array of integers value from input stream

        Args:
            nval: Number of values(int)

        Returns:
            List of integer values read

        Note:
            No defaults given

        """

        val = []
        try:
            if nval > 0:
                for it in range(0, nval):
                    itm = self.readint()
                    val.append(itm)
        except ValueError as e:
            self.writeerror()
            raise ValueError(e)

        return val


    def readstr(self, default=None):
        """
        Read string value from input stream

        Args:
            default: String default value

        Returns:
            String read

        """

        if self._slash:
            if default is None:
                default = ''
            return default

        val = ''

        try:

            item = self._nextitem()
            if item == '*':
                if default is not None:
                    val = default
                else:
                    self.writeerror('No default value defined')

            elif item == '/':
                self._slash = True
                if default is not None:
                    val = default
                else:
                    self.writeerror('Missing value')

            else:
                val = item

        except ValueError:
            errstr = 'Expected string, reading ' + item
            self.writeerror(errstr)

        val = val.strip("\'")
        val = val.lstrip()
        val = val.rstrip()
        return val

    def readstru(self, default=None):
        """
        Read string from input stream and return in uppercase

        Args:
            default: String default value

        Returns:
            String read, in uppercase

        """

        val = self.readstr(default)
        return val.upper()

    def readyesno(self, default=None):
        """
        Read string from input stream and check if yes or no.

        Args:
            default: String default value

        Returns:
            True if YES

        """

        tyes = ('YES', 'Y')
        tno = ('NO', 'N')

        val = self.readstru(default)
        if val in tyes:
            isyes = True
        elif val in tno:
            isyes = False
        else:
            errstr = 'Expected YES or NO, but found ' + val
            self.writeerror(errstr)
            isyes = False

        return isyes

    def readlogi(self, default=None):
        """
        Read boolean value from input stream

        Args:
            default:  Default boolean value True/False

        Returns:
            Boolean value read.

        """

        if self._slash:
            if default is None:
                default = False
            return default

        val = False

        try:
            item = self._nextitem()
            if item == '*':
                if default is not None:
                    val = default
                else:
                    self.writeerror('No default value defined')

            elif item == '/':
                self._slash = True
                if default is not None:
                    val = default
                else:
                    self.writeerror('Missing value')

            else:
                if item is None:
                    val = default
                elif item == 'F':
                    val = False
                elif item == 'T':
                    val = True
                else:
                    print('Expected logical value, reading ', item)

        except ValueError as e:
            print('Expected string, reading ', item)
            raise ValueError(e)

        return val

    def readrptkey(self, default=None):
        """
        Read mnemonic in Eclipse keywords RPT..., of type 'BASIC=4'

        Args:
            default: Default string

        Returns:
            Tuple with total mnemonic, sub-keyword (e.g BASIC), and numeric parameter.

        """

        item = self.readstr(default)
        if item == default:
            return (item, default, None)

        item.strip("\'")

        il = item.find('=')
        if il < 0:
            key = item
            ival = None
        else:
            terms = item.split('=')
            if len(terms) == 2:
                key = terms[0]
                ival = int(terms[1])
            else:
                errstr = 'Incorrect sub-keyword found: ' + item
                raise ValueError(errstr)

        return (item, key, ival)


    def ignoreto(self, keyword):
        """
        Ignore keywords up to and included input keyword, assumed to be found in main input file.

        Args:
            keyword: String with keyword starting reading, e.g., SCHEDULE.

        Returns:
            True if keyword found, else False

        Note:
            Input keyword is assumed to have no associated data.

        """

        while True:
            terms = self._nextline()
            if terms is None:
                errstr = 'Keyword ' + keyword + ' not found.'
                self._currentkey = ''
                self.writeerror(errstr)
                return False

            else:
                if terms[0] == keyword:
                    return True

        return False


    def writeerror(self, string=None):
        """
        Write error message with location info.

        Args:
            string:  Error message.

        """

        key = self._currentkey
        if len(key) == 0:
            sloc = (
                'Occured in\nFile   : '
                + self._currentname
                + '\nLine no: '
                + str(self._currentline))
        else:
            sloc = (
                'Occured in keyword: '
                + key + '\nFile   : '
                + self._currentname
                + '\nLine no: '
                + str(self._currentline))

        first = self._errors + self._warnings
        if first == 0:
            print(file=self._errfile)

        if string is not None:
            print('Error: ', string, file=self._errfile)
        else:
            print('Error reading: ', file=self._errfile)

        print(sloc, '\n', file=self._errfile)

        self._ok = False
        self._errors += 1

#       raise ValueError(string)

        return None


    def writewarning(self, string=None):
        """
        Write warning message with location info.

        Args:
            string: Warning message

        """

        key = self._currentkey
        if len(key) == 0:
            sloc = (
                'Occured in\nFile   : '
                + self._currentname
                + '\nLine no: '
                + str(self._currentline))
        else:
            sloc = (
                'Occured in keyword: '
                + key + '\nFile   : '
                + self._currentname
                + '\nLine no: '
                + str(self._currentline))

        first = self._errors + self._warnings
        if first == 0:
            print(file=self._errfile)

        if string is not None:
            print('Warning: ', string, file=self._errfile)
        else:
            print('Warning reading: ', file=self._errfile)

        print(sloc, '\n', file=self._errfile)

# Cut if too many warnings:

        self._warnings += 1
        if self._warnings > 100:
            self._ok = False

        return None


    def fine(self):
        """
        Perform final clean up after reading.

        """

        for fil in self._files:
            fil.close()

        print(' ', file=self._errfile)
        if self._errors > 0:
            print('Errors found:   ', self._errors)
        if self._warnings > 0:
            print('Warnings found: ', self._warnings)
        if self._errors > 0 or self._warnings > 0:
            print(file=self._errfile)

        return None
