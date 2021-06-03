import numpy as np
from datetime import datetime
import copy

import roxar_api_utils.ioutil

#---------------------------------------------------------------------------------------
# ProfilesVector class

class ProfilesVector:
    """Class for storing a single Profiles vector
    Args:
        keyword (str): Keyword
        profdata (Numpy array):  Profiles data
        name (str): Optional well/group name
        num (int): Numerical identifiers
        unit (str): Units
        lgrnam (str): LGR name
    Note:
        LGR data not yet properly supported
    """

    def __init__(
            self,
            keyword,
            profdata=None,
            name=None,
            num=None,
            unit=None,
            lgrname=None,
            setindex=None):

        zdum = ':+:+:+:+'
        self._keyword = keyword.strip()
        self._profdata = profdata
        if name is None:
            self._name = zdum
        else:
            self._name = name.strip()
        if num is None:
            self._num = 0
        else:
            self._num = num
        if unit is None:
            self._unit = zdum
        else:
            self._unit = unit.strip()
        if lgrname is None:
            self._lgrname = zdum
        else:
            self._lgrname = lgrname.strip()

# Index to vector in Profiles set
        self._sindex = setindex

    def __str__(self):
        """Print statement for ProfilesVector
        """

        blank = 8*' '

        if self._name is None:
            name = blank
        else:
            name = self._name

        if self._num is None:
            num = blank
        else:
            num = str(self._num)

        if self._unit is None:
            unit = blank
        else:
            unit = self._unit

        if self._lgrname is None:
            lgrname = blank
        else:
            lgrname = self._lgrname

        prstring = self._keyword + ' ' + name + ' ' + num + ' ' + unit + ' ' + lgrname

        return prstring

    def __copy__(self):
        """Return copy of Profiles object
        """

        return ProfilesVector(
            self._keyword,
            self._profdata,
            self._name,
            self._num,
            self._unit,
            self._lgrname,
            self._sindex)

    copy = __copy__

    def _get_keyword(self):
        """Get keyword
        """

        return self._keyword

    def _get_name(self):
        """Get name
        """

        return self._name

    def _set_name(self, name):
        """Set name
        """

        self._name = name.strip()

        return None

    def _get_num(self):
        """Get identifier
        """

        return self._num

    def _set_num(self, num):
        """Set name
        """

        self._num = num

        return None

    def _get_unit(self):
        """Get unit
        """

        return self._unit

    def _set_unit(self, unit):
        """Set unit
        """

        self._unit = unit.strip()

        return None

    def _get_lgrname(self):
        """Get LGR name
        """

        return self._lgrname

    def _set_lgrname(self, lgrname):
        """Set LGR name
        """

        self._lgrname = srip(lgrname)

        return None

    def _get_index(self):
        """Get profiles set index
        """

        return self._sindex

    def _set_index(self, indx):
        """Set Profiles set index
        """

        self._sindex = indx
        return None

    def _get_data(self):
        """Get profiles vector data
        """

        return self._profdata

    def _set_data(self, sdat):
        """Set profiles vector data
        """

        self._profdata = sdat

    def append_tstep(self, value):
        """Append time step value to profiles vector
        Args:
            value (float):  Vector value
        """

        if self._profdata is None:
            self._profdata = np.array([value])
        else:
            self._profdata = np.append(self._profdata, value)

        return None

    keyword = property(_get_keyword, doc='Get/set Profiles vector keyword')
    name = property(_get_name, _set_name, doc='Get/set Profiles vector well/group name')
    num = property(_get_num, _set_num, doc='Get/set Profiles vector numerical identifier')
    unit = property(_get_unit, _set_unit, doc='Get/set Profiles vector unit')
    lgrname = property(_get_lgrname, _set_lgrname, doc='Get/set Profiles vector LGR name')
    profdata = property(_get_data, _set_data, doc='Get/set Profiles vector data')
    index = property(_get_index, _set_index, doc='Get/set vector index in Profiles set')


#--------------------------------------------------------------------------------------------
# Profiles class

class Profiles:
    """Storage of Profiles data
    Args:
        idtsring (str):  Id string with Profiles set name
        keywords (list of str*8): Optional keyword list
        names (list of str*8): Optional well/group names list
        nums (list of ints): Optional list of numerical identifiers
        units (list of str*8): Optional list of units
        startdate (datetime):  Start date
        griddim (tupe): Option grid dimensions
        profdata (Numpy array):  Profiles data
        backwards (bool): Flag for rate representation
    """

    def __init__(
            self,
            profid=None,
            keywords=None,
            names=None,
            nums=None,
            units=None,
            startdate=None,
            griddim=(1, 1, 1),
            profdata=None,
            backwards=True):

        self._profid = profid
        self._profiles = []

        self._nokeys = 0
        self._nosteps = 0

        self._startdate = startdate
        self._nx, self._ny, self._nz = griddim

        self._backwards = backwards

        if keywords is not None:
            self._nokeys = len(keywords)
            for i, key in enumerate(keywords):
                v = ProfilesVector(key)
                v.index = i
                self._profiles.append(v)

            if names is not None:
                for i in range(self._nokeys):
                    self._profiles[i].name = names[i]
            if nums is not None:
                for i in range(self._nokeys):
                    self._profiles[i].num = nums[i]
            if units is not None:
                for i in range(self._nokeys):
                    self._profiles[i].unit = units[i]
            if profdata is not None:
                for i in range(self._nokeys):
                    self._profiles[i].profdata = profdata[i]
                self._nostep = len(profdata[0])

    def __str__(self):
        """Print statement for Profiles
        """

        if self._profid is None:
            profid = 'None'
        else:
            profid = self._profid

        if self._backwards:
            raterepr = 'Backwards constant'
        else:
            raterepr = 'Forwards constant'

        prstring = (
            'Profiles set:        '
            + profid
            + '\nNo of vectors:       '
            + str(self._nokeys)
            + '\nNo of time steps     '
            + str(self._nosteps)
            + '\nGrid dimension:      '
            + str(self._nx)
            + ' '
            + str(self._ny)
            + ' '
            + str(self._nz)
            + '\nStart date:          '
            + str(self._startdate)
            + '\nRate representation: '
            + raterepr)

        return prstring

    def __copy__(self):
        """Return copy of Profiles object
        """

        keywords = []
        names = []
        nums = []
        units = []
        profdata = []
        griddim = [self._nx, self._ny, self._nz]
        for v in self._profiles:
            keywords.append(v.keyword)
            names.append(v.name)
            nums.append(v.num)
            units.append(v.unit)
            profdata.append(v.profdata)

        return Profiles(
            self._profid,
            keywords,
            names,
            nums,
            units,
            self._startdate,
            griddim,
            profdata,
            self._backwards)

    copy = __copy__

    def __iter__(self):
        """Iterator for Profiles
        """

        return iter(self._profiles)

    def _get_nokeys(self):
        """Get number of vectors in data set
        """

        return self._nokeys

    def _get_nosteps(self):
        """Get number of time steps in data set
        """

        return self._nosteps

    def _set_griddim(self, dim):
        """Set grid dimension (nx, ny, nz)
        """

        self._nx, self._ny, self._nz = dim
        return None

    def _get_griddim(self):
        """Get grid dimension (nx, ny, nz)
        """

        return (self._nx, self._ny, self._nz)

    def _get_keywords(self):
        """Get keywords
        """

        keys = []
        for v in self._profiles:
            keys.append(v.keyword)
        return keys

    def _get_names(self):
        """Get well/group name data
        """

        names = []
        for v in self._profiles:
            names.append(v.name)
        return names

    def _get_nums(self):
        """Get nums data

        """

        nums = []
        for v in self._profiles:
            nums.append(v.num)
        return nums

    def _get_units(self):
        """Get unit data
        """

        units = []
        for v in self._profiles:
            units.append(v.unit)
        return units

    def _set_startdate(self, startdate):
        """Set start date
        """

        self._startdate = startdate

        return None

    def _get_startdate(self):
        """Get startdate
        """

        return self._startdate

    def append_tstep(self, tdata):
        """Append data for time step to Profiles data
        Args:
            tdata (list): Profiles data for a single time step
        Returns:
            Number of time steps
        """

        for i, v in enumerate(self._profiles):
            v.append_tstep(tdata[i])

        self._nosteps += 1

        return self._nosteps

    def get_step(self, istep):
        """Get Profiles data for given time step number
        Args:
            istep (int): Time step number
        Returns:
            Profiles data for time step
        """

        tdata = []
        if istep < 0 or istep >= self._nosteps:
            errstr = 'Incorrect time step number : ' + str(istep)
            raise ValueError(errstr)

        for v in self._profiles:
            tdata.append(v.profdata[istep])

        return tdata

    def get_vector(self, keyword=None, name=None, num=None, vindex=None):
        """Find vector in Profiles data set
        Args:
            keyword (str):  Profiles keyword
            name (str): Profile well/group name
            num (int): Profiles numerical ident
            vindex (int): Vector index
        Returns:
            Profiles vector, None if not found
        Note:
            Does not handle LGR data
        """

        if keyword is not None:

            key8 = keyword.strip()
            if name is not None:
                name8 = name.strip()

            if name is None and num is None:
                for v in self._profiles:
                    if v.keyword == key8:
                        return v
            elif num is None:
                for v in self._profiles:
                    if v.keyword == key8 and v.name == name8:
                        return v
            elif name is None:
                for v in self._profiles:
                    if v.keyword == key8 and v.num == num:
                        return v
            else:
                for v in self._profiles:
                    if v.keyword == key8:
                        if v.num == num:
                            if v.name == name8:
                                return v

        elif vindex is not None:
            if vindex < 0 or vindex >= self._nokeys:
                errstr = 'Incorrect vindex value to function get_vector'
                raise ValueError(errstr)
            else:
                return self._profiles[vindex]

        else:
            errstr = 'Missing input data to function get_vector'
            raise ValueError(errstr)

        return None

    def set_vector(self, keyword, profdata, name=None, num=None, unit=None):
        """Set Profiles vector into set
        Args:
            keyword (str):  Profiles keyword
            name (str): Profile well/group name
            num (int): Profiles numerical ident
            unit (str): Unit for keyword
            profdata (list): Profiles data for defined vector
        Returns:
            Index for vector in Profiles data set
            profiles data vector
        Note:
            Overwrites existing vector, adds if non-existing
            LGR data not handled
        """

        lt = len(profdata)
        if self._nosteps == 0:
            self._nosteps = lt
        else:
            if lt != self._nosteps:
                errstr = 'Mismatch in number of time steps defined.'
                raise ValueError(errstr)

        v = self.get_vector(keyword, name, num)

        if v is not None:
            indx = v.index
            self._profiles[indx].profdata = profdata
        else:
            v = ProfilesVector(keyword, profdata, name, num, unit)
            v.index = self._nokeys
            self._nokeys += 1
            self._profiles.append(v)

        return v

    def get_time(self):
        """Return time array
        """

        vt = self.get_vector('TIME')
        if vt is not None:
            return vt.profdata
        else:
            return None

    def wellset(self):
        """Return set of well names in Profiles set
        """

        wnames = set()
        zdum = ':+:+:+:+'

        for v in self._profiles:
            if v.keyword[0] == 'W':
                wn = v.name
                if wn != zdum:
                    wnames.add(wn)

        return wnames

    def groupset(self):
        """Return set of group names in Profiles set
        """

        gnames = set()
        zdum = ':+:+:+:+'

        for v in self._profiles:
            if v.keyword[0] == 'G':
                gn = v.name
                if gn != zdum:
                    gnames.add(gn)

        return gnames

    def _get_backwards(self):
        """Get backwards flag
        """

        return self._backwards

    def _set_backwards(self,backwards):
        """Get backwards flag
        """

        self._backwards = backwards
        return None

    nokeys = property(_get_nokeys, doc='Get no of vectors in Profiles set')
    nosteps = property(_get_nosteps, doc='Get/set no of time steps in Profiles set')
    griddim = property(_get_griddim, _set_griddim, doc='Get/set grid dimension nx,ny,nz')
    keywords = property(_get_keywords, doc='Get Profiles keywords')
    names = property(_get_names, doc='Get Profiles keywords well/group names')
    nums = property(_get_nums, doc='Get/set Profiles numerical identifiers')
    units = property(_get_units, doc='Get/set Profiles units')
    startdate = property(_get_startdate, _set_startdate, doc='Get/set start date')
    backwards = property(_get_backwards, _set_backwards, doc='Get/set backwards flag')
