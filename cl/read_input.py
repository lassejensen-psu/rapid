from __future__ import print_function
from sys import exit, stdout
from math import pi
from numpy import array, loadtxt
from input_reader import InputReader, SUPPRESS, ReaderError, \
                         range_check, abs_file_path
HZ2WAVENUM = 1 / ( 100 * 2.99792458E8 ) # Hz to cm^{-1} conversion
Fs = 1E-15                              # Femptoseconds

__all__ = ['read_input', 'ReaderError']

def read_input(input_file):
    '''Defines what to expect from the input file and then
    reads it in.'''

    # Creates an input reader instance
    reader = InputReader(default=SUPPRESS)

    # Rate parameter, either rate or lifetime, not both
    rate = reader.add_mutually_exclusive_group(required=True)
    # The units are s, ns, ps, or fs.  The default is ps.
    unitglob = {'len' : '?',
                'type' : ('ps', 'fs', 'ns', 's'),
                'default' : 'ps'}
    rate.add_line_key('lifetime', type=float, glob=unitglob)
    rate.add_line_key('rate',     type=float, glob=unitglob)

    # The range of the X-axis
    reader.add_line_key('xlim', type=[float, float], default=(1900.0, 2000.0))
    reader.add_boolean_key('reverse', action=True, default=False)

    # Plot data to screen,output to txt file, or to a script.
    # The default is to screen.
    outformat = reader.add_mutually_exclusive_group()
    outformat.add_line_key('data', type=str, case=True)
    outformat.add_line_key('save_plot_script', type=str, case=True)
    outformat.add_boolean_key('parameters', action=True, default=False)

    # Read in the raw data.  
    reader.add_line_key('raw', type=[], glob={'len':'*', 'join':True, },
                               default=None, case=True)

    # Read in the peak data.  The wavenumber and height is required.
    # The Lorentzian and Gaussian widths are defaulted to 10 if not given.
    floatkw = {'type' : float, 'default' : 10.0}
    reader.add_line_key('peak', required=True, repeat=True, type=[float,float],
                                keywords={'g':floatkw, 'l':floatkw,
                                          'num' : {'type':int,'default':-1}})

    # Read the exchange information.
    reader.add_line_key('exchange', repeat=True, type=[int, int],
                                    glob={'type' : float,
                                          'default' : 1.0,
                                          'len' : '?'})

    # Actually read the input file
    args, ifile = reader.read_input(input_file)

    # Make sure the filename was given correctly and read in data
    if args.raw:
        args.raw = loadtxt(abs_file_path(args.raw))

    # Make the output file path absolute if given
    if 'data' in args:
        args.data = abs_file_path(args.data)

    # Output a script to replot
    if 'save_plot_script' in args:
        args.save_plot_script = open(abs_file_path(args.save_plot_script), 'w')
    else:
        args.save_plot_script = None

    # Adjust the input rate or lifetime to wavenumbers
    if 'lifetime' in args:
        convert = { 'ps' : 1E-12, 'ns' : 1E-9, 'fs' : 1E-15, 's' : 1 }
        args.add('k', 1 / ( convert[args.lifetime[1]] * args.lifetime[0] ))
    else:
        convert = { 'ps' : 1E12, 'ns' : 1E9, 'fs' : 1E15, 's' : 1 }
        args.add('k', convert[args.rate[1]] * args.rate[0])
    args.k *= HZ2WAVENUM / ( 2 * pi )

    # Parse the vibrational input
    num, vib, Gamma_Lorentz, Gamma_Gauss, heights, rel_rates, num_given = (
                                                    [], [], [], [], [], [], [])
    for peak in args.peak:
        # Vibration #
        num.append(peak[2]['num'])
        num_given.append(False if peak[2]['num'] < 0 else True)
        # Angular frequency
        vib.append(peak[0])
        # Relative peak heights
        heights.append(peak[1])
        # Default Gaussian or Lorentzian width or relative rate
        Gamma_Lorentz.append(peak[2]['l'])
        Gamma_Gauss.append(peak[2]['g'])

    # Either all or none of the numbers must be given explicitly
    if not (all(num_given) or not any(num_given)):
        exit('All or none of the peaks must be given numbers explicitly')
    # If the numbers were give, make sure there are no duplicates
    if all(num_given):
        if len(num) != len(set(num)):
            exit('Duplicate peaks cannot be given')
    # If none were given, number automatically
    else:
        num = range(1, len(num)+1, 1)

    args.add('num', array(num))
    args.add('vib', array(vib))
    args.add('heights', array(heights))
    args.add('Gamma_Lorentz', array(Gamma_Lorentz))
    args.add('Gamma_Gauss', array(Gamma_Gauss))

    # Set up the exchanges
    # Make sure the each exchange number appears in num.
    num = set(num)
    ex = []
    rates = []
    string = 'Requested peak {0} in exchange does not exist'
    if 'exchange' in args:
        for exchange in args.exchange:
            p1 = exchange[0]
            if p1 not in num:
                exit(string.format(p1))
            p2 = exchange[1]
            if p2 not in num:
                exit(string.format(p2))
            if p1 == p2:
                exit('Self exchange is not allowed')
            rate = exchange[2]
            # Offset the peak number by one to match python indicies
            ex.append([p1-1, p2-1])
            rates.append(rate)
    else:
        ex = []
        rates = []
    args.add('exchanges', array(ex, dtype=int))
    args.add('exchange_rates', array(rates))

    # Make sure the xlimits are asending
    try:
        range_check(args.xlim[0], args.xlim[1])
    except ValueError:
        raise ReaderError('In xrange, the low value must '
                          'less than the high value')

    return args
