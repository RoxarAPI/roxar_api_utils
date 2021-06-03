"""Similar to the standard function split(), but takes into acount quotation marks and comments.

Terms can be separated by blanks or by commas.
A comment is assumed to start with a hash #.

Example:

line = 'This,,   is a "well name"   # Comment '

returns as a list of five strings.

['this', '', 'is, 'a', 'well name']
"""

def _is_error(errmes, line_no):
    if line_no is not None:
       errmes += ' in line ' + str(line_no)
    raise ValueError(errmes)
    return None

def _next_term(line, line_no):
    """Return next term in line + remaining lines
    """

    z1 = "'"
    z2 = '"'
    comma = ','
    is_error = False

    temp = line.lstrip()

    if temp == '':
        return (None, None)
    elif temp[0:1] == comma:
        temp = temp[1:]
        temp = temp.lstrip()

    if temp[0:1] == comma:
        return ('', temp)
    elif temp[0:1] == z1:
        temp = temp.lstrip(z1)
        ie = temp.find(z1)
        if ie >= 0:
            next_term = temp[0:ie]
            remain = temp[ie+1:]
        else:
            errmes = 'Missing quotation mark'
            _is_error(errmes, line_no)

    elif temp[0:1] == z2:
        temp = temp.lstrip(z2)
        ie = temp.find(z2)
        if ie >= 0:
            next_term = temp[0:ie]
            remain = temp[ie+1:]
        else:
            errmes = 'Missing quotation mark'
            _is_error(errmes, line_no)

    else:
        temp2 = temp.replace(comma, ' ')
        all_terms = temp2.split()
        next_term = all_terms[0]
        remain = temp.lstrip(next_term)
        if next_term.endswith(z1):
            errmes = 'Misplaced quotation mark'
            _is_error(errmes, line_no)
        elif next_term.endswith(z2):
            errmes = 'Misplaced quotation mark'
            _is_error(errmes, line_no)

#    print(next_term)
#    print(remain)

    return (next_term, remain)

def line_split(line, line_no=None):
    allterms = []
    while True:
        next_term, line = _next_term(line, line_no)
        if next_term is None:
            break
        else:
            allterms.append(next_term)

# Remove comment
    terms = []
    for trm in allterms:
        if trm.startswith('#'):
            break
        else:
            terms.append(trm)

    if len(terms) == 0:
        terms = None

    return terms

