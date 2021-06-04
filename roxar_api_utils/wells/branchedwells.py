import copy
import copy
import numpy as np

import roxar_api_utils.ioutil

class BranchedWells:
    """Class for defining branched wells
    Args:
        text_file (str):  Name of text file with branch information
        parents (dict of dicts): For each main well, a dictionary with parent[child]
    Note:
        The BranchedWells class stores information about parent/child relationship
        in a branched well.
    """
    def __init__(self, text_file=None, parents=None):

        self._wells = set()      # Set of names for all main wells
        self._branches = set()   # Set of names for all branches
        self._parents = dict()   # Dict of parent dicts
        self._wtie = dict()      # Branch tie-in point
        self._mainwell = dict()  # Main well for each branch, irrespectively of level

        if text_file is not None:
            self.read_txt(text_file)

        elif parents is not None:
            self._parents = copy.deepcopy(parents)
            for wname in parents.keys():
                self._wells.add(wname)
                for bname in parents[wname].keys():
                    self._branches.add(bname)
                    self._mainwell[bname] = wname
                    self._wtie[bname] = -1.0

        else:
            errmes = 'Missing input for class BranchedWells'
            raise ValueError(errmes)

        self._traj_type = 'Drilled trajectory'
        self._prefix = 'BR_'


    def __iter__(self):
        for name in sorted(self._wells):
            yield name

    def get_branched_wells(self):
        """Sorted list of branched wells
        """
        return sorted(list(self._wells))

    def _get_no_wells(self):
        return len(self._wells)

    def _get_no_branches(self):
        return len(self._branches)

    no_wells = property(_get_no_wells, doc='No of branched wells')
    no_branches = property(_get_no_branches, doc='No of branches')

    def is_branched(self, name):
        """check if well is branched
        Args:
            name (str): Well name
        """
        return bool(name in self._wells)

    def get_branch_names(self, mainwell=None):
        """Sorted list of all branch names
        """

        if mainwell is None:
            return sorted(list(self._branches))
        else:
            if mainwell in self._wells:
                par = self._parents[mainwell]
                return sorted(par.keys())
            else:
                return None

    def get_branch_names_leveled(self, mainwell):
        """Return branches names per level
        Args:
            mainwell (str):  Main well name
        Returns:
            List of branch names per level [[br1,br2,br3],[br4]]
        """

        if mainwell not in self._wells:
            return None

        branches = []
        prev = [mainwell]
        par = self._parents[mainwell]

        for itr in range(0, 10):
            now = []
            for p in prev:
                for key, val in par.items():
                    if val == p:
                        now.append(key)

            if len(now) > 0:
                branches.append(now)
                prev = now
            else:
                break

        return branches

    def get_parents(self, name):
        """Return parent list for given well
        Args:
            name (str):  well name
        Returns:
            Parent dictionary, None if not found
        """

        if name in self._wells:
            return self._parents[name]
        else:
            return None

    def get_branch_parent(self, branch_name):
        """Return parent for given branch
        """

        if branch_name in self._branches:
            for wname in self._wells:
                par = self._parents[wname]
                if branch_name in par.keys():
                    return par[branch_name]

        return None

    def get_wtie(self, name=None):
        """Return well tie for given branch
        """

        if name is None:
            return self._wtie
        elif name in self._branches:
            return self._wtie[name]
        else:
            return None

    def set_wtie(self, name, wtie):
        """Set well tie for given branch
        """

        if name in self._branches:
            self._wtie[name] = copy.deepcopy(wtie)

        return None

    def _get_traj_type(self):
        return self._traj_type

    def _set_traj_type(self, traj_type):
        self._traj_type = traj_type
        return None

    traj_type = property(_get_traj_type, _set_traj_type, doc='Trajectory type')

    def _get_prefix(self):
        return self._prefix

    def _set_prefix(self, prefix):
        self._prefix = prefix
        return None

    prefix = property(_get_prefix, _set_prefix, doc='Branched well name prefix')

    def get_main_well(self, name):
        """Return main well for given branch
        """

        if name in self._branches:
            return self._mainwell[name]
        else:
            return None

    def read_txt(self, input_name):
        """Read branch info from file
        Args:
            input_name (str): File input name
        Note:
            The text file is expected to contain data for branches/parents/branch tie, with keyword
                BRANCHES mainwell
                    branch1    parent1   branch_tie_1
                    branch2    parent2   branch_tie_2
                /
        """

        try:
            pfil = open(input_name, 'r')
        except OSError as e:
            raise OSError(e)

        line_no = 1
        qkey = False
        while True:
            try:
                line = pfil.readline()
            except IOError as e:
                pfil.close()
                errmes = 'Error reading branch file, line ' + str(line_no) + '\n' + str(e)
                raise IOError(errmes)

            if not line:
                break
            line_no += 1

            ix = line.find('#')
            if ix >= 0:
                temp = line[0:ix]
            else:
                temp = line

            terms = roxar_api_utils.ioutil.line_split(temp, line_no)

            if temp == '':
                pass    # Skip blank lines
            elif terms is None:
                pass  # Should not happen...
            elif terms[0] == 'BRANCHES':
                if len(terms) > 1:
                    mainwell = terms[1]
                    self._wells.add(mainwell)
                    parent = dict()
                    qkey = True
            elif terms[0].startswith('/'):
                if qkey:
                    qkey = False
                    self._parents[mainwell] = parent
                    del parent
            elif qkey and len(terms) == 3:
                b = terms[0]
                par = terms[1]
                wtie = float(terms[2])
                parent[b] = par
                self._branches.add(b)
                self._wtie[b] = wtie
                self._mainwell[b] = mainwell
            elif qkey:
                errmes = 'Incorrect number of data items in line number ' + str(line_no) + '\nExpected three values.'
                raise IOError(errmes)
        else:
            pass
#           print('Error: ',line)

        pfil.close()
        return None

    def write_txt(self, file_name):
        """Write branch info to file
        Args:
            file_name (str): File name
        """
        try:
            pf = open(file_name, 'w')
        except OSError as e:
            raise OSError(e)

        for w in sorted(self._wells):
            par = self._parents[w]
            print('BRANCHES ', w, sep='', file=pf)
            for b in sorted(par.keys()):
                print('  {:25}  {:25}   '.format(b, par[b]), end='', file=pf)
                print(self._wtie[b], file=pf)
            print('/\n', file=pf)

        pf.close()
        return None

    def copy_alias_inverse(self, aliasinfo):
        """Make copy of BranchedWells object, with alias names
        Args:
            aliasinfo (NameAlias): Alias info
        """

        newparlib = dict()
        oldparlib = self._parents

        for oldname in self._wells:
            oldpar = oldparlib[oldname]
            newname = aliasinfo.get_alias_inverse(oldname)

            newpar = dict()
            for oldk, oldp in oldpar.items():
                newk = aliasinfo.get_alias_inverse(oldk)
                newp = aliasinfo.get_alias_inverse(oldp)
                newpar[newk] = newp
            newparlib[newname] = newpar

        newbranchinfo = BranchedWells(parents=newparlib)

        for oldname, oldtie in self._wtie.items():
            newname = aliasinfo.get_alias_inverse(oldname)
            newbranchinfo.set_wtie(newname, oldtie)

        return newbranchinfo

    def copy_alias(self, aliasinfo):
        """Make copy of BranchedWells object, with alias names
        Args:
            aliasinfo (NameAlias): Alias info
            inverse:  True if alias inverse names should be used
        """

        newparlib = dict()
        oldparlib = self._parents

        for oldname in self._wells:
            oldpar = oldparlib[oldname]
            newname = aliasinfo.get_alias(oldname)

            newpar = dict()
            for oldk, oldp in oldpar.items():
                newk = aliasinfo.get_alias(oldk)
                newp = aliasinfo.get_alias(oldp)
                newpar[newk] = newp
            newparlib[newname] = newpar

        newbranchinfo = BranchedWells(parents=newparlib)

        for oldname, oldtie in self._wtie.items():
            newname = aliasinfo.get_alias(oldname)
            newbranchinfo.set_wtie(newname, oldtie)

        return newbranchinfo

    def get_trajectory_tie(self, rms_project):
        """Find tie-in points from RMS trajectories
        Args:
            rms_project (Roxar API): Project
        Returns:
            Dictionary of well tie in points
        """

        md_tie = dict()

        for bname in self._branches:
            md_tie[bname] = 0.0

            if bname not in rms_project.wells.keys():
                continue

            well2 = rms_project.wells[bname]
            track2 = well2.wellbore.trajectories[self._traj_type]
            points2 = track2.survey_point_series.get_survey_points()

            parname = self.get_branch_parent(bname)
            if parname not in rms_project.wells.keys():
                continue
            try:
                well1 = rms_project.wells[parname]
            except:
                errmes = 'Error: Parent well not found in RMS: ' + parname
                print(errmes)
                continue
            try:
                track1 = well1.wellbore.trajectories[self._traj_type]
                points1 = track1.survey_point_series.get_survey_points()
            except:
                errmes = (
                    'Error: Parent well trajectory not found in RMS: '
                    + parname
                    + ' '
                    + self._traj_type)
                print(errmes)
                continue

            if well1.wellhead != well2.wellhead:
                print('Error: Non-matching well heads ', bname, parname)
                continue
            if well1.rkb != well2.rkb:
                print('Error: Non-matching RKB ', bname, parname)
                continue

            mdbreak = 0.
            for i, p in enumerate(points1):
                if np.all(p != points2[i]):
                    break
                mdbreak = p[0]

            md_tie[bname] = mdbreak

        return md_tie

    def branched_alias(self, aliasinfo):
        """Make new NameAlias object with branch prefix
        """

        newalias = dict()
        for oa in aliasinfo:
            wname, al = oa
            if wname in self._wells:
                newname = self._prefix + wname
                newalias[newname] = al
            elif wname in self._branches:
                newname = self._prefix + wname
                newalias[newname] = al
            elif al in self._wells:
                newname = self._prefix + wname
                newalias[newname] = al
            elif al in self._branches:
                newname = self._prefix + wname
                newalias[newname] = al
            else:
                newalias[wname] = al

        aliasinfo2 = roxar_api_utils.ioutil.NameAlias(alias_dict=newalias)
        return aliasinfo2
