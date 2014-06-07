from __future__ import print_function, division, absolute_import

# Std. lib imports
from sys import stderr


def plot(args, x, y):
    '''Plots the normalized data.'''
    try:
        from matplotlib.pyplot import rc, plot, xlim, ylim, \
                                      xlabel, ylabel, show
    except ImportError:
        print('It appears that you are missing matplotlib.', file=stderr)
        print('You should install it using your favorite method', file=stderr)
        return 1
    
    # 14 point font size
    rc('font', **{'size': 14})

    # Plot the data and set the data window
    if args.raw is not None:
        plot(x, y, 'b-', args.raw[:,0], args.raw[:,1], 'g-', lw=1.5)
    else:
        plot(x, y, 'b-', lw=1.5)
    if args.reverse:
        xlim(args.xlim[1], args.xlim[0])
    else:
        xlim(args.xlim[0], args.xlim[1])
    ylim(-0.1, 1.2)
    xlabel('Wavenumbers')
    ylabel('Intensity (Normalized)')
    show()
    return 0
