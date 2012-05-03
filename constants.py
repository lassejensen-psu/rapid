from __future__ import print_function, division
from math import pi as PI

# Physical constants
ELEM_CHARGE    = 1.602176487E-19 # C
MASS_ELECT     = 9.10938215E-31 # kg 
MASS_PROT      = 1.672621637E-27 # kg
MASS_NEUT      = 1.674927211E-27 # kg
PLANCK         = 6.62606896E-34 # Js
HBAR           = PLANCK / ( 2 * PI )
LIGHT          = 2.99792458E8 # m/s
BOLTZMAN       = 1.3806504E-23 # J/K
AVOGADRO       = 6.02214179E23 # N/mol
VACUUM_EL      = 8.854187817e-12 # (A s)/(V m)
VACUUM_MAG     = 1.2566370614e-6 # N/A
FINE_STRUCTURE = 7.2973525698e-3 # N/A
LIGHT_AU       = 137.035999074 # au
AMU            = 1E-3 / AVOGADRO # Kg

class Conversion(object):
    '''A class that defines a conversion value.
    It can be used wherever a number is used, but
    can also be called like a function.
    '''

    def __init__(self, num):
        self.num = num

    def __call__(self, othernum):
        '''When called as a function, does conversion for you'''
        try:
            return self.num * othernum
        except TypeError:
            return self.num + othernum.num

    def __repr__(self):
        return repr(self.num)

    def __add__(self, othernum):
        try:
            return self.num + othernum
        except TypeError:
            return self.num + othernum.num

    def __mul__(self, othernum):
        try:
            return self.num * othernum
        except TypeError:
            return self.num * othernum.num

    def __sub__(self, othernum):
        try:
            return self.num - othernum
        except TypeError:
            return self.num - othernum.num

    def __div__(self, othernum):
        try:
            return self.num / othernum
        except TypeError:
            return self.num / othernum.num

    def __truediv__(self, othernum):
        try:
            return self.num / othernum
        except TypeError:
            return self.num / othernum.num

    def __floordiv__(self, othernum):
        try:
            return self.num // othernum
        except TypeError:
            return self.num // othernum.num

    def __mod__(self, othernum):
        try:
            return self.num % othernum
        except TypeError:
            return self.num % othernum.num

    def __pow__(self, othernum):
        try:
            return self.num** othernum
        except TypeError:
            return self.num**othernum.num

    def __radd__(self, othernum):
        try:
            return othernum + self.num
        except TypeError:
            return othernum.num + self.num

    def __rmul__(self, othernum):
        try:
            return othernum * self.num
        except TypeError:
            return othernum.num * self.num

    def __rsub__(self, othernum):
        try:
            return othernum - self.num
        except TypeError:
            return othernum.num - self.num

    def __rdiv__(self, othernum):
        try:
            return othernum / self.num
        except TypeError:
            return othernum.num / self.num

    def __rtruediv__(self, othernum):
        try:
            return othernum / self.num
        except TypeError:
            return othernum.num / self.num

    def __rfloordiv__(self, othernum):
        try:
            return othernum // self.num
        except TypeError:
            return othernum.num // self.num

    def __rmod__(self, othernum):
        try:
            return othernum % self.num
        except TypeError:
            return othernum.num % self.num

    def __rpow__(self, othernum):
        try:
            return othernum**self.num
        except TypeError:
            return othernum.num**self.num

    def __neg__(self):
        return -self.num

    def __pos__(self):
        return self.num

    def __abs__(self):
        return abs(self.num)

    def __int__(self):
        return int(self.num)

    def __float__(self):
        return float(self.num)

    def __complex__(self):
        return complex(self.num)

# Wavelength-energy conversions
class WVConversion(Conversion):
    '''Conversion factor between energy and wavelengths'''

    def __init__(self, num):
        Conversion.__init__(self, num)

    def __call__(self, othernum):
        try:
            try:
                return self.num / othernum
            except ZeroDivisionError:
                return float('inf')
        except TypeError:
            try:
                return self.num / othernum.num
            except ZeroDivisionError:
                return float('inf')

# Provide for completeness and general programming
NOCONV        = Conversion(1.0)

# Length Conversions
BOHR2ANGSTROM = Conversion(0.52917720859)
ANGSTROM2BOHR = Conversion(1 / BOHR2ANGSTROM)
M2ANGSTROM    = Conversion(1E10)
M2NM          = Conversion(1E9)
M2CM          = Conversion(100)
CM2M          = Conversion(1 / M2CM)
ANGSTROM2M    = Conversion(1 / M2ANGSTROM)
NM2M          = Conversion(1 / M2NM)
M2BOHR        = Conversion(M2ANGSTROM * ANGSTROM2BOHR)
BOHR2CM       = Conversion(BOHR2ANGSTROM / M2ANGSTROM / M2CM)
ANGSTROM2NM   = Conversion(1.0E-1)
NM2ANGSTROM   = Conversion(1.0 / ANGSTROM2NM)
BOHR2NM       = Conversion(BOHR2ANGSTROM * ANGSTROM2NM)
NM2BOHR       = Conversion(1.0 / BOHR2NM)

# Direct energy conversions
HART2WAVENUM  = Conversion(219474.629)
HART2KJPMOL   = Conversion(2625.49996)
HART2KCALPMOL = Conversion(627.509552)
HART2EV       = Conversion(27.2113961)
HART2HZ       = Conversion(6.579683920729E15)
EV2HART       = Conversion(0.0367493088)
EV2WAVENUM    = Conversion(8065.54093)
EV2HZ         = Conversion(2.41798940E14)
WAVENUM2HART  = Conversion(4.5563353E-6)
WAVENUM2EV    = Conversion(1.123964245E-4)
WAVENUM2HZ    = Conversion(M2CM(LIGHT))
HZ2HART       = Conversion(1 / HART2HZ)
HZ2EV         = Conversion(1 / EV2HZ)
HZ2WAVENUM    = Conversion(1 / WAVENUM2HZ)

WAVENUM2INVM  = Conversion(100)
INVM2WAVENUM  = Conversion(1 / WAVENUM2INVM)

# Wavelength to energy (or vise versa) conversions
HART2NM       = WVConversion(45.56335)
EV2NM         = WVConversion(1239.8424121)
WAVENUM2NM    = WVConversion(1E7)
HZ2NM         = WVConversion(M2NM(LIGHT))
NM2HART       = WVConversion(45.56335)
NM2EV         = WVConversion(1239.8424121)
NM2WAVENUM    = WVConversion(1E7)
NM2HZ         = WVConversion(M2NM(LIGHT))

# Other generic conversions
AU2DEBYE = Conversion(2.5417463)

#HART2JOULE = 4.35974394E-18
#JOULE2HART = 1 / 4.35974394E-18

# The elements! elem can be indexed (i.e. elem[6] returns 'C') and elemset can
# be quickly searched ('Be' in elemset)
elem = ( 'Xx', 'H',  'He', 'Li', 'Be', 'B',  'C',  'N',  'O',  'F',  'Ne',
               'Na', 'Mg', 'Al', 'Si', 'P',  'S',  'Cl', 'Ar', 'K',  'Ca', 'Sc',
               'Ti', 'V',  'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zi', 'Ga', 'Ge',
               'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y',  'Zr', 'Nb', 'Mo', 'Tc',
               'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',  'Xe',
               'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb',
               'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W',  'Re', 'Os',
               'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr',
               'Ra', 'Ac', 'Th', 'Pa', 'U', )
elemset = frozenset(elem)

# This function returns a color.
def atomic_color(element):
    """Return the color of an atom, as typically seen in molecular models."""

    # Set colors for each atom
    color = {'H' : (1.0,1.0,1.0),
             'C' : (0.25,0.25,0.25),
             'N' : (0.0,0.0,1.0),
             'O' : (1.0,0.0,0.0),
             'F' : (1.0,0.0,1.0),
             'P' : (0.5,0.5,1.0),
             'S' : (1.0,1.0,0.0),
             'Cl': (0.0,1.0,0.0),
             'Br': (1.0,0.5,0.0),
             'I' : (0.5,0.0,0.5),
             'Cu': (0.72, 0.45,0.2),
             'Ag': (0.90,0.91,0.98),
             'Au': (0.85,0.85,0.1)
            }

    # Return the color requested
    try:
        return color[element]
    except KeyError:
        import sys
        print('Color for {0} not specified.'.format(element),
              'Defaulted to Light Gray', file=sys.stderr)
        return (0.9, 0.9, 0.9);

# This function returns a radius.
def atomic_radius(element):
    """Return a tuple of  atomic radii.  The first value is NOT PHYSICAL and
    only used for visualization like in ADFView.  The second value is a real
    physical (Van der Waal) radius."""

    # Set sizes for each atom (in Angstroms)
    radius = {'H' : 0.30,
              'He': 0.99,
              'Li': 1.52,
              'Be': 1.12,
              'B' : 0.88,
              'C' : 0.77,
              'N' : 0.70,
              'O' : 0.66,
              'F' : 0.64,
              'Ne': 1.60,
              'Na': 1.86,
              'Mg': 1.60,
              'Al': 1.43,
              'Si': 1.17,
              'P' : 1.10,
              'S' : 1.04,
              'Cl': 0.99,
              'Ar': 1.92,
              'K' : 2.31,
              'Ca': 1.97,
              'Sc': 1.60,
              'Ti': 1.46,
              'V' : 1.31,
              'Cr': 1.25,
              'Mn': 1.29,
              'Fe': 1.26,
              'Co': 1.25,
              'Ni': 1.24,
              'Cu': 1.28,
              'Zi': 1.33,
              'Ga': 1.41,
              'Ge': 1.22,
              'As': 1.21,
              'Se': 1.17,
              'Br': 1.14,
              'Kr': 1.97,
              'Rb': 2.44,
              'Sr': 2.15,
              'Y' : 1.80,
              'Zr': 1.57,
              'Nb': 1.41,
              'Mo': 1.36,
              'Tc': 1.35,
              'Ru': 1.33,
              'Rh': 1.34,
              'Pd': 1.38,
              'Ag': 1.44,
              'Cd': 1.49,
              'In': 1.66,
              'Sn': 1.62,
              'Sb': 1.41,
              'Te': 1.37,
              'I' : 1.33,
              'Xe': 2.17,
              'Cs': 2.62,
              'Ba': 2.17,
              'La': 1.88,
              'Ce': 1.818,
              'Pr': 1.824,
              'Nd': 1.814,
              'Pm': 1.834,
              'Sm': 1.804,
              'Eu': 2.084,
              'Gd': 1.804,
              'Tb': 1.773,
              'Dy': 1.781,
              'Ho': 1.762,
              'Er': 1.761,
              'Tm': 1.759,
              'Yb': 1.922,
              'Lu': 1.738,
              'Hf': 1.57,
              'Ta': 1.43,
              'W' : 1.37,
              'Re': 1.37,
              'Os': 1.34,
              'Ir': 1.35,
              'Pt': 1.38,
              'Au': 1.44,
              'Hg': 1.52,
              'Tl': 1.71,
              'Pb': 1.75,
              'Bi': 1.70,
              'Po': 1.40,
              'At': 1.40,
              'Rn': 2.40,
              'Fr': 2.70,
              'Ra': 2.20,
              'Ac': 2.00,
              'Th': 1.79,
              'Pa': 1.63,
              'U' : 1.56
             }
    # These are the physical values for atomic radii.  If not known, the above
    # value is used.  The ones that are real are marked.
    real_radius = {'H' : 1.20, #
              'He': 1.40, #
              'Li': 1.82, #
              'Be': 1.12,
              'B' : 0.88,
              'C' : 1.70, #
              'N' : 1.55, #
              'O' : 1.52, #
              'F' : 1.47, #
              'Ne': 1.54, #
              'Na': 2.27, #
              'Mg': 1.73, #
              'Al': 1.43,
              'Si': 2.10, #
              'P' : 1.80, #
              'S' : 1.80, #
              'Cl': 1.75, #
              'Ar': 1.88, #
              'K' : 2.75, #
              'Ca': 1.97,
              'Sc': 1.60,
              'Ti': 1.46,
              'V' : 1.31,
              'Cr': 1.25,
              'Mn': 1.29,
              'Fe': 1.26,
              'Co': 1.25,
              'Ni': 1.63, #
              'Cu': 1.40, #
              'Zi': 1.39, #
              'Ga': 1.87, #
              'Ge': 1.22,
              'As': 1.85, #
              'Se': 1.90, #
              'Br': 1.85, #
              'Kr': 2.02, #
              'Rb': 2.44,
              'Sr': 2.15,
              'Y' : 1.80,
              'Zr': 1.57,
              'Nb': 1.41,
              'Mo': 1.36,
              'Tc': 1.35,
              'Ru': 1.33,
              'Rh': 1.34,
              'Pd': 1.63, #
              'Ag': 1.72, #
              'Cd': 1.58, #
              'In': 1.93, #
              'Sn': 2.17, #
              'Sb': 1.41,
              'Te': 1.37,
              'I' : 1.98, #
              'Xe': 2.16, #
              'Cs': 2.62,
              'Ba': 2.17,
              'La': 1.88,
              'Ce': 1.818,
              'Pr': 1.824,
              'Nd': 1.814,
              'Pm': 1.834,
              'Sm': 1.804,
              'Eu': 2.084,
              'Gd': 1.804,
              'Tb': 1.773,
              'Dy': 1.781,
              'Ho': 1.762,
              'Er': 1.761,
              'Tm': 1.759,
              'Yb': 1.922,
              'Lu': 1.738,
              'Hf': 1.57,
              'Ta': 1.43,
              'W' : 1.37,
              'Re': 1.37,
              'Os': 1.34,
              'Ir': 1.35,
              'Pt': 1.75, #
              'Au': 1.66, #
              'Hg': 1.55, #
              'Tl': 2.06, #
              'Pb': 2.02, #
              'Bi': 1.70,
              'Po': 1.40,
              'At': 1.40,
              'Rn': 2.40,
              'Fr': 2.70,
              'Ra': 2.20,
              'Ac': 2.00,
              'Th': 1.96, #
              'Pa': 1.63,
              'U' : 1.86  #
              }
    
    if element is None:
        return None
    else:
        return (radius[element], real_radius[element])

# This function returns a mass.
def atomic_mass(element):
    """Return the mass of the most common isotope of the selected element."""

    # Set mass for each atom
    mass = {'H' :  1.007825,
            'He':  4.002603,
            'Li':  7.016004,
            'Be':  9.012182,
            'B' : 11.009305,
            'C' : 12.000000,
            'N' : 14.003074,
            'O' : 15.994914,
            'F' : 18.998403,
            'Ne': 19.992440,
            'Na': 22.989769,
            'Mg': 23.985041,
            'Al': 26.981538,
            'Si': 27.976926,
            'P' : 30.973761,
            'S' : 31.972070,
            'Cl': 34.968852,
            'Ar': 39.962383,
            'K' : 38.963706,
            'Ca': 39.962591,
            'Sc': 44.955910,
            'Ti': 47.947947,
            'V' : 50.943963,
            'Cr': 51.849511,
            'Mn': 54.938049,
            'Fe': 55.934941,
            'Co': 58.933199,
            'Ni': 57.935347,
            'Cu': 62.929600,
            'Zi': 63.929146,
            'Ga': 68.925581,
            'Ge': 73.921178,
            'As': 74.921596,
            'Se': 79.916522,
            'Br': 78.918337,
            'Kr': 83.911508,
            'Rb': 84.911792,
            'Sr': 87.905616,
            'Y' : 88.905848,
            'Zr': 89.904702,
            'Nb': 92.906376,
            'Mo': 97.905406,
            'Tc': 98.000000,
            'Ru': 101.904348,
            'Rh': 102.905504,
            'Pd': 105.903484,
            'Ag': 106.905093,
            'Cd': 113.903358,
            'In': 114.903879,
            'Sn': 119.902198,
            'Sb': 120.903822,
            'Te': 129.906222,
            'I' : 126.904468,
            'Xe': 131.904154,
            'Cs': 132.905447,
            'Ba': 137.905242,
            'La': 138.906349,
            'Ce': 139.905435,
            'Pr': 140.907648,
            'Nd': 141.907719,
            'Pm': 145.000000,
            'Sm': 151.919729,
            'Eu': 152.921227,
            'Gd': 157.924101,
            'Tb': 158.925343,
            'Dy': 163.929171,
            'Ho': 164.930319,
            'Er': 165.930290,
            'Tm': 168.934211,
            'Yb': 173.938858,
            'Lu': 174.940768,
            'Hf': 179.946548,
            'Ta': 180.947996,
            'W' : 183.950932,
            'Re': 186.955750,
            'Os': 191.961479,
            'Ir': 192.962923,
            'Pt': 194.964774,
            'Au': 196.966551,
            'Hg': 201.970625,
            'Tl': 204.974412,
            'Pb': 207.976636,
            'Bi': 208.980384,
            'Po': 209.000000,
            'At': 210.000000,
            'Rn': 222.000000,
            'Fr': 223.000000,
            'Ra': 226.000000,
            'Ac': 227.000000,
            'Th': 232.038049,
            'Pa': 231.035878,
            'U' : 238.050783
           }

    if element is None:
        return None
    else:
        return mass[element]

# This function returns a number or element.
def atomic_number(element):
    '''Return the atomic number if given an element,
    or the symbol if given a number.'''   

    # First, assume an integer was given
    try:
        try:
            return elem[int(element)]
        except IndexError:
            import sys
            sys.exit('Symbol for element '+str(element)+' is not implemented.')
    # If that didn't work, then it must be the symbol
    except ValueError:
        try:
            return elem.index(element)
        except ValueError:
            import sys
            sys.exit('Element '+element+' is not implemented.')
