"""Strip comments from line.  Comments start with a hash sign #
"""

def comment_strip(line):

    if line is None:
        return None

    ix = line.find('#')
    if ix >= 0:
        return line[0:ix]
    else:
        return line
