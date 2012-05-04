from __future__ import print_function, division
from .common import normalize, clip

def write(args, x, y):
    '''Writes the normalized data to file.'''

    # Write the data to file. 
    try:
        f = open(args.data, 'w')
    except (IOError, OSError) as e:
        exit(str(e)) # Error writing file to disk

    # Write the arrays line by line in reverse order
    for xd, yd in reversed(zip(x, y)):
        print('{0:17.10E} {1:17.10E}'.format(xd, yd), file=f)
    f.close()
    print('Data written to file {0}'.format(args.data))
    return 0

def numerics(old_params, new_params, out):
    '''Make a nice table of the old and new data'''

    N = range(len(old_params[0]))
    vib = [old_params[0][i], new_params[0][i] for i in N]
    GL  = [old_params[1][i], new_params[1][i] for i in N]
    GG  = [old_params[2][i], new_params[2][i] for i in N]
    h   = [old_params[3][i], new_params[3][i] for i in N]

    sr = '# {0:15}:{1:^25g}{2:^30g}'
    for i in N:
        print('#', file=out)
        print(sr.format('Omega', args.vib[i], omega),
              file=args.save_plot_script)
        print(sr.format('Gamma Lorentz', args.Gamma_Lorentz[i], 2 * gamma),
              file=args.save_plot_script)
        print(sr.format('Gamma Gauss', args.Gamma_Gauss[i], 
                                   sigma * sqrt(2 * log(2)) * 2),
          file=args.save_plot_script)
        print(sr.format('Rel. Height', args.heights[i], height),
          file=args.save_plot_script)
        

def save_script(args, x, y):
    '''Saves a python script capable of generating a plot of the parameters'''

    # Output a script to replot
    if 'save_plot_script' in args:
        args.save_plot_script = open(abs_file_path(args.save_plot_script), 'w')
        print('#! /usr/bin/env python', file=args.save_plot_script)
        print('from __future__ import print_function, division',
              file=args.save_plot_script)
        print('from pylab import *', file=args.save_plot_script)
    elif args.parameters:
        args.save_plot_script = stdout
    else:
        args.save_plot_script = None

    # Table header, if it is requested
    if isinstance(args.save_plot_script, file):
        print(file=args.save_plot_script)
        print('#'+' '*16 + 'Input Values'.center(25) + 'New Values'.center(30),
              file=args.save_plot_script)
        print('# '+'-'*70, file=args.save_plot_script)

def numerics(i, args, omega, gamma, sigma, height):
    '''Prints out a table of the data.'''

    print('#', file=args.save_plot_script)
    sr = '# {0:15}:{1:^25g}{2:^30g}'

    string = dedent("""\
                    def make_plot():
                        '''Plots the data contained in this script.'''

                        # 14 point font size
                        rc('font', **{{'size': 14}})

                        # Actually plot the data
                        {plot}

                        # You can manually edit the x- and y-axis limits
                        xlim({xmin}, {xmax})
                        ylim(-0.1, 1.2)

                        # You can manually edit the x- and y-axis labels
                        xlabel('Wavenumbers')
                        ylabel('Intensity (Normalized)')

                        # Uncomment the below line to add a title
                        #title('Your Title Here')

                        # Show the plot on the screen
                        show()
                    """)

    # Determine how to plot
    if args.raw is not None:
        plot = "plot(x, y, 'b-', xraw, yraw, 'g-', lw=1.5)"
    else:
        plot = "plot(x, y, 'b-', lw=1.5)"

    # Print what we have so far to file        
    if args.reverse:
        print(string.format(xmin=args.xlim[1], xmax=args.xlim[0], plot=plot),
              file=args.save_plot_script)
    else:
        print(string.format(xmin=args.xlim[0], xmax=args.xlim[1], plot=plot),
              file=args.save_plot_script)

    # Define a function that allows us to print off the arrays how we want
    def pprint(arr):
        string = 'array(['
        for v in arr:
            string += str(v)+',\n'
        string += '])'
        return string
    set_string_function(pprint, repr=False)

    # Print off the arrays
    print('# The frequencies for the predicted spectra',
          file=args.save_plot_script)
    print('x =', x, file=args.save_plot_script)
    print('y =', normalize(y), file=args.save_plot_script)

    # Print off raw data arrays if necessary
    if args.raw is not None:
        args.raw = clip(args.raw, args.xlim)
        args.raw[:,1] = normalize(args.raw[:,1])
        print('xraw =', args.raw[:,0], file=args.save_plot_script)
        print('yraw =', args.raw[:,1], file=args.save_plot_script)

    # Finally, print off the part that executes the plotting code
    print(dedent('''
                 if __name__ == '__main__':
                     make_plot()
                 '''), file=args.save_plot_script)

def normalize(y, x=None, xlimits=None):
    '''Normalizes a data set.  Clips according to x-values if given.''' 
    # Set baseline to zero.
    y = y - y.min()
    # Normalize
    return y / y.max()

def clip(xy, xlimits):
    '''Clips according to x-values.'''
    xy = xy[where(xy[:,0] > xlimits[0])]
    return xy[where(xy[:,0] < xlimits[1])]
