from __future__ import print_function, division
from sys import exit
from math import sqrt
from scipy.linalg import eig, inv
from scipy.special import wofz
from numpy.fft import fft, fftshift, fftfreq
from numpy import array, arange, argmin, argsort, diag
from numpy import dot, exp, eye, log, where, zeros, zeros_like
from constants import PI

def K_matrix(peak_exchanges, exchange_rates, k, npeaks):
    '''Constructs the K (exchange) matrix of the rates'''
    Z = zeros((npeaks, npeaks))

    # Place the exchanges symmetrically
    for index, rate in zip(peak_exchanges, exchange_rates):
        Z[index[0],index[1]] = rate
        Z[index[1],index[0]] = rate

    # The diagonals must be 1 minus the sum of the off diagonals for that row
    sums = zeros(npeaks)
    for i in xrange(npeaks):
        sums[i] = sum(Z[i,:])
        Z[i,i]  = 1 - sums[i]

    # Now, if any of the sums are greater than 1, normalize
    if any(sums > 1):
        Z /= sums.max()

    return k * ( Z - eye(npeaks) )

def spectrum(args, K):
    '''This routine contains the code that drives the actual calculation
    of the intensities.  The already constructed K matrix and the input
    arguments are given.'''

    # Use the exchange matrix to find S and Lambda
    S, Sinv, Lambda = S_and_Lambda(args.vib, args.Gamma_Lorentz, K)

    # Calculate Gprimed
    Gprime = G_prime(S, Sinv, args.Gamma_Gauss)

    # Now, determine the spectrum in the frequency domain.
    # The frequencies are in wavenumbers.
    return intensities(args, Lambda, S, Sinv, Gprime, args.heights)

def S_and_Lambda(vib, Gamma_Lorentz, K):
    '''Construct the A matrix and then find the eigenvectors and the
    eigenvalues, which are the S and Lambda matricies, respectively.'''
    A = diag(-1j * vib + 0.5 * Gamma_Lorentz) - K
    #A = diag(-1j * vib + Gamma_Lorentz) - K
    Lambda, S = eig(A)
    # Return in ascending order
    indx = argsort(abs(Lambda.imag))
    return S[:,indx], inv(S[:,indx]), Lambda[indx]

def G_prime(S, Sinv, Gamma_Gauss):
    '''Calculates the G primed matrix from S and the Gaussian Gamma.'''

    # Convert Gamma_Gauss to sigma
    sigma = Gamma_Gauss / ( sqrt(2 * log(2)) * 2 )

    G = diag(sigma**(-2))
    # Off-diagonals are zero
    Gp = array(diag(dot(dot(Sinv, G), S)), dtype=complex).real
    # Sometimes the Gaussians end up negative.  This is a problem.
    if any(Gp < 0):
        exit('The input parameters for this system are not physical.\n'
             'Try increasing the Gaussian line widths')
    else:
        return Gp

def voigt(freq, height, vib, Gamma_Lorentz, sigma):
    '''Return a Voigt line shape over a given domain about a given vib'''

    # Define what to pass to the complex error function
    z = ( freq - vib + 1j*Gamma_Lorentz ) / ( sqrt(2) * sigma )
    # The Voigt is the real part of the complex error function with some
    # scaling factors.  It is multiplied by the height here.
    return ( height.conjugate() * wofz(z) ).real / ( sqrt(2 * PI) * sigma )

def intensities(args, Lambda, S, Sinv, Gprime, heights):
    '''Calculates the spectral intensities.  
    In addition to the intensities,  the fruequencies are returned as well'''

    # Frequency domain over interesting region
    omega = arange(200, 3000, 0.5)

    # Table header, if it is requested
    if isinstance(args.save_plot_script, file):
        print(file=args.save_plot_script)
        print('#'+' '*16 + 'Input Values'.center(25) + 'New Values'.center(30),
              file=args.save_plot_script)
        print('# '+'-'*70, file=args.save_plot_script)

    # For this frequency range, calculate the spectrum, one for each vibration
    spectrum = zeros_like(omega)
    N = range(len(heights))
    for j in N:

        # Extract the omega, Lorenzian gamma, and Gaussian gamma
        w, gamma, sigma = -Lambda[j].imag, Lambda[j].real, 1 / sqrt(Gprime[j])

        # Determine the peak heights
        h = sum([heights[a] * S[a,j] * Sinv[j,ap] for a in N for ap in N])

        # Use a Voigt profile to go from time domain to frequency domain
        spectrum += voigt(omega, h, w, gamma, sigma)

        # If requested, put this info into a file
        if isinstance(args.save_plot_script, file):
            numerics(j, args, w, gamma, sigma, h.real)

    # Print an extra space if printing to file
    if isinstance(args.save_plot_script, file):
        print(file=args.save_plot_script)

    return spectrum, omega

def numerics(i, args, omega, gamma, sigma, height):
    '''Prints out a table of the data.'''

    print('#', file=args.save_plot_script)
    sr = '# {0:15}:{1:^25g}{2:^30g}'
    print(sr.format('Omega', args.vib[i], omega),
          file=args.save_plot_script)
    # Convert from HWHM to FWHM
    print(sr.format('Gamma Lorentz', args.Gamma_Lorentz[i], 2 * gamma),
          file=args.save_plot_script)
    # Convert from sigma to FWHM
    print(sr.format('Gamma Gauss', args.Gamma_Gauss[i], 
                                   sigma * sqrt(2 * log(2)) * 2),
          file=args.save_plot_script)
    print(sr.format('Rel. Height', args.heights[i], height),
          file=args.save_plot_script)
