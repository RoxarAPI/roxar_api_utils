def padblanc8(sval):
    """Make string 8 characters long by padding with blanks
    Args:
        sval (str): String
    Returns:
        String of 8 characters, padded with blanks
    """
    lens = len(sval)
    blank = '        '
    if lens >= 8:
        return sval[0:8]
    else:
        lb = 8 - lens
        return sval + blank[0:lb]
