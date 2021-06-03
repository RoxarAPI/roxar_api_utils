"""Define saturation functions for reservoir simulation:
   Relative permeability functions
   Capillary pressure functions
"""

import math

import roxar_api_utils.ioutil

class EndPoints:
    """Defines class for handling saturation table end points.
    Args:
        swirr: Irreducible water saturation
        swcr: Critical water saturation
        sorw: Residual oil saturation to water
        sorg: Residual oil saturation to gas
        sgirr: Irreducible gas saturation
        sgcr: Critical gas saturation
        kwmax: Max value for water rel.perm
        komax: Max value for oil rel.perm
        kgmax: Max  value for gas rel.perm
        pcwmin: Min value for water/oil cap pressure
        pcwmax: Max value for wate/oil cap pressure
        pcgmin: Min value for gas/oil cap pressure
        pcgmax: Max value for gas/oil cap pressure
    Raises:
        ValueError if unphysical end points
    """

    def __init__(
            self,
            swirr=0.,
            swcr=0.,
            sorw=0.,
            sorg=0.,
            sgirr=0.,
            sgcr=0.,
            kwmax=1.,
            komax=1.,
            kgmax=1.,
            pcwmin=0.,
            pcwmax=1.,
            pcgmin=0,
            pcgmax=1.):

        self._swirr = swirr
        self._swcr = swcr
        self._sorw = sorw
        self._sorg = sorg
        self._sgirr = sgirr
        self._sgcr = sgcr

        self._kwmax = kwmax
        self._komax = komax
        self._kgmax = kgmax

        self._pcwmin = pcwmin
        self._pcwmax = pcwmax
        self._pcgmin = pcgmin
        self._pcgmax = pcgmax

        self._swmin = 0
        self._swmax = 1.
        self._somin = 0
        self._somax = 1.
        self._sgmin = 0
        self._sgmax = 1.

# Check water saturation end points:

        if self._swirr < 0. or self._swirr > 1.:
            raise ValueError('Unphysical end points for water saturation')

        if self._swcr < 0.  or self._swcr > 1.:
            raise ValueError('Unphysical end points for water saturation')

        self._swkdenom = 1. - self._swcr - self._sorw
        if self._swkdenom <= 0.:
            raise ValueError('Unphysical end points for water saturation')

        self._swpdenom = 1. - self._swirr
        if self._swpdenom <= 0.:
            raise ValueError('Unphysical end points for water saturation')

        if self._swcr < self._swirr:
            raise ValueError('Unphysical end points for water saturation')

# Check oil saturation end points:

        if self._sorw < 0. or self._sorw > 1.:
            raise ValueError('Unphysical end points for oil saturation')

        if self._sorg < 0. or self._sorg > 1.:
            raise ValueError('Unphysical end points for oil saturation')

# Check gas saturation end points

        if self._sgirr < 0. or self._sgirr > 1.:
            raise ValueError('Unphysical end points for gas saturation')

        if self._sgcr < 0.  or self._sgcr > 1.:
            raise ValueError('Unphysical end points for gas saturation')

        self._sgkdenom = 1. - self._swirr - self._sgcr - self._sorg
        if self._sgkdenom <= 0.:
            raise ValueError('Unphysical end points for gas saturation')

        self._sgpdenom = 1. - self._sgirr - self._swirr
        if self._sgpdenom <= 0.:
            raise ValueError('Unphysical end points for gas saturation')

        if self._sgirr > self._sgcr:
            raise ValueError('Unphysical end points for gas saturation')

# Check rel.perm end points:

        if self._kwmax < 0.:
            raise ValueError('Unphysical end points for water rel.perm')

        if self._komax < 0.:
            raise ValueError('Unphysical end points for oil rel.perm')

        if self._kgmax < 0.:
            raise ValueError('Unphysical end points for gas rel.perm')

# Check capillary pressure end points:

        if self._pcwmax < self._pcwmin:
            raise ValueError('Unphysical end points for water/oil capillary pressure')

        if self._pcgmax < self._pcgmin:
            raise ValueError('Unphysical end points for gas/oil capillary pressure')

    def _get_swirr(self):
        return self._swirr

    def _get_swcr(self):
        return self._swcr

    def _get_sorw(self):
        return self._sorw

    def _get_sorg(self):
        return self._sorg

    def _get_sgirr(self):
        return self._sgirr

    def _get_sgcr(self):
        return self._sgcr

    def _get_kwmax(self):
        return self._kwmax

    def _get_komax(self):
        return self._komax

    def _get_kgmax(self):
        return self._kgmax

    def _get_pcwmin(self):
        return self._pcwmin

    def _get_pcwmax(self):
        return self._pcwmax

    def _get_pcgmin(self):
        return self._pcgmin

    def _get_pcgmax(self):
        return self._pcgmax

    def _get_swmin(self):
        return self._swmin

    def _get_swmax(self):
        return self._swmax

    def _get_somin(self):
        return self._somin

    def _get_somax(self):
        return self._somax

    def _get_sgmin(self):
        return self._sgmin

    def _get_sgmax(self):
        return self._sgmax

    swirr = property(_get_swirr, doc='Get irreducible water saturation')
    swcr = property(_get_swcr, doc='Get critical water saturation')
    sorw = property(_get_sorw, doc='Get residual oil saturation, water')
    sorg = property(_get_sorg, doc='Get residual oil saturation, gas')
    sgirr = property(_get_sgirr, doc='Get irreducible gas saturation')
    sgcr = property(_get_sgcr, doc='Get critical gas saturation')

    kwmax = property(_get_kwmax, doc='Get max water rel.perm')
    komax = property(_get_komax, doc='Get max oil rel.perm')
    kgmax = property(_get_kgmax, doc='Get max gas rel.perm')

    pcwmin = property(_get_pcwmin, doc='Get min water/oil pc')
    pcwmax = property(_get_pcwmax, doc='Get max water/oil pc')
    pcgmin = property(_get_pcgmin, doc='Get min gas/oil pc')
    pcgmax = property(_get_pcgmax, doc='Get max gas/oil pc')

    swmin = property(_get_swmin, doc='Get min water saturation in tables')
    swmax = property(_get_swmax, doc='Get max water saturation in tables')
    somin = property(_get_somin, doc='Get min oil saturation in tables')
    somax = property(_get_somax, doc='Get max oil saturation in tables')
    sgmin = property(_get_sgmin, doc='Get min gas saturation in tables')
    sgmax = property(_get_sgmax, doc='Get max gas saturation in tables')

    def norm_sw_relp(self, sw):
        """Normalise water saturation for rel.perm
        Args:
            sw: List of table saturations
        Returns:
            List of normalized saturations
        """
        swn = (sw - self._swcr)/self._swkdenom
        swn = max(swn, 0.)
        return swn

    def denorm_sw_relp(self, swn):
        """Denormalise water saturation for rel.perm
        Args:
            swn: List of normalized table saturations
        Returns:
            List of denormalized saturations
        """
        return (swn*self._swkdenom) + self._swcr

    def norm_sw_pc(self, sw):
        """Normalise water saturation for capillary pressure
        Args:
            sw: List of table saturations
        Returns:
            List of normalized saturations
        """
        swn = (sw - self._swirr)/self._swpdenom
        swn = max(swn, 0.)
        return swn

    def denorm_sw_pc(self, swn):
        """Denormalise water saturation for capillary pressure
        Args:
            swn: List of table saturations
        Returns:
            List of denormalized saturations
        """
        return (swn*self._swpdenom) + self._swirr


    def norm_sg_relp(self, sg):
        """Normalise gas saturation for rel.perm
        Args:
            sg: List of table saturations
        Returns:
            List of normalized saturations
        """
        sgn = (sg - self._sgcr) / self._sgkdenom
        sgn = max(sgn, 0.)
        return sgn


    def denorm_sg_relp(self, sgn):
        """Denormalise gas saturation for rel.perm
        Args:
            sgn: List of normalized table saturations
        Returns:
            List of denormalized saturations
        """
        return (sgn*self._sgkdenom) + self._sgcr

    def norm_sow_relp(self, so):
        """Normalise oil saturation for oil/water rel.perm
        Args:
            so: List of table saturations
        Returns:
            List of normalized saturations
        """
        son = (so - self._sorw) / (1. - self._sorw - self._swirr)
        son = max(son, 0.)
        return son

    def denorm_sow_relp(self, son):
        """Denormalise oil saturation for oil/water rel.perm
        Args:
            son: List of table saturations
        Returns:
            List of normalized saturations
        """
        return son*(1. - self._swirr - self._sorw) + self._sorw

    def norm_sog_relp(self, so):
        """Normalise oil saturation for oil/gas rel.perm
        Args:
            so: List of table saturations
        Returns:
            List of normalized saturations
        """
        son = (so - self._sorg) / (1. - self._sorg - self._swirr)
        son = max(son, 0.)
        return son

    def denorm_sog_relp(self, son):
        """Denormalise oil saturation for oil/gas rel.perm
        Args:
            son: List of normalized table saturations
        Returns:
            List of denormalized saturations
        """
        return son*(1. - self._swirr - self._sorg) + self._sorg

    def tsw(self, nopoints):
        """Return table array with saturations for water
        Args:
            nopoints (int):  Number of requested table points
        Returns:
            List of saturation values between endpoints
        """
        sw = []
        diff = self._swcr - self._swirr
        if diff > 0:
            no1 = int(math.floor(diff*nopoints/self._swpdenom))
            if no1 == 0:
                no1 = 1
            no2 = nopoints - no1 - 1
            ds1 = diff*0.90/no1
            for i in range(no1):
                xsw = self._swcr - (no1-i)*ds1
                sw.append(xsw)
        else:
            no1 = 0
            no2 = nopoints - 1
            ds1 = 0

        ds2 = self._swkdenom/(no2 - 1)
        for i in range(no2 - 1):
            xsw = self._swcr + i*ds2
            sw.append(xsw)

        sw.append(1. - self._sorw)
        sw.append(1.)

        self._swmin = sw[0]
        self._swmax = 1.

#       print('Length water: ',len(sw))
        return sw

    def tsg(self, nopoints):
        """Return table array with saturations for gas
        Args:
            nopoints (int):  Number of requested table points
        Returns:
            List of saturation values between endpoints
        """
        sg = []
        diff = self._sgcr - self._sgirr
        if diff > 0:
            no1 = int(math.floor(diff * nopoints / self._sgpdenom)) + 1
            no2 = nopoints - 1 - no1
            ds1 = diff*0.90/no1
            for i in range(no1):
                xsg = self._sgcr - (no1-i)*ds1
                sg.append(xsg)
        else:
            no1 = 0
            no2 = nopoints - 1
            ds1 = 0

        ds2 = self._sgkdenom/(no2-1)
        for i in range(no2-1):
            xsg = self._sgcr + i*ds2
            sg.append(xsg)

        sg.append(1. - self._sorg - self._swirr)
        sg.append(1.)

        self._sgmin = sg[0]
        self._sgmax = 1.

#       print('Length gas: ',len(sg))
        return sg

    def tso(self, nopoints):
        """Return table array with saturations for oil
        Args:
            nopoints (int):  Number of requested table points
        Returns:
            List of saturation values between endpoints
        """
        so = [0.0]
        diff = abs(self._sorw - self._sorg)
        if diff > 0:
            so1 = min(self._sorw, self._sorg)
            so2 = max(self._sorw, self._sorg)
            no1 = int(math.floor(diff*nopoints/(1. - so1))) + 1
            no2 = nopoints - no1 - 1
            ds1 = diff/no1
            for i in range(no1):
                xso = so1 + i*ds1
                so.append(xso)
        else:
            no1 = 0
            no2 = nopoints - 1
            ds1 = 0
            so2 = self._sorw

        ds2 = (1 - self._swirr - so2)/(no2 - 1)
        for i in range(no2 - 1):
            xso = so2 + i*ds2
            so.append(xso)

        xso = 1. - self._swirr
        so.append(xso)

        self._somin = so[0]
        self._somax = xso

#       print('Length oil = ',len(so))
        return so


class SatFunc:
    """Defines class for single saturation functions table
    Args:
        nopoints: Optional number of points in all tables
        tsw: Optional list of water saturation values for tables
        tso: Optional list of oil saturation values for tables
        tsg: Optional list of gas saturation values for tables
    Note:
        nopoints should be given if one of the arrays (tsw,tso,tsg) is not defined
    """

    def __init__(self, endpoints, nopoints=None, tsw=None, tso=None, tsg=None):

        self._endp = endpoints

        if tsw is None:
            if nopoints is None:
                raise ValueError('Missing definition of number of water table points')
            else:
                self._sw = self._endp.tsw(nopoints)
        else:
            if len(tsw) < 2:
                raise ValueError('Water saturation table should contain at least two points')
            self._sw = tsw

        self._krw = []
        self._pcw = []

        if tso is None:
            if nopoints is None:
                raise ValueError('Missing definition of number of oil table points')
            else:
                self._so = self._endp.tso(nopoints)
        else:
            if len(tso) < 2:
                raise ValueError('Oil saturation table should contain at least two points')
            self._so = tso

        self._krow = []
        self._krog = []
        self._somin = 0
        self._somax = 1.

        if tsg is None:
            if nopoints is None:
                raise ValueError('Missing definition of number of gas table points')
            else:
                self._sg = self._endp.tsg(nopoints)
        else:
            if len(tsg) < 2:
                raise ValueError('Gas saturation table should contain at least two points')
            self._sg = tsg

        self._krg = []
        self._pcg = []
        self._sgmin = 0
        self._sgmax = 1.

    def get_wat(self):
        """Returns table for water
        """
        return (self._sw, self._krw, self._pcw)

    def get_oil(self):
        """Returns table for oil
        """
        return (self._so, self._krow, self._krog)

    def get_gas(self):
        """Returns table for gas
        """

        return (self._sg, self._krg, self._pcg)

    def _get_endpoints(self):
        return self._endp

    endp = property(_get_endpoints, doc='Get saturation table end points')

    def corey(self, coeff):
        """Define rel.perm tables from Corey expressions
        Args:
            coeff: List of Corey coefficients nw, now, nog, ng
        """

        nw, now, nog, ng = coeff

        for sw in self._sw:
            swn = self._endp.norm_sw_relp(sw)
            if swn > 1.000001:
                self._krw.append(1.0)
            else:
                krw = self._endp.kwmax*(swn**nw)
                self._krw.append(krw)
            self._pcw.append(0.)

        for sg in self._sg:
            sgn = self._endp.norm_sg_relp(sg)
            if sgn > 1.000001:
                self._krg.append(1.0)
            else:
                krg = self._endp.kgmax*(sgn**ng)
            self._krg.append(krg)
            self._pcg.append(0.)

        for so in self._so:
            son = self._endp.norm_sow_relp(so)
            krow = self._endp.komax*(son**now)
            son = self._endp.norm_sog_relp(so)
            krog = self._endp.komax*(son**nog)
            self._krow.append(krow)
            self._krog.append(krog)

        return None

    def let(self, coeff):
        """Define rel.perm tables from LET expressions
        Args:
            coeff: List of LET coefficients LW,EW,TW,LOW,EOW,TOW,LOG,EOG,TOG,LG,EG,TG
        """

        c_lw, c_ew, c_tw, c_low, c_eow, c_tow, c_log, c_eog, c_tog, c_lg, c_eg, c_tg = coeff

        if c_ew <= 0. or c_eow <= 0. or c_eog <= 0. or c_eg <= 0:
            raise ValueError('E coefficients for LET correlations should be positive')

        try:
            for sw in self._sw:
                swn = self._endp.norm_sw_relp(sw)
                if swn > 1.000001:
                    self._krw.append(1.0)
                else:
                    krw = self._endp.kwmax*(swn**c_lw/(swn*c_lw + c_ew*((1-swn)**c_tw)))
                    self._krw.append(krw)
                self._pcw.append(0.)
        except:
            raise ValueError('Illegal input data for LET correlation for water')

        try:
            for sg in self._sg:
                sgn = self._endp.norm_sg_relp(sg)
                if sgn > 1.000001:
                    self._krg.append(1.0)
                else:
                    krg = self._endp.kgmax*(sgn**c_lg/(sgn*c_lg + c_eg*((1 - sgn)**c_tg)))
                    self._krg.append(krg)
                self._pcg.append(0.)
        except:
            raise ValueError('Illegal input data for LET correlation for gas')

        try:
            for so in self._so:
                son = self._endp.norm_sow_relp(so)
                krow = self._endp.komax * (son**c_low/(son*c_low + c_eow*((1-son)**c_tow)))
                son = self._endp.norm_sog_relp(so)
                krog = self._endp.komax * (son**c_log/(son*c_log + c_eog*((1-son)**c_tog)))
                self._krow.append(krow)
                self._krog.append(krog)
        except:
            raise ValueError('Illegal input data for LET correlation for oil')

        return None

    def standing(self, pindx):
        """Define rel.perm tables from Standing's expressions
        Args:
            pindx: Pore index, should be larger than 1E-8
        """
        if pindx <= 1e-8:
            raise ValueError('Illegal pore index')

        nw = (2. + 3.*pindx)/pindx
        nn = (2. + pindx)/pindx

        for sw in self._sw:
            swn = self._endp.norm_sw_relp(sw)
            if swn > 1.000001:
                self._krw.append(1.0)
            else:
                krw = self._endp.kwmax*(swn**nw)
                self._krw.append(krw)
            self._pcw.append(0.)

        for sg in self._sg:
            sgn = self._endp.norm_sg_relp(sg)
            if sgn > 1.000001:
                self._krg.append(1.0)
            else:
                krg = self._endp.kgmax*(sgn*sgn*(1.-(1.-sgn)**nn))
            self._krg.append(krg)
            self._pcg.append(0.)

        for so in self._so:
            son = self._endp.norm_sow_relp(so)
            krow = self._endp.komax * (son*son*(1.-(1.-son)**nn))
            son = self._endp.norm_sog_relp(so)
            krog = self._endp.komax * (son**nw)
            self._krow.append(krow)
            self._krog.append(krog)

        return None


    def pcw_hlh(self, a, b):
        """Define pcow from Hawkins, Luffel and Harris (Oil & Gas Journal, Jan 18 1993)
        Args:
            a: Correlation coefficient a
            b: Correlation coefficient b
        """

        if len(self._sw) == 0:
            return None

        tpc = []
        swn = self._endp.norm_sw_pc(self._sw[0])
        try:
            pcmax = 10**((a/math.log(1. - swn)) + b)
        except:
            raise ValueError('Incorrect capillary pressure calculation.')

        pcmin = 10**b

        scale = (self._endp.pcwmax - self._endp.pcwmin)/(pcmax - pcmin)

        for sw in self._sw:
            swn = self._endp.norm_sw_pc(sw)
            try:
                if swn < 0.98:
                    pc = 10**((a/math.log(1. - swn)) + b)
                    pc = (pc - pcmin)*scale + self._endp.pcwmin
                else:
                    pc = self._endp.pcwmin
            except:
                raise ValueError('Incorrect capillary pressure calculation.')
            tpc.append(pc)

        self._pcw = tpc

        return None

    def pcw_linear(self):
        """Define linear pcow
        """
        if len(self._sw) == 0:
            return None

        tpc = []

        scale = (self._endp.pcwmax - self._endp.pcwmin)/(self._endp.swmax - self._endp.swmin)

        for sw in self._sw:
            pc = scale*(self._endp.swmax - sw) + self._endp.pcwmin
            tpc.append(pc)

        self._pcw = tpc

        return None

    def pcg_linear(self):
        """Define linear pcog
        """
        if len(self._sg) == 0:
            return None

        tpc = []

        scale = (self._endp.pcgmax - self._endp.pcgmin)/(self._endp.sgmax - self._endp.sgmin)

        for sg in self._sg:
            pc = scale*(self._endp.sgmax - sg) + self._endp.pcgmin
            tpc.append(pc)

        self._pcg = tpc

        return None


class SatFuncModel:
    """Defines class for saturation functions model, containing multiple tables
    Args:
        phases (str): Description of phases, o, g, w, as in 'ow'
    """

    def __init__(self, phases='owc'):

        self._nophases = 0
        self._notables = 0
        self._tables = []
        self._table = None
        self._tabcom = []

        test = phases.lower()
        if test.find('o') > -1:
            self._oil = True
            self._nophases = self._nophases + 1
        else:
            self._oil = False

        if test.find('g') > -1:
            self._gas = True
            self._nophases = self._nophases + 1
        else:
            self._gas = False

        if test.find('w') > -1:
            self._water = True
            self._nophases = self._nophases + 1
        else:
            self._water = False

        if self._nophases < 2:
            raise ValueError('Incorrect phase definition in class SatFuncModel')


    def __str__(self):
        """Returns class information in string format
        """
        phases = ''
        if self._oil:
            phases = phases + 'O'
        if self._gas:
            phases = phases + 'G'
        if self._water:
            phases = phases + 'W'

        string = 'SatFuncModel: ' + phases + ' No of tables: ' + str(self._notables)
        return string

    def get_phases(self):
        """Return defined phases in model
        Returns:
            Tuple of bools (oil,gas,water) where each component is true if phase is available
        """
        return (self._oil, self._gas, self._water)

    def corey(self, endpoints, coeff, nopoints=None, tsw=None, tso=None, tsg=None):
        """Add Corey table to the model
        Args:
            endpoints:  En point info as class EndPoints
            coeff: List of Corey coefficients nw, now, nog, ng
            nopoints (int): Optional no of points in each table, if auto generated
            tsw: Optional list of table water saturation values
            tso: Optional list of table oil saturation values
            tsg: Optional list of table gas saturation values
        Returns:
            SatFunc table
        """
        self._notables = self._notables + 1
        self._table = SatFunc(endpoints, nopoints, tsw, tso, tsg)
        self._table.corey(coeff)
        self._tables.append(self._table)

        nw, now, nog, ng = coeff
        comment = ('Corey correlations with nw='
                   + str(nw)
                   + ', now='
                   + str(now)
                   + ', nog='
                   + str(nog)
                   + ', ng='
                   + str(ng))
        self._tabcom.append(comment)

        return self._table

    def standing(self, endpoints, pindx, nopoints=None, tsw=None, tso=None, tsg=None):
        """Add Standing table to the model
        Args:
            pindx (float): Pore index
            nopoints (int): Optional no of points in each table, if auto generated
            tsw: Optional list of table water saturation values
            tso: Optional list of table oil saturation values
            tsg: Optional list of table gas saturation values
        Returns:
            SatFunc table
        """

        self._notables = self._notables + 1
        self._table = SatFunc(endpoints, nopoints, tsw, tso, tsg)
        self._table.standing(pindx)
        self._tables.append(self._table)

        com = 'Standing correlations with pore index = ' + str(pindx)
        self._tabcom.append(com)

        return self._table

    def let(self, endpoints, coeff, nopoints=None, tsw=None, tso=None, tsg=None):
        """Add rel perm table from LET correlations
        Args:
            coeff: List of LET coefficients LW,EW,TW,LOW,EOW,TOW,LOG,EOG,TOG,LG,EG,TG
            nopoints (int): Optional no of points in each table, if auto generated
            tsw: Optional list of table water saturation values
            tso: Optional list of table oil saturation values
            tsg: Optional list of table gas saturation values
        Returns:
            SatFunc table
        """

        self._notables = self._notables + 1
        self._table = SatFunc(endpoints, nopoints, tsw, tso, tsg)
        self._table.let(coeff)
        self._tables.append(self._table)

        com = 'LET correlations with coefficients \n-- ' + str(coeff)
        self._tabcom.append(com)

        return self._table

    def pcw_hlh(self, acoeff, bcoeff):
        """Define pcow in current table from Hawkins, Luffel and Harris
        Args:
            acoeff: Correlation coefficient a
            bcoeff: Correlation coefficient b
        Returns:
            SatFunc table
        Note:
            From (Oil & Gas Journal, Jan 18 1993)
        """

        self._table.pcw_hlh(acoeff, bcoeff)
        return self._table

    def pcw_linear(self):
        """Define linear pcow in current table
        Returns:
            SatFunc table
        """
        self._table.pcw_linear()
        return self._table

    def pcg_linear(self):
        """Define linear pcog in current table

        Returns:
            SatFunc table

        """
        self._table.pcg_linear()
        return self._table

    def _wendp(self, pfil):
        """Write table end points to data files
        Args:
            pfil: Pointer to open file
        """
        if self._notables == 0:
            return None

        print('-- Table end points', file=pfil)
        print(
            '-- Swirr    Swcr     Sorw     Sorg     Sgirr    Sgcr     kwmax    komax    kgmax    ',
            'pcwmin   pcwmax   pcgmin   pcgmax', file=pfil)
        for tab in self._tables:
            endp = tab.endp
            print(
                '-- ',
                '{:7.5f}'.format(endp.swirr), '  ',
                '{:7.5f}'.format(endp.swcr), '  ',
                '{:7.5f}'.format(endp.sorw), '  ',
                '{:7.5f}'.format(endp.sorg), '  ',
                '{:7.5f}'.format(endp.sgirr), '  ',
                '{:7.5f}'.format(endp.sgcr), '  ',
                '{:7.5f}'.format(endp.kwmax), '  ',
                '{:7.5f}'.format(endp.komax), '  ',
                '{:7.5f}'.format(endp.kgmax), '  ',
                '{:7.2f}'.format(endp.pcwmin), '  ',
                '{:7.2f}'.format(endp.pcwmax), '  ',
                '{:7.2f}'.format(endp.pcgmin), '  ',
                '{:7.2f}'.format(endp.pcgmax), '  ',
                sep='', file=pfil)

        print(file=pfil)

        return None

    def write_eclipse(self, pfil):
        """Write saturation functions to open file in ECLIPSE format
        Args:
            pfil: Pointer to open text file
        """
        if self._notables == 0:
            return None

        roxar_api_utils.ioutil.write_file_header(pfil, comment_start='--')
        self._wendp(pfil)

        print('\nSWFN', file=pfil)
        itab = 0
        for tab in self._tables:
            com = self._tabcom[itab]
            itab = itab + 1
            print(75*('-'), '\n-- Table no. ', itab, file=pfil, sep='')
            print('-- ', com, file=pfil, sep='')
            print(75*('-'), file=pfil, sep='')
            tsw, tkrw, tpcw = tab.get_wat()
            for xval in zip(tsw, tkrw, tpcw):
                sw, krw, pcw = xval
                print('{:7.5f}'.format(sw), end='', file=pfil)
                print(' ', '{:7.5f}'.format(krw), end='', file=pfil)
                print(' ', '{:7.3f}'.format(pcw), file=pfil)
            print('/', file=pfil)

        print('\nSGFN', file=pfil)
        itab = 0
        for tab in self._tables:
            com = self._tabcom[itab]
            itab = itab + 1
            print(75*('-'), '\n-- Table no. ', itab, file=pfil, sep='')
            print('-- ', com, file=pfil, sep='')
            print(75*('-'), file=pfil, sep='')
            tsg, tkrg, tpcg = tab.get_gas()
            for xval in zip(tsg, tkrg, tpcg):
                sg, krg, pcg = xval
                print('{:7.5f}'.format(sg), end='', file=pfil)
                print(' ', '{:7.5f}'.format(krg), end='', file=pfil)
                print(' ', '{:7.3f}'.format(pcg), file=pfil)
            print('/', file=pfil)

        print('\nSOF3', file=pfil)
        itab = 0
        for tab in self._tables:
            com = self._tabcom[itab]
            itab = itab + 1
            print(75*('-'), '\n-- Table no. ', itab, file=pfil, sep='')
            print('-- ', com, file=pfil, sep='')
            print(75*('-'), file=pfil, sep='')
            tso, tkrow, tkrog = tab.get_oil()
            for xval in zip(tso, tkrow, tkrog):
                so, krow, krog = xval
                print('{:7.5f}'.format(so), end='', file=pfil)
                print(' ', '{:7.5f}'.format(krow), end='', file=pfil)
                print(' ', '{:7.5f}'.format(krog), file=pfil)
            print('/', file=pfil)

    def write_more(self, pfil):
        """Write saturation functions to open file in MORE format
        Args:
            pfil: Pointer to open text file
        """
        if self._notables == 0:
            return None

        roxar_api_utils.ioutil.write_file_header(pfil, comment_start='--')
        self._wendp(pfil)

        print('\nSWFN', file=pfil)
        itab = 0
        for tab in self._tables:
            com = self._tabcom[itab]
            itab = itab + 1
            print(75*('-'), '\n-- Table no. ', itab, file=pfil, sep='')
            print('-- ', com, file=pfil, sep='')
            print(75*('-'), file=pfil, sep='')
            tsw, tkrw, tpcw = tab.get_wat()
            for xval in zip(tsw, tkrw, tpcw):
                sw, krw, pcw = xval
                print('{:7.5f}'.format(sw), end='', file=pfil)
                print(' ', '{:7.5f}'.format(krw), end='', file=pfil)
                print(' ', '{:7.3f}'.format(pcw), file=pfil)
            print('/', file=pfil)

        print('\nSGFN', file=pfil)
        itab = 0
        for tab in self._tables:
            com = self._tabcom[itab]
            itab = itab + 1
            print(75*('-'), '\n-- Table no. ', itab, file=pfil, sep='')
            print('-- ', com, file=pfil, sep='')
            print(75*('-'), file=pfil, sep='')
            tsg, tkrg, tpcg = tab.get_gas()
            for xval in zip(tsg, tkrg, tpcg):
                sg, krg, pcg = xval
                print('{:7.5f}'.format(sg), end='', file=pfil)
                print(' ', '{:7.5f}'.format(krg), end='', file=pfil)
                print(' ', '{:7.3f}'.format(pcg), file=pfil)
            print('/', file=pfil)

        print('\nSOF3', file=pfil)
        itab = 0
        for tab in self._tables:
            com = self._tabcom[itab]
            itab = itab + 1
            print(75*('-'), '\n-- Table no. ', itab, file=pfil, sep='')
            print('-- ', com, file=pfil, sep='')
            print(75*('-'), file=pfil, sep='')
            tso, tkrow, tkrog = tab.get_oil()
            for xval in zip(tso, tkrow, tkrog):
                so, krow, krog = xval
                print('{:7.5f}'.format(so), end='', fil=pfil)
                print(' ', '{:7.5f}'.format(krow), end='', file=pfil)
                print(' ', '{:7.5f}'.format(krog), file=pfil)
            print('/', file=pfil)
