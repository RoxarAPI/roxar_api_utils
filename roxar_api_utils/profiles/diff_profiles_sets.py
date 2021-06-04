import numpy as np
from .profiles import Profiles
from .keyword_check import is_rate
from .keyword_check import is_cell
from .keyword_check import is_cellperf
from .keyword_check import is_timedef
from .profiles_interpolation import profiles_interpolation

def diff_profiles_sets(profiles1, profiles2):
    """Calculate difference between two profiles sets
    Args:
        profiles1 (Profiles):  Profiles set 1
        profiles2 (Profiles2): Profiles set 2
    Returns:
        profiles set
    """

    time1 = profiles1.get_time()
    time2 = profiles2.get_time()

    no_step = time1.size

    profiles = Profiles('DIFF')
    profiles.startdate = profiles1.startdate
    profiles.griddim = profiles1.griddim

    equal_grid = False
    if profiles1.griddim == profiles2.griddim:
        equal_grid = True

    for v1 in profiles1:
        key = v1.keyword
        if is_timedef(key):
            profiles.set_vector(key, v1.profdata, unit=v1.unit)
        else:
            v2 = profiles2.get_vector(key, v1.name, v1.num)
            diffcalc = True
            if v2 is not None:
                vkey2 = v2.keyword
                if not equal_grid:
                    if is_cell(vkey2) or is_cellperf(vkey2):
                        diffcalc = False

                if diffcalc:
                    vdiff = np.zeros(no_step)
                    vdat1 = v1.profdata
                    vdat2 = v2.profdata
                    itype = 'L'
                    if is_rate(key):
                        itype = 'B'
                    for i, t in enumerate(time1):
                        v2t = profiles_interpolation(t, time2, vdat2, itype)
                        vdiff[i] = vdat1[i] - v2t
                    profiles.set_vector(key, vdiff, v1.name, v1.num, v1.unit)

    return profiles
