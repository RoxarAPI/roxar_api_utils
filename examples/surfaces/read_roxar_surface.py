"""Read a surface in RMS format, store result in current project
"""

import roxar
import roxar_api_utils.surfaces

# --------------------------------------------------------------------------
# Script parameters

# Input RMS surface
file_input_path = r'D:\RMS\Data\surface.rmsbin'

# Horizon name
horizon_name = 'TopF'

# Horizon data type
data_type = 'NewResidualSurface'

# --------------------------------------------------------------------------
# Script starts

horizon = project.horizons.create(horizon_name, roxar.HorizonType.interpreted)
representation = project.horizons.representations.create(data_type,
                                            roxar.GeometryType.surface,
                                            roxar.VerticalDomain.no_domain)

surface = project.horizons[horizon_name][data_type]
new_grid = roxar_api_utils.surfaces.read_roxar_surface(file_input_path)
surface.set_grid(new_grid)

print( 'Horizon surface imported:', horizon_name, data_type)
