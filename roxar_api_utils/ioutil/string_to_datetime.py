from datetime import datetime

def string_to_datetime(datestring, date_format='DDMMYYYY'):
    """Convert date string to python datetime
    Args:
        datestring: Date represented as string
        date_format: Date format in Qt format
    Returns:
        Datetime object
    Raises:
        ValueError if illegal month name
        Valueerror if illegal date format
    Note:
        Could probably be done much smarter...
    """

    day = 1
    month = 1
    year = 1900

    if date_format == 'ddMMyyyy':
        dstring = datestring[0:2].lstrip('0')
        mstring = datestring[2:4].lstrip('0')
        year = int(datestring[4:])
        month = int(mstring)
        day = int(dstring)

    elif date_format == 'dd MMM yyyy':
        months = (
            'JAN',
            'FEB',
            'MAR',
            'APR',
            'MAY',
            'JUN',
            'JUL',
            'AUG',
            'SEP',
            'OCT',
            'NOV',
            'DEC')
        terms = datestring.split(' ')
        dstring = terms[0].lstrip('0')
        mstring = terms[1].upper()
        year = int(terms[2])

        try:
            month = months.index(mstring) + 1
        except ValueError:
            if mstring == 'JLY':
                month = 7
            else:
                errstr = 'Illegal month name: ' + mstring
                raise ValueError(errstr)

        day = int(dstring)

    else:
        found = False
        for cval in (r'.', r'-', r'*', r'+', r':', r';', '\\', r'/'):
            if date_format.find(cval) >= 0:
                sep = cval
                found = True
                break
        if found:
            date1 = 'dd' + sep + 'MM' + sep + 'yyyy'
            if date_format == date1:
                dstring = datestring[0:2].lstrip('0')
                mstring = datestring[3:5].lstrip('0')
                year = int(datestring[6:])
                month = int(mstring)
                day = int(dstring)
            else:
                errstr = 'Unsupported date format: ' + date_format
                raise ValueError(errstr)

        else:
            errstr = 'Unsupported date format: ' + date_format
            raise ValueError(errstr)

    return datetime(year, month, day, 0, 0, 0, 0)
