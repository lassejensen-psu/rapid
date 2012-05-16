from __future__ import print_function, division
from sys import stderr
from numpy import where, savetxt, array

def write_data(x, y, datafile):
    '''Writes the normalized data to file.'''

    # Write the data to file. 
    savetxt(str(datafile), array([x, y]).T, fmt='%.1f %.16f')

def numerics(old_params, new_params, out):
    '''Make a nice table of the old and new data'''

    # Extract values
    N = range(len(old_params[0]))
    vib = [(old_params[0][i], new_params[0][i]) for i in N]
    GL  = [(old_params[1][i], new_params[1][i]) for i in N]
    GG  = [(old_params[2][i], new_params[2][i]) for i in N]
    h   = [(old_params[3][i], new_params[3][i]) for i in N]

    # Write to specified location
    sr = '# {0:15}:{1[0]:^25g}{1[1]:^30g}'
    for i in N:
        print('#', file=out)
        print(sr.format('Omega',         vib[i]), file=out)
        print(sr.format('Gamma Lorentz', GL[i]),  file=out)
        print(sr.format('Gamma Gauss',   GG[i]),  file=out)
        print(sr.format('Rel. Height',   h[i]),   file=out)
    return 0

def normalize(y):
    '''Normalizes a data set.  Clips according to x-values if given.''' 
    # Set baseline to zero.
    y = y - y.min()
    # Normalize
    return y / y.max()

def clip(xy, xlimits):
    '''Clips according to x-values.'''
    xy = xy[where(xy[:,0] > xlimits[0])]
    return xy[where(xy[:,0] < xlimits[1])]
