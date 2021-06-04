def is_well(keyword):
    """Check if well keyword
    Args:
        Profiles keyword
    Returns:
        True if well keyword
    """
    return bool(keyword[0] == 'W' or keyword[0:2] == 'LW')

def is_group(keyword):
    """Check if group keyword
    Args:
        Profiles keyword
    Returns:
        True if group keyword
    """
    return bool(keyword[0] == 'G')

def is_field(keyword):
    """Check if field keyword
    Args:
        Profiles keyword
    Returns:
        True if field keyword
    """
    return bool(keyword[0] == 'F')

def is_rate(keyword):
    """Check if rate keyword
    Args:
        Profiles keyword
    Returns:
        True if rate keyword
    """
    if keyword[0] == 'L':
        z2 = keyword[3:5]
    else:
        z2 = keyword[2:4]
    return bool(z2 == 'PR' or z2 == 'SR' or z2 == 'IR' or z2 == 'FR')

def is_cumulative(keyword):
    """Check if cumulative keyword
    Args:
        Profiles keyword
    Returns:
        True if cumulative keyword
    """
    if keyword[0] == 'L':
        z1 = keyword[4:5]
        z2 = keyword[3:5]
        z3 = keyword[2:5]
    else:
        z1 = keyword[3:4]
        z2 = keyword[2:4]
        z3 = keyword[1:4]
    if z3 == 'WCT':
        isok = False
    elif keyword == 'MONTH   ':
        isok = False
    elif z1 == 'T' and z2 != 'IP':
        isok = True
    else:
        isok = False
    return isok

def is_cell(keyword):
    """Check if cell keyword
    Args:
        Profiles keyword
    Returns:
        True if cell keyword
    """
    if keyword[0] == 'L':
        z1 = keyword[1]
    else:
        z1 = keyword[0]
    return bool(z1 == 'B')

def is_cellperf(keyword):
    """Check if cell perforation keyword
    Args:
        Profiles keyword
    Returns:
        True if cell perforation keyword
    """
    if keyword[0] == 'L':
        z1 = keyword[1]
    else:
        z1 = keyword[0]
    return bool(z1 == 'C')

def is_timedef(keyword):
    """Check if time definition keyword
    Args:
        Profiles keyword
    Returns:
        True if time definition keyword
    """

    vtime = ('TIME    ', 'DAY     ', 'MONTH   ', 'YEAR    ', 'YEARS   ')
    return bool(keyword in vtime)
