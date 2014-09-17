from __future__ import print_function, division, absolute_import

# Std. lib imports
from textwrap import dedent

# Non-std. lib imports
from numpy import set_string_function

# Local imports
from .utils import numerics


def save_script(x, y, raw, xlim, reverse, old_params, new_params, scriptfile, msg=False):
    '''Saves a python script capable of generating a plot of the parameters'''

    # Output a script to re-plot
    out = open(scriptfile, 'w')

    # Make the file header
    title = '#'+' '*16 + 'Input Values'.center(25) + 'New Values'.center(30)
    spacer = '# '+'-'*70
    print(dedent('''\
    #! /usr/bin/env python
    from __future__ import print_function, division
    from pylab import *

    {title}
    {spacer}\
    ''').format(title=title, spacer=spacer), file=out)

    # Write a table of the parameters
    numerics(old_params, new_params, out)

    # Determine how to plot
    if raw is not None:
        plot = "plot(x, y, 'b-', xraw, yraw, 'g-', lw=1.5)"
    else:
        plot = "plot(x, y, 'b-', lw=1.5)"

    # Set the x limits properly
    if reverse:
        xlim = xlim[1], xlim[0]

    # Print this function to file
    print(dedent("""\

                 def make_plot():
                     '''Plots the data contained in this script.'''

                     # 14 point font size
                     rc('font', **{{'size': 14}})

                     # Actually plot the data
                     {plot}

                     # You can manually edit the x- and y-axis limits
                     xlim({xmin}, {xmax})
                     ylim(-0.05, 1.1)

                     # You can manually edit the x- and y-axis labels
                     xlabel('Wavenumbers')
                     ylabel('Intensity (Normalized)')

                     # Uncomment the below line to add a title
                     #title('Your Title Here')

                     # Show the plot on the screen
                     show()
                 """).format(plot=plot, xmin=xlim[0], xmax=xlim[1]), file=out)

    # Define a function that allows us to print off the arrays how we want
    def pprint(arr):
        string = 'array(['
        for v in arr:
            string += str(v)+',\n'
        string += '])'
        return string
    set_string_function(pprint, repr=False)

    # Print off the arrays
    print('# The frequencies for the predicted spectra', file=out)
    print('x =', x, file=out)
    print('y =', y, file=out)

    # Print off raw data arrays if necessary
    if raw is not None:
        print('xraw =', raw[:,0], file=out)
        print('yraw =', raw[:,1], file=out)

    # Finally, print off the part that executes the plotting code
    print(dedent('''\

                 if __name__ == '__main__':
                     make_plot()
                 '''), file=out)

    # Close the file
    out.close()

    if msg:
        print('Data written to file {0}'.format(scriptfile))

    return 0
