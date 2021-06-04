"""Classes for defining data for simulation wells and well groups

Updated January 9 2017

"""

from datetime import datetime

class SimWell:
    """Define and store data for a single simulation well

    Args:
        type (str): well type Producer/Injector
        phase (str): Main well phase Gas/Oil/Water

    """

    def __init__(self, name, type='Producer', phase='Oil'):

        self._name = name
        self._type = type
        self._phase = phase
        self._group = None
        self._cmode = None      # Well control mode
        self._cphase = phase    # Control phase
        self._startdate = datetime(1950, 1, 1)
        self._shutstop = None
        self._endrun = None   # End-run flag
        self._iswseg = False
        self._lifttab = None
        self._ishist = False
        self._nobranches = 0
        self._densmod = None
        self._bhpref = None
        self._crossflow = True
        self._mdstart = None

    def _get_name(self):
        return self._name

    def _get_group(self):
        return self._group

    def _set_group(self, group):
        self._group = group
        return None

    def _get_type(self):
        return self._type

    def _set_type(self, type):
        self._type = type
        return None

    def _get_phase(self):
        return self._phase

    def _set_phase(self, phase):
        self._phase = phase
        return None

    def _get_startdate(self):
        return self._startdate

    def _set_startdate(self, startdate):
        self._startdate = startdate
        return None

    def _get_cmode(self):
        return self._cmode

    def _set_cmode(self, cmode):
        self._cmode = cmode
        return None

    def _get_cphase(self):
        return self._cphase

    def _set_cphase(self, cphase):
        self._cphase = cphase
        return None

    def _get_shutstop(self):
        return self._shutstop

    def _set_shutstop(self, shutstop):
        self._shutstop = shutstop
        return None

    def _get_endrun(self):
        return self._endrun

    def _set_endrun(self, endrun):
        self._endrun = endrun
        return None

    def _get_lifttab(self):
        return self._lifttab

    def _set_lifttab(self, notab):
        self._lifttab = notab
        return None

    def _get_ishist(self):
        return self._ishist

    def _set_ishist(self, ishist):
        self._ishist = ishist
        return None

    def _get_iswseg(self):
        return self._iswseg

    def _set_iswseg(self, iswseg):
        self._iswseg = iswseg
        return None

    def _get_nobranches(self):
        return self._nobranches

    def _set_nobranches(self, nobranches):
        self._nobranches = nobranches
        return None

    def _get_densmod(self):
        return self._densmod

    def _set_densmod(self, densmod):
        self._densmod = densmod
        return None

    def _get_crossflow(self):
        return self._crossflow

    def _set_crossflow(self, crossflow):
        self._crossflow = crossflow
        return None

    def _get_bhpref(self):
        return self._bhpref

    def _set_bhpref(self, bhpref):
        self._bhpref = bhpref
        return None

    def _get_mdstart(self):
        return self._mdstart

    def _set_mdstart(self, mdstart):
        self._mdstart = mdstart
        return None

    name = property(_get_name, doc='Well name')
    group = property(_get_group, _set_group, doc='Well group')
    start_date = property(_get_startdate, _set_startdate, doc='Well start date')
    type = property(_get_type, _set_type, doc='Well type')
    phase = property(_get_phase, _set_phase, doc='Well phase')
    cmode = property(_get_cmode, _set_cmode, doc='Well control mode')
    cphase = property(_get_cphase, _set_cphase, doc='Well control phase')
    shutstop = property(_get_shutstop, _set_shutstop, doc='Shut/stop flag')
    endrun = property(_get_endrun, _set_endrun, doc='End-run flag')
    lifttab = property(_get_lifttab, _set_lifttab, doc='Well lift table')
    is_hist = property(_get_ishist, _set_ishist, doc='Well historical well')
    is_wseg = property(_get_iswseg, _set_iswseg, doc='Is using WSEG keyword')
    no_branches = property(_get_nobranches, _set_nobranches, doc='No of branches in WELLSEGS')
    densmod = property(_get_densmod, _set_densmod, doc='Density model')
    crossflow = property(_get_crossflow, _set_crossflow, doc='Crossflow flag')
    bhpref = property(_get_bhpref, _set_bhpref, doc='BHP reference depth')
    mdstart = property(_get_mdstart, _set_mdstart, doc='Start MD in WELLSEGS')

class SimGroup:
    """Storage of various well group information

    Args:
        gname (str): Group name.  Real groups, not wildcards
        parent (str):  Parent group

    """

    def __init__(self, gname, parent=None):

        self._gname = gname

        self._members = set()
        self._parent = parent

    def _get_gname(self):
        return self._gname

    def add_member(self, member):
        """Add member to SimGroup

        Args:
            member (str): Group member

        Returns:
            List of all members in group

        """
        self._members.add(member)
        return self._members

    def _get_members(self):
        return self._members

    def _set_parent(self, parent):
        self._parent = parent

    def _get_parent(self):
        return self._parent

    name = property(_get_gname, doc='Well group name')
    members = property(_get_members, doc='Well group members')
    parent = property(_get_parent, _set_parent, doc='Well group parent')


class SimMultiWells:
    """Define and store data for multiple simulation wells

    Args:
        well_names (list str): List of well names

    """

    def __init__(self, well_names=None):

        self._welldict = dict()  # Store wells as dictionary by names
        self._groupdict = dict()

        if well_names is not None:
            for name in well_names:
                simw = SimWell(name)
                self._welldict[name] = simw

    def __iter__(self):
        for name in sorted(self._welldict.keys()):
            yield self._welldict[name]


    def get_well(self, name):
        """Get SimWell from name

        Args:
            name (str): Well name

        Returns:
            SimWell, None if not found

        """
        if name in self._welldict.keys():
            return self._welldict[name]
        else:
            return None

    def add_well(self, simw):
        """Add SimWell

        Args:
            simw (SimWell): SimWell

        """
        name = simw.name
        if len(name) > 0:
            self._welldict[name] = simw

        return None

    def add_well_name(self, wname):
        """Add SimWell from well name

        Args:
            wname (str): Well name

        Returns:
            SimWell

        """
        simw = SimWell(wname)
        self._welldict[wname] = simw
        return simw

    def _get_well_names(self):
        """Sorted list of well names

        """
        return sorted(list(self._welldict.keys()))

    well_names = property(_get_well_names, doc='Well names')

    def get_simgroup(self, name):
        """Get SimGroup from name

        Args:
            name (str): Group name

        Returns:
            SimGroup, None if not found

        """
        if name in self._groupdict.keys():
            return self._groupdict[name]
        else:
            return None

    def add_simgroup(self, simg):
        """Add SimGroup

        Args:
            simg (SimGroup)

        """
        name = simg.name
        if len(name) > 0:
            self._groupdict[name] = simg

        return None

    def get_group_names(self):
        """Get list of all group names

        """
        if len(self._groupdict.keys()) > 0:
            return sorted(list(self._groupdict.keys()))
        else:
            return None

    def add_group(self, group_name, parent_name):
        """Add SimGroup from names

        Args:
            group_name (str): Group name
            parent_name (str): Group parent name

        """
        simg = SimGroup(group_name, parent_name)
        self._groupdict[group_name] = simg

        return None

    def get_parent(self, name):
        """Get parent for well group

        Args:
            name (str):  Group name

        Returns:
            String with name of group parent

        """
        if name in self._welldict.keys():
            simw = self._welldict[name]
            return simw.group
        elif name in self._groupdict.keys():
            simg = self._groupdict[name]
            return simg.parent
        else:
            return None

    def write_csv(self, file_name, aliasinfo):
        """Write CSV file with well info

        Args:
            file_name (str): File name
            aliasinfo (NameAlias): Alias list

        """
        sepa = ';'
        date_format = '%Y-%m-%d'

        try:
            fp = open(file_name, 'w')
        except:
            errmes = 'Failed to open file ' + file_name
            raise IOError(errmes)

        print('WELL', sepa, sep='', end='', file=fp)
        print('ALIAS', sepa, sep='', end='', file=fp)
        print('START DATE', sepa, sep='', end='', file=fp)
        print('TYPE', sepa, sep='', end='', file=fp)
        print('PHASE', sepa, sep='', end='', file=fp)
        print('GROUP', sepa, sep='', end='', file=fp)
        print('BHP REF', sepa, sep='', end='', file=fp)
        print('CRFLOW', sepa, sep='', end='', file=fp)
        print('DENSMOD', sepa, sep='', end='', file=fp)
        print('VFP', sepa, sep='', end='', file=fp)
        print('MD START', sepa, sep='', end='', file=fp)
        print(file=fp)

        for wname in sorted(self._welldict.keys()):
            simw = self._welldict[wname]
            print(wname, sepa, sep='', end='', file=fp)

            aname = aliasinfo.get_alias(wname)
            if aname is None:
                aname = ''
            print(aname, sepa, sep='', end='', file=fp)

            if simw.start_date is None:
                strt = ''
                print(strt, sepa, sep='', end='', file=fp)
            else:
                strt = simw.start_date
                print(strt.strftime(date_format), sepa, sep='', end='', file=fp)

            if simw.type is None:
                wtype = ''
            else:
                wtype = simw.type
            print(wtype, sepa, sep='', end='', file=fp)

            if simw.phase is None:
                wphase = ''
            else:
                wphase = simw.phase
            print(wphase, sepa, sep='', end='', file=fp)

            if simw.group is None:
                grup = ''
            else:
                grup = simw.group
            print(grup, sepa, sep='', end='', file=fp)

            if simw.bhpref is None:
                bhpref = ''
            else:
                bhpref = simw.bhpref
            print(bhpref, sepa, sep='', end='', file=fp)

            if simw.crossflow is None:
                crflow = ''
            else:
                crflow = 'N'
                if simw.crossflow:
                    crflow = 'Y'
            print(crflow, sepa, sep='', end='', file=fp)

            if simw.densmod is None:
                densmod = ''
            else:
                densmod = simw.densmod
            print(densmod, sepa, sep='', end='', file=fp)

            if simw.lifttab is None:
                lifttab = ''
            else:
                lifttab = simw.lifttab
            print(lifttab, sepa, sep='', end='', file=fp)

            if simw.mdstart is None:
                mdstart = ''
            else:
                mdstart = simw.mdstart
            print(mdstart, sepa, sep='', end='', file=fp)

            print(file=fp)

        fp.close()
        return None


    def read_csv(self, file_name, date_format='%Y-%m-%d'):
        """Read CSV file with well definitions

        Args:
            file_name (str): File name
            date_format (str): Optional date format

        """

        sepa = ';'

        try:
            fp = open(file_name, 'r')
        except:
            errmes = 'Failed to open file ' + file_name
            raise IOError(errmes)

        aliasdict = dict()

        line_no = 1
        try:
            line = fp.readline()
        except:
            errmes = 'Failed to read file ' + file_name + ', line ' + str(line_no)
            raise IOError(errmes)

        doread = True
        while doread:

            line_no += 1
            try:
                line = fp.readline()
                if not line:
                    doread = False
            except:
                errmes = 'Failed to read file ' + file_name + ', line ' + str(line_no)
                raise IOError(errmes)

            terms = line.split(sepa)
            lterms = len(terms)

            if lterms > 0:
                wname = terms[0].strip()
                if wname != '':
                    simw = self.add_well_name(wname)
                else:
                    continue
            else:
                return None

            if lterms > 1 and terms[1] != '':
                aliasdict[wname] = terms[1]

            if lterms > 2 and terms[2] != '':
                try:
                    simw.start_date = datetime.strptime(terms[2], date_format)
                except:
                    errmes = 'Failed to read start date: ' + str(terms[2])
                    raise IOError(errmes)

            if lterms > 3 and terms[3] != '':
                simw.type = terms[3]

            if lterms > 4 and terms[4] != '':
                simw.phase = terms[4]

            if lterms > 5 and terms[5] != '':
                simw.group = terms[5]

            if lterms > 6 and terms[6] != '':
                try:
                    simw.bhpref = float(terms[6])
                except:
                    errmes = 'Failed to read BHP value: ' + str(terms[6])
                    raise IOError(errmes)

            if lterms > 7 and terms[7] != '':
                if terms[7].startswith('Y'):
                    simw.crossflow = True
                elif terms[7].startswith('N'):
                    simw.crossflow = False
                else:
                    errmes = 'Incorrect crossflow flag: ' + str(terms[7])
                    raise IOError(errmes)

            if lterms > 8 and terms[8] != '':
                simw.densmod = terms[8]

            if lterms > 9 and terms[9] != '':
                try:
                    simw.lifttab = int(terms[9])
                except:
                    errmes = 'Failed to read VFP table value: ' + str(terms[9])
                    raise IOError(errmes)

            if lterms > 10 and terms[10] != '':
                try:
                    simw.mdstart = float(terms[10])
                except:
                    errmes = 'Failed to read MD start value: ' + str(terms[10])
                    raise IOError(errmes)

        fp.close()

        return aliasdict
