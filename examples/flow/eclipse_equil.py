"""Write EQUIL keyword based on surface data in RMS

GOC and OWC defined as horizons in RMS.

Two equilibrium regions with identical data.
"""
import roxar_api_utils.flow
import roxar.horizons

# --------------------------------------------------------
# Script parameters

# Output text file
out_file = r'C:\Users\torb\MyData\temp\X.EQUIL.INC'

# Fluid contacts.  Define with horizon name and data type
goc_surf = ['TopC','DepthSurface']
owc_surf = ['TopA','DepthSurface']

# Pressure at datum
pdatum = 250

# --------------------------------------------------------
# Start script

def _make_equil(equildat, pdatum, goc_surf, owc_surf):

    real = project.current_realisation

    name = goc_surf[0]
    type = goc_surf[1]
    s = project.horizons[name][type]
    g = s.get_grid(real)
    gval = g.get_values()
    goc = 0.5*(gval.min() + gval.max())

    name = owc_surf[0]
    type = owc_surf[1]
    s = project.horizons[name][type]
    g = s.get_grid(real)
    gval = g.get_values()
    owc = 0.5*(gval.min() + gval.max())

    dequil = dict()
    dequil['GOC'] = goc
    dequil['OWC'] = owc
    dequil['PDATUM'] = pdatum
    equildat.append( dequil )
    return equildat

# Main
equildat = []
equildat = _make_equil(equildat, pdatum, goc_surf, owc_surf)
equildat = _make_equil(equildat, pdatum, goc_surf, owc_surf)
fp = open(out_file, 'w')
roxar_api_utils.flow.write_equil(fp, equildat)
print( 'Equil file written:',out_file )
fp.close()
