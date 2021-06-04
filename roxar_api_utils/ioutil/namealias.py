import copy
from .line_split import line_split

class NameAlias():
    """Class for handling (well) name aliases
    Args:
        text_file (str):  File name for alias file
        alias_dict (dict): Dictionary with alias info
        aiasi_dict (dict): Dictionary with alias_inverse info
    """

    def __init__(self, text_file=None, alias_dict=None, aliasi_dict=None):

        if alias_dict is not None:
            adict = copy.deepcopy(alias_dict)
            adict = self._rm_whitespace(adict)
            if len(adict) > 0:
                self._alias = adict
                self._verify_unique()
                self._to_inverse()
            else:
                errmes = 'Empty alias dictionary'
                raise ValueError(errmes)
        elif aliasi_dict is not None:
            adict = copy.deepcopy(aliasi_dict)
            adict = self._rm_whitespace(adict)
            if len(adict) > 0:
                self._aliasi = adict
                self._from_inverse()
                self._verify_unique()
            else:
                errmes = 'Empty alias inverse dictionary'
                raise ValueError(errmes)

        elif text_file is not None:
            self.read_txt(text_file)
        else:
            self._alias = dict()

    def __iter__(self):
        for name in sorted(self._alias.keys()):
            yield (name, self._alias[name])

    def _to_inverse(self):
        self._aliasi = dict()
        for k in self._alias.keys():
            self._aliasi[self._alias[k]] = k

    def _rm_whitespace(self, al):
        rmset = set()
        for k in al.keys():
            if al[k] is None:
                rmset.add(k)
            else:
                alk = al[k].strip()
                if alk == '':
                    rmset.add(k)

        if len(rmset) > 0:
            for k in rmset:
                del al[k]

        return al

    def _from_inverse(self):
        self._alias = dict()
        for k in self._aliasi.keys():
            self._alias[self._aliasi[k]] = k

    def is_ok(self, name):
        """Check if name is in alias key list
        Args:
            name (str)
        """
        return bool(name in self._alias.keys())

    def is_ok_inverse(self, name):
        """Check if name is in alias list
        Args:
            name (str)
        """
        for dval in self._alias.values():
            if name == dval:
                return True
        return False

    def get_alias(self, obj=None):
        """Alias conversion
        Args:
            obj (str/set/list/dict):  Oject to be converted
        Returns:
            Alias converted object
        """
        if obj is None:
            return sorted(self._aliasi.keys())
        elif isinstance(obj, str):
            if obj in self._alias.keys():
                return self._alias[obj]
            else:
                return obj

        elif isinstance(obj, set):
            tran_set = set()
            for name in obj:
                if name in self._alias.keys():
                    tran_set.add(self._alias[name])
                else:
                    tran_set.add(name)
            return tran_set

        elif isinstance(obj, list):
            tran_list = []
            for name in obj:
                if name in self._alias.keys():
                    tran_list.append(self._alias[name])
                else:
                    tran_list.append(name)
            return tran_list

        elif isinstance(obj, dict):
            tran_dict = dict()
            for name1, name2 in obj.items():
                if name1 in self._alias.keys():
                    new1 = self._alias[name1]
                else:
                    new1 = name1
                if name2 in self._alias.keys():
                    new2 = self._alias[name2]
                else:
                    new2 = name2
                tran_dict[new1] = name2
            return tran_dict

    def get_alias_inverse(self, obj=None):
        """Alias inverse conversion
        Args:
            obj (str/set/list/dict):  Oject to be converted
        Returns:
            Alias inverse converted object
        """
        if obj is None:
            return sorted(self._alias.keys())
        elif isinstance(obj, str):
            if obj in self._aliasi.keys():
                return self._aliasi[obj]
            else:
                return obj

        elif isinstance(obj, set):
            tran_set = set()
            for name in obj:
                if name in self._aliasi.keys():
                    tran_set.add(self._aliasi[name])
                else:
                    tran_set.add(name)
            return tran_set

        elif isinstance(obj, list):
            tran_list = []
            for name in obj:
                if name in self._aliasi.keys():
                    tran_list.append(self._aliasi[name])
                else:
                    tran_set.add(name)
            return tran_list

        elif isinstance(obj, dict):
            tran_dict = dict()
            for name1, name2 in obj.items():
                if name1 in self._aliasi.keys():
                    new1 = self._aliasi[name1]
                else:
                    new1 = name1
                if name2 in self._aliasi.keys():
                    new2 = self._aliasi[name2]
                else:
                    new2 = name2
                tran_dict[new1] = name2
            return tran_dict

    def get_alias_dict(self):
        """Return alias dictionary
        """
        return self._alias

    def _verify_unique(self):
        """Check that alias list is one-to-one
        """
        aset = set()
        for k in self._alias.keys():
            aset.add(self._alias[k])

        if len(aset) != len(self._alias.keys()):
            errmes = 'Non-unique alias list'
            raise ValueError(errmes)

    def read_txt(self, file_name):
        """Read alias file
        Args:
            file_name (str): File name
        Note:
            Alias file is assumed to contain list of well_name and aliases.
            The list should be arranged as two columns, first column names, second column aliases.
            Quotation marks should be used for names containing blanks.
            Comments start with #.
        """

        try:
            pfil = open(file_name, 'r')
        except OSError as e:
            errmes = 'Error opening file ' + file_name + '\n' + str(e)
            raise OSError(errmes)

        alias = dict()

        line_no = 1
        while True:
            try:
                line = pfil.readline()
            except IOError as e:
                errstr = 'Error reading alias file, line ' + str(line_no) + '\n' + str(e)
                raise IOError(errstr)

            if not line:
                break

            line_no += 1
            z1 = "'"
            z2 = '"'

            temp = line.strip()
            if temp == '':
                pass    # Skip blank lines
            elif temp.startswith('#'):
                pass    # Skip comments starting with #
            else:
                terms = line_split(temp, line_no)
                if len(terms) == 2:
                    name1 = terms[0]
                    name2 = terms[1]
                    alias[name1] = name2
                else:
                    errstr = 'Error reading alias file, line ' + str(line_no) + '\n'
                    errstr += 'Incorrect number of terms found in line, expected 2.'
                    raise IOError(errstr)

        if len(alias) > 0:
            self._alias = alias
        else:
            errmes = 'Empty alias dictionary'
            raise ValueError(errmes)

        self._verify_unique()
        self._to_inverse()
        return None

    def write_txt(self, file_name):
        """Write alias file
        Args:
            file_name (str): File name
        Note:
            Alias file is assumed to contain list of well_name and aliases.
            The list should be arranged as two columns, first column names, second column aliases.
            Quotation marks should be used for names containing blanks.
            Comments start with #.
        """

        try:
            outfil = open(file_name, 'w')
        except OSError as e:
            errmes = 'Error opening file ' + file_name + '\n' + str(e)
            raise IOError(errmes)

        print('# Well name', 19*' ', 'Alias', file=outfil)
        for name in sorted(self._alias.keys()):
            well_name = self._alias[name]
            print('{:30}  {:30}'.format(name, well_name), file=outfil)

        outfil.close()

        return None
