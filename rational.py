'''
These are the functions typically used in runoff calculations using the rational method
as described in the Mile High Flood Distruct (mhfd.org) documentation. Some parameters
used in these formulae have hard-coded parameters that are specific to the the 
Front Range.
'''

import numpy as np

# Classes
class SubBasin:

    def __init__(
        self,
        name: str,
        C5: float,
        Li: float,
        Si: float,
        Lt: float,
        St: float,
        K: int
    ):
        # Allow attribute access outside of object
        self.name = name
        self.C5 = C5
        self.Li = Li
        self.Si = Si
        self.Lt = Lt
        self.St = St
        self.K = K

        # Calculated values based on MHFD criteria
        self.ti = get_ti(C5, Li, Si)
        self.tt = get_tt(Lt, St, K)
        self.tc = self.ti + self.tt

# Functions


def get_ti(
    C5: float,
    Li: float,
    Si: float        
):
    '''
    Get the time of concentration for the initial (overland) flow in a subbasin
    Parameters
    ----------
    C5: float
        Runoff coefficient for the 5-year event
    Li: float
        Length of initial (overland) flow in ft
    Si: float
        Slope of the initial (overland) portion of the basin in ft/ft

    Returns
    -------
    ti
        time of concentration for the initial (overland) portion of the basin in seconds
    '''

    return 0.395 * (1.1 - C5) * np.sqrt(Li) / np.pow(Si, 0.33)


def get_tt(
    Lt: float,
    St: float,
    K: int      
):
    return Lt / (60 * K * np.sqrt(St)) 


# Run as standalone. Not sure what this will look like yet, and during dev this 
# is just for calling functions and creating classes from the library to verify 
# calculation r"esults (by comparison to MHFD spreadsheets)
if __name__ == "__main__":
    
    test_basin = SubBasin(
        name = "A1",
        C5 = 0.7,
        Li = 100,
        Si = 0.01,
        Lt = 100,
        St = 0.015,
        K = 20
    )
    
    debug=True