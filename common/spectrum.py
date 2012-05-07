from __future__ import division
from sys import exit
from math import sqrt, log, pi
from scipy.linalg import eig, inv
from scipy.special import wofz
from numpy import array, arange, argsort, diag, dot, eye, zeros

# A few constats
SQRT2LOG2_2 = sqrt(2 * log(2)) * 2
INVSQRT2LOG2_2 = 1 / SQRT2LOG2_2
SQRT2 = sqrt(2)
SQRT2PI = sqrt(2 * pi)

# Frequency domain over interesting region
omega = arange(200, 3000, 0.5)

def ZMat(npeaks, peak_exchanges, relative_rates, symmetric):
    '''Construct the Z matrix.  Symmetry can be enforced or not.'''

    Z = zeros((npeaks, npeaks))

    if symmetric:
        # Place the relative exchange rates symmetrically in Z
        for index, rate in zip(peak_exchanges, relative_rates):
            Z[index[0],index[1]] = rate
            Z[index[1],index[0]] = rate

        # The diagonals of Z must be 1 minus the sum
        # of the off diagonals for that row
        sums = zeros(npeaks)
        for i in xrange(npeaks):
            sums[i] = sum(Z[i,:])
            Z[i,i]  = 1 - sums[i]

        # Now, if any of the sums are greater than 1, normalize
        if any(sums > 1):
            Z /= sums.max()
    else:
        # Place the relative exchange rates in Z
        for index, rate in zip(peak_exchanges, relative_rates):
            Z[index[0],index[1]] = rate
        
    return Z

def spectrum(Z, k, vib, Gamma_Lorentz, Gamma_Gauss, heights):
    '''This routine contains the code that drives the actual calculation
    of the intensities.
    '''
    npeaks = len(vib)
    N = range(npeaks)

    # Multiply Z-I by k to get K
    K = k * ( Z - eye(npeaks) )

    ############################
    # Find S, S^{-1}, and Lambda
    ############################

    # Construct the A matrix from K, the vibrational frequencies,
    # and the Lorentzian HWHM
    A = diag(-1j * vib + 0.5 * Gamma_Lorentz) - K
    # Lambda is the eigenvalues of A, S is the eigenvectors
    Lambda, S = eig(A)
    # Since the eigens are unordered, order by
    # the imaginary part of Lambda
    indx = argsort(abs(Lambda.imag))
    S, Sinv, Lambda = S[:,indx], inv(S[:,indx]), Lambda[indx]

    #################################
    # Use S and S^{-1} to find Gprime
    #################################

    # Convert Gamma_Gauss to sigma
    sigma = Gamma_Gauss * INVSQRT2LOG2_2

    # Construct the G matrix from sigma,
    # then use S and S^{-1} to get Gprime
    G = diag(sigma**(-2))
    # Off-diagonals are zero
    Gprime = array(diag(dot(dot(Sinv, G), S)), dtype=complex).real

    ##########################################
    # Construct an array of the new parameters
    ##########################################

    h = [height(j, heights, S, Sinv) for j in N]
    peaks = [-x.imag for x in Lambda]
    HWHM  = [x.real for x in Lambda]
    try:
        sigmas = [1 / sqrt(x) for x in Gprime]
    except ValueError:
        # I'm not sure this is a problem anymore, but this happened at some
        # stage of developement
        raise SpectrumError('The input parameters for this system are '
                            'not physical.\nTry increasing the Gaussian '
                            'line widths')
    # Also create the modified input parameters for return
    GL = [2 * x for x in HWHM]
    GG = [SQRT2LOG2_2 * x for x in sigmas]
    new_params = peaks, GL, GG, [x.real for x in h]

    ###############################################
    # Use these new values to calucate the spectrum
    ###############################################

    # Return the sum of voigt profiles for each peak,
    # along with the omega array and new parameters
    return (array([voigt(omega, j, h, peaks, HWHM, sigmas) for j in N]).sum(0),
            omega,
            new_params)

def voigt(freq, j, height, vib, HWHM, sigma):
    '''Return a Voigt line shape over a given domain about a given vib'''

    # Define what to pass to the complex error function
    z = ( freq - vib[j] + 1j*HWHM[j] ) / ( SQRT2 * sigma[j] )
    # The Voigt is the real part of the complex error function with some
    # scaling factors.  It is multiplied by the height here.
    return ( height[j].conjugate() * wofz(z) ).real / ( SQRT2PI * sigma[j] )

def height(j, heights, S, Sinv):
    '''Return the modified peak height'''
    N = range(len(heights))
    return sum([heights[a] * S[a,j] * Sinv[j,ap] for a in N for ap in N])

class SpectrumError(Exception):
    '''An exception for making the spectrum'''
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
