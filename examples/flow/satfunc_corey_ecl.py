"""
Make three-phase rel.perm tables with Corey correlations and write in Eclipse format

Corey coefficients from Excel spreadsheet

Requires installation of Python library xlrd
"""

import xlrd

import roxar_api_utils.flow

# --------------------------------------------------------
# Script parameters

# Output text file
out_file = r'C:\Users\torb\MyData\temp\tmp.txt'

# Excel file with Corey coefficients
excel_file = r'C:\Users\torb\MyData\python\roxar_api_utils\roxar_api_utils\examples\flow\x_corey.xlsx'

# --------------------------------------------------------
# Start script

wb = xlrd.open_workbook(excel_file)

s = wb.sheets()
sheet1 = s[0]
sheet2 = s[1]
nr = sheet1.nrows

c = roxar_api_utils.flow.SatFuncModel('owg')

endpoints = []
for row in range(1, sheet1.nrows):
    values = []
    for col in range(sheet1.ncols):
        values.append(sheet1.cell(row, col).value)
    endp = roxar_api_utils.flow.EndPoints(
        swirr=values[0],
        swcr=values[1],
        sorw=values[2],
        sorg=values[3],
        sgirr=values[4],
        sgcr=values[5],
        kwmax=values[6],
        komax=values[7],
        kgmax=values[8],
        pcwmin=values[9],
        pcwmax=values[10],
        pcgmin=values[11],
        pcgmax=values[12])

    coeff = []
    for col in range(sheet2.ncols):
        coeff.append(sheet2.cell(row, col).value)

    tab = c.corey(endp, coeff, 20)

pfil = open(out_file, 'w')
c.write_eclipse(pfil)
pfil.close()

print('Output to file', out_file)
