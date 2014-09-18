from __future__ import print_function, division, absolute_import

# Std. lib imports
from sys import stderr, stdout

# Non-std. lib imports
from numpy import arange
from input_reader import ReaderError

# Local imports
from rapid.common import spectrum, SpectrumError, ZMat, normalize, clip, \
                     numerics, write_data, save_script, read_input
from rapid.cl.plot import plot


def run_non_interactive(cmd_line_args):
    '''Driver to calculate the spectra non-interactively
    (i.e. from the command line).
    '''

    # Read in the input file that is given
    try:
        args = read_input(cmd_line_args.input_file)
    except (OSError, IOError) as e:
        print(str(e), file=stderr) # An error occurred when locating the file
        return 1
    except ReaderError as r:
        print(str(r), file=stderr) # An error occurred when reading the file
        return 1

    # Generate the Z matrix
    Z = ZMat(len(args.num), args.exchanges, args.exchange_rates,
             args.symmetric_exchange)

    # Generate the frequency domain
    omega = arange(args.xlim[0]-10, args.xlim[1]+10, 0.5)

    # Calculate the spectrum
    try:
        I_omega, new_params = spectrum(Z,
                                       args.k,
                                       args.vib,
                                       args.Gamma_Lorentz,
                                       args.Gamma_Gauss,
                                       args.heights,
                                       omega
                                      )
    except SpectrumError as se:
        print(str(se), file=stderr)
        return 1

    # Make a tuple of the old parameters
    old_params = (args.vib,
                  args.Gamma_Lorentz,
                  args.Gamma_Gauss,
                  args.heights)

    # Normalize the generated data
    I_omega = normalize(I_omega)
    # Repeat for the raw data if given.  Clip according to the xlimits
    if args.raw is not None:
        args.raw = clip(args.raw, args.xlim)
        args.raw[:,1] = normalize(args.raw[:,1])

    # Plot the data or write to file
    if cmd_line_args.data:
        try:
            write_data(omega, I_omega, cmd_line_args.data)
        except (IOError, OSError) as e:
            print(str(e), file=stderr)
            return 1
        else:
            print('Data written to file {0}'.format(cmd_line_args.data))
            return 0
    elif cmd_line_args.script:
        return save_script(omega, I_omega, args.raw, args.xlim, args.reverse,
                           old_params, new_params, cmd_line_args.script,
                           msg=True)
    elif cmd_line_args.params:
        return numerics(old_params, new_params, stdout)
    else:
        return plot(args, omega, I_omega)
