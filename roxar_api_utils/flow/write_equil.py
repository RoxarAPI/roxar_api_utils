import roxar_api_utils.ioutil

def write_equil(fp, equildat):
    """Write Eclipse EQUIL keyword
    Args:
        fp: File pointer to open file
        equildat:  List of dicts with equil data.  Keys = (PDATUM,GOC,OWC,PCOWC,PCGOC,TRSVD,TRVVD)
    """

    roxar_api_utils.ioutil.write_file_header(fp, comment_start='--', name=None)
    print('EQUIL', file=fp)
    print('--    Datum    Pdatum       OWC     PCOWC', end='', file=fp)
    print('       GOC     PCGOC     TRSVD     TRVVD', file=fp)

    for deq in equildat:
        pdatum = deq.get('PDATUM', 0.0)
        goc = deq.get('GOC', 0.0)
        owc = deq.get('OWC', 0.0)
        pcowc = deq.get('PCOWC', 0.0)
        pcgoc = deq.get('PCGOC', 0.0)
        trsvd = deq.get('TRSVD', 0)
        trvvd = deq.get('TRVVD', 0)

        print('   ', '{:7.2f}'.format(goc), '  ', end='', file=fp)
        print('{:7.2f}'.format(pdatum), '  ', end='', file=fp)
        print('{:7.2f}'.format(owc), '    ', end='', file=fp)
        print('{:5.2f}'.format(pcowc), '  ', end='', file=fp)
        print('{:7.2f}'.format(goc), '    ', end='', file=fp)
        print('{:5.2f}'.format(pcgoc), '    ', end='', file=fp)
        print(trsvd, '        ', end='', file=fp)
        print(trvvd, '   /', file=fp)

    print(file=fp)

    return None
