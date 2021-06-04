def profiles_interpolation( time,vtime,v,itype='L' ):
    """Profiles interpolation
    Args:
        time (float): Time value
        vt (np array): Time vector
        v (np array): Profiles vector
        itype (character):  Interpolation type (L=Linear,V=Linear volume, B=Backwards,F=Forwards)
    """

    if itype== 'L':
        for i,t in enumerate(vtime):
            if time <= t:
                if i == 0:
                    return 0.
                else:
                    dv = (v[i] - v[i-1])/(vtime[i] - vtime[i-1])
                    return (v[i-1] + dv*(time - vtime[i-1]))

        return 0.

    elif itype== 'V':
        for i,t in enumerate(vtime):
            if time <= t:
                if i == 0:
                    return v[0]
                else:
                    dv = (v[i] - v[i-1])/(vtime[i] - vtime[i-1])
                    return (v[i-1] + dv*(time - vtime[i-1]))

        return v[i]
    elif itype == 'B':
        for i,t in enumerate(vtime):
            if time <= t: return v[i]

        return 0.0

    elif itype == 'F':

        for i,t in enumerate(vtime):
            if time < t:
                if i == 0:
                    return 0.0
                else:
                    return v[i-1]

            elif time == t:
                return v[i]

        return 0.0

    else:
        errstr = 'Incorrect interpolation type: ' + itype
        raise ValueError( errstr )

    return None
