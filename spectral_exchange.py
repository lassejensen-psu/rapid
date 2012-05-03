from __future__ import print_function, division
from sys import argv, exit
from textwrap import dedent
from numpy import where, set_string_function

# These are imported from files in this folder
from read_input import read_input, ReaderError
from intensities import K_matrix, spectrum

def main():
    '''This routine conatins the code that drives the actual calculation.'''

    # Read in the input file that is given
    try:
        args = read_input(argv[1])
    except IndexError:
        exit('No input file given!')
    except (OSError, IOError) as e:
        exit(str(e)) # An error occured when locating the file
    except ReaderError as r:
        exit(str(r)) # An error occured when reading the file

    # Construct the K (exchange) matrix
    K = K_matrix(args.exchanges, args.exchange_rates, args.k, args.vib.size)

    # Use the K matrix and the input to calculate the spectrum
    I_omega, omega = spectrum(args, K)

    # Plot the data or write to file
    if 'data' in args:
        write(args, omega, I_omega)
    elif args.parameters:
        pass
    elif isinstance(args.save_plot_script, file):
        save_script(args, omega, I_omega)
        args.save_plot_script.close()
    else:
        plot(args, omega, I_omega)


def plot(args, x, y):
    '''Plots the normalized data.'''
    from matplotlib.pyplot import rc, plot, xlim, ylim, xlabel, ylabel, show
    
    # Normalize the generated data
    y = normalize(y)
    # Repeat for the raw data if given.  Clip according to the xlimits
    if args.raw is not None:
        args.raw = clip(args.raw, args.xlim)
        args.raw[:,1] = normalize(args.raw[:,1])

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

def save_script(args, x, y):
    '''Saves a python script capable of generating a plot of the parameters'''
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

###############
# Run program #
###############

if __name__ == '__main__':
    main()
