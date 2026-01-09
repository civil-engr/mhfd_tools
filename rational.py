'''
These are the functions typically used in runoff calculations using the rational method
as described in the Mile High Flood Distruct (mhfd.org) documentation. Some parameters
used in these formulae have hard-coded parameters that are specific to the
Front Range.

STYLE NOTE: in its current form, this code relies on some dictionaries that all need the same
keys in order to pass and process values easily. This could be updated to be a central dataframe
where the sub-basin names are primary keys and all the data that's currently getting spread
# across multiple columns in the spreadsheet can be contained more neatly?
'''

import numpy as np
import pandas as pd

# Classes
class Area:
    def __init__(
        self,
        area_ac: float,
        nrcs_soil_group: str,
        impervious_ratio: float,
    ):
        self.area_ac = area_ac
        self.nrcs_soil_group = nrcs_soil_group
        self.impervious_ratio = impervious_ratio
        self.cWQE = get_c_inflitration(nrcs_soil_type=nrcs_soil_group, impervious_pct=impervious_ratio)["cWQE"]
        self.c005 = get_c_inflitration(nrcs_soil_type=nrcs_soil_group, impervious_pct=impervious_ratio)["c005"]
        self.c010 = get_c_inflitration(nrcs_soil_type=nrcs_soil_group, impervious_pct=impervious_ratio)["c010"]
        self.c025 = get_c_inflitration(nrcs_soil_type=nrcs_soil_group, impervious_pct=impervious_ratio)["c025"]
        self.c050 = get_c_inflitration(nrcs_soil_type=nrcs_soil_group, impervious_pct=impervious_ratio)["c050"]
        self.c100 = get_c_inflitration(nrcs_soil_type=nrcs_soil_group, impervious_pct=impervious_ratio)["c100"]
        self.c500 = get_c_inflitration(nrcs_soil_type=nrcs_soil_group, impervious_pct=impervious_ratio)["c500"]

class SubBasin:
    # Sub-Basin class: main spatial unit for rational analysis using MHFD sheets
    # CONTAINS physical parameters for initial and channelized length/slope, NRCS k-factor
    # CALLS Area class, various helper functions to calculate parameters (I, ti, tt, tc)

    # Design notes: for a given dictionary  {rtn_prd: P1} pairs, the basin can calculate
    # the Intensity and the Discharge for all return periods.
    # {P1} applies to all sub-basins, while tc is specific to each sub-basin and can be tweaked by users
    # Tweaking tc will require recalculating Intensity and Q arrays

    def __init__(
        self,
        name: str,
        Li: float,
        Si: float,
        Lt: float,
        St: float,
        K: int,
        areas: list[Area],
        P1_dict: dict[str, float],
        tc=None,
    ):

        self.name = name
        self.Li = Li
        self.Si = Si
        self.Lt = Lt
        self.St = St
        self.K = K
        self.areas = areas
        self.P1_dict = P1_dict
        self.tc = tc

        # Area count
        self.area_count = len(areas)

        # Total basin area: sum of all constituent are objects
        self.basin_area_ac = sum(a.area_ac for a in areas)

        # List of all soil groups, duplicates removed
        self.soil_groups = sorted(list(set([a.nrcs_soil_group for a in areas])))

        # Basin imperviousness: area-weighted average of Area objects' imperviousness
        self.basin_pct_imp = sum(area.impervious_ratio * area.area_ac for area in areas) / self.basin_area_ac

        basin_df = pd.DataFrame()

        # Runoff coefficients (weighted by area)
        self.cWQE = sum(area.area_ac * area.cWQE for area in areas) / self.basin_area_ac
        self.c002 = sum(area.area_ac * area.cWQE for area in areas) / self.basin_area_ac
        self.c005 = sum(area.area_ac * area.c005 for area in areas) / self.basin_area_ac
        self.c010 = sum(area.area_ac * area.c010 for area in areas) / self.basin_area_ac
        self.c025 = sum(area.area_ac * area.c025 for area in areas) / self.basin_area_ac
        self.c050 = sum(area.area_ac * area.c050 for area in areas) / self.basin_area_ac
        self.c100 = sum(area.area_ac * area.c100 for area in areas) / self.basin_area_ac
        self.c500 = sum(area.area_ac * area.c500 for area in areas) / self.basin_area_ac
        # self.c_list = [self.cWQE, self.c005, self.c010, self.c025, self.c050, self.c100, self.c500]
        self.c_dict= {
            "cWQE": self.cWQE,
            "c002": self.c002,
            "c005": self.c005,
            "c010": self.c010,
            "c025": self.c025,
            "c050": self.c050,
            "c100": self.c100,
            "c500": self.c500,
        }

        # Calculated values based on MHFD criteria
        self.ti = 0.395 * (1.1 - self.c005) * np.sqrt(Li) / np.pow(Si, 0.33)
        self.tt = Lt / (60 * K * np.sqrt(St))

        self.tc_normal = self.ti + self.tt
        self.tc_region = (26 - 17*self.basin_pct_imp) + \
                         (self.Lt / (60 * (14 * self.basin_pct_imp + 9) * np.sqrt(St)))

        # TODO: allow a user to pick regional or normal tc; possibly by having a textbox pass a
        # number to this block, like -1 for normal and -2 for regional?
        # DURING DEV: using min of (normal, regional) so we can write the rest
        if self.tc is None:
            self.tc = min(self.tc_region, self.tc_normal)

        self.intensity_dict = {}
        self.discharge_dict = {}
        self.get_intensity()
        self.get_discharges()

    def get_intensity(self, a=28.5, b=10.0, c=0.786):
        for key, value in self.P1_dict.items():
            self.intensity_dict[key] = (a * value) / (b + self.tc)**c
        # return (a * P1) / (b + self.tc)**c

    # NOTE: need to handle the differnce dict sizes:
    # For C-values, 2-year and WQE are the same. Maybe add a redundancy c value to get 1:1?
    def get_discharges(self):
        for key, value in self.P1_dict.items():
            self.discharge_dict[key] = self.basin_area_ac * \
                                       self.intensity_dict[key] * self.c_dict[key]

    debug = True

# Functions ------------------------------------------------------------------------------------------------

def get_c_inflitration(
    nrcs_soil_type: str,
    impervious_pct: float
):
    match nrcs_soil_type.upper():
        case 'A':
            cWQE = 0.840 * (impervious_pct**1.302)
            c002 = cWQE
            c005 = 0.861 * (impervious_pct**1.276)
            c010 = 0.873 * (impervious_pct**1.232)
            c025 = 0.884 * (impervious_pct**1.124)
            c050 = (0.854 * impervious_pct) + 0.025
            c100 = (0.779 * impervious_pct) + 0.110
            c500 = (0.654 * impervious_pct) + 0.254
        case 'B':
            cWQE = 0.835 * (impervious_pct ** 1.169)
            c002 = cWQE
            c005 = 0.857 * (impervious_pct ** 1.088)
            c010 = (0.807 * impervious_pct) + 0.025
            c025 = (0.628 * impervious_pct) + 0.249
            c050 = (0.558 * impervious_pct) + 0.328
            c100 = (0.465 * impervious_pct) + 0.426
            c500 = (0.366 * impervious_pct) + 0.536
        case 'C/D':
            cWQE = 0.834 * (impervious_pct ** 1.122)
            c002 = cWQE
            c005 = (0.815 * impervious_pct) + 0.035
            c010 = (0.735 * impervious_pct) + 0.132
            c025 = (0.560 * impervious_pct) + 0.319
            c050 = (0.494 * impervious_pct) + 0.393
            c100 = (0.409 * impervious_pct) + 0.484
            c500 = (0.315 * impervious_pct) + 0.588
        case _:
            raise ValueError('nrcs_soil_type must be in ["A", "B", or "C/D"')

    return {
        "cWQE": cWQE,
        "c002": c002,
        "c005": c005,
        "c010": c010,
        "c025": c025,
        "c050": c050,
        "c100": c100,
        "c500": c500
    }


def route_sbs_at_dp(
    subbasins: list,
    # return_prd: str
):
    # For a design point, take a list of tributary sub-basins
    # For each sub-basin, generate a flow by doing the below: (outer loop)
    # 1. Set that basin's [rainfall intensity] as the intensity for all subbasins
    # 2. For each subbasin, if its tc < basin tc, define % intensity (default = 1.00) (inner loop)
    # 3. Within inner loop, multiply C * A * % intensity

    # TODO: have this automatically do all return periods
    # TODO: design a GUI element (dict backend?) that matches a human-readable return period to sb.c_rtnprd

    # Re-creating the logic from column Q of the 'Runoff Routing' sheet (basin routing to design points)
    for h in subbasins[0].c_dict.keys():
        print(f'{h}\t{subbasins[0].c_dict[h]}')


    for i, sb_outer in enumerate(subbasins):
        intensity = sb_outer.intensity

        # array to hold the flows from each routing scenario (where flow and tc are based on each
        # outer-loop basin zero through i)
        q_all_ab = np.zeros(len(subbasins))

        # set a dummy variable to hold the sum of all sub-basins (zero through j) routing the flow
        # from the current (ith) basin in the outer loop
        trial_q = 0
        for j, sb_inner in enumerate(subbasins):
            pct_intensity = max(1, sb_inner/sb_outer)
            # Q = CIA * %tc for basins with longer tc that the ith basin.
            q_sb_inner = sb_inner.basin_c005 * sb_inner.basin_area_ac * intensity * pct_intensity
            trial_q += q_sb_inner

        q_all_ab[i] = trial_q


    debug = True


    return True


# Run as standalone. Not sure what this will look like yet, and during dev this 
# is just for calling functions and creating classes from the library to verify 
# calculation results (by comparison to MHFD spreadsheets)
if __name__ == "__main__":

    P1 = {
        "cWQE": 0.60,
        "c002": 0.84,
        "c005": 1.13,
        "c010": 1.39,
        "c025": 1.77,
        "c050": 2.08,
        "c100": 2.42,
        "c500": 3.30
    }

    # Don't worry about naming areas for now - this will be graphical input eventually
    area_a1 = Area(area_ac=3.0, nrcs_soil_group="A", impervious_ratio=0.65)
    area_a2 = Area(area_ac=10.0, nrcs_soil_group="B", impervious_ratio=0.15)
    sub_basin_A = SubBasin(
        name = "A",
        Li =  100,
        Si =  0.02,
        Lt = 200,
        St = 0.025,
        K = 20,
        areas = [area_a1, area_a2],
        P1_dict = P1
    )

    area_b1 = Area(area_ac=2.0, nrcs_soil_group="A", impervious_ratio=0.90)
    area_b2 = Area(area_ac=6.0, nrcs_soil_group="B", impervious_ratio=0.75)
    area_b3 = Area(area_ac=11.0, nrcs_soil_group="C/D", impervious_ratio=0.20)
    sub_basin_B = SubBasin(
        name="B",
        Li=150,
        Si=0.01,
        Lt=120,
        St=0.03,
        K=20,
        areas=[area_b1, area_b2, area_b3],
        P1_dict = P1
    )

    route_sbs_at_dp([sub_basin_A, sub_basin_B])

    debug=True