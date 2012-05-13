from __future__ import print_function
from sys import stderr, stdout
from numpy import arange

def run_non_interactive(input_file):
    '''Driver to calculate the spectra non-interactively
    (i.e. from the command line).
    '''
    # Import needed functions.  Do so here to handle errors better
    try:
        from input_reader import ReaderError
    except ImportError:
        print("Cannot find input_reader module", file=stderr)
        print("Find it at github.com/SethMMorton/input_reader", file=stderr)
        return 1
    from common import spectrum, SpectrumError, ZMat, \
                       numerics, write_data, save_script, read_input
    from plot import plot

    # Read in the input file that is given
    try:
        args = read_input(input_file)
    except (OSError, IOError) as e:
        print(str(e), file=stderr) # An error occured when locating the file
        return 1
    except ReaderError as r:
        print(str(r), file=stderr) # An error occured when reading the file
        return 1

    # Generate the Z matrix
    Z = ZMat(len(args.vib), args.exchanges, args.exchange_rates, True)

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

    # Plot the data or write to file
    if args.data:
        return write_data(omega, I_omega, args.data)
    elif args.save_plot_script:
        return save_script(omega, I_omega, args.raw, args.xlim, args.reverse,
                           old_params, new_params, args.save_plot_script)
    elif args.parameters:
        return numerics(old_params, new_params, stdout)
    else:
        return plot(args, omega, I_omega)
