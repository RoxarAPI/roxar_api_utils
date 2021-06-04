def ib_to_cell(ib, nx, ny, nz):
    """Convert from cell number in Eclipse internal ordering to (i,j,k)
    Args:
        ib: Cell number in Eclipse ordering (int)
        nx: Grid dimension (int)
        ny: Grid dimension (int)
        nz: Grid dimension (int)
    Returns:
        3D tuple cell number (i,j,k) in user coordinates, starting with 1
    """
    nxny = nx * ny

    kz = ib // nxny
    if (kz*nxny) < ib:
        kz += 1

    ir = ib - ((kz - 1)*nxny)
    jy = ir // nx
    if (jy * nx) < ir:
        jy += 1

    ix = ir - ((jy - 1)*nx)

    return (ix, jy, kz)

