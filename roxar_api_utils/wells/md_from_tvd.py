def _zloc(tvd, sps, md0, z0, md1, z1):
    """Locate md corresponding to given tvd, by simple bisecting
    Args:
        tvd (float): TVD value to locate
        md0 (float): MD for nearest table point above (in measured depth)
        z0 (float): TVD for nearest table point above
        md1 (float): MD for nearest table point below
        z1 (float): TVD for nearest table point below
    Returns:
        MD value corresponding to tvd
    """
    for iter in range(100):
        der = (md1 - md0)/(z1 - z0)
        md  = md0 + der*(tvd - z0)
        zu  = sps.interpolate_survey_point(md)[5]
        if abs(zu-tvd) < 1e-6:
            break
        z1 = zu
        md1 = md
    return md

def md_from_tvd(tvd, sps, mdps, mdstart=0.0):
    """Locate first well MD larger than a start value, corresponding to a given TVD.
    Args:
        tvd: TVD value to locate
        sps:  Survey point series for well
        mdps: Numpy array of trajectory points
        mdstart: MD value to start searching
    Returns:
        MD value corresponding to TVD
    Note:
        Returns negative min well md value if TVD is above well.
        Returns negative max md value if TVD is below well.
    """
    md0, x0, y0, z0 = mdps[0]
    if mdstart <= md0 and tvd < z0:
        return -md0
    for i in range(1, len(mdps)):
        md1, x1, y1, z1 = mdps[i]
        if mdstart <= md1:
            if (z1 - tvd)*(z0 - tvd) <= 0:
                md = _zloc(tvd, sps, md0, z0, md1, z1)
                return md
        md0, x0, y0, z0 = mdps[i]
    return -md1
