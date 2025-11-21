import numpy as np
from scipy.optimize import minimize
from matplotlib import pyplot as plt


class Subcatch:
    def __init__(
        self,
        name: str,
        swmm_node: str,
        raingage: str,
        soil_group: str,
        area_ac: float,
        length_ft: float,
        length_to_centroid_ft: float,
        slope: float,
        impervious_pct: float,  # Use a decimal, not a percent
        f0_in_hr: float,
        fi_in_hr: float,
        alpha: float,
        depr_loss_prv_in: float,
        depr_loss_imp_in: float,
    ):
        # Model info
        self.name = name
        self.swmm_node = swmm_node
        self.raingage = raingage,
        # subcatchment parameters
        self.soil_group = soil_group,
        self.area = area_ac,
        self.length = length_ft,
        self.length_to_centroid = length_to_centroid_ft,
        self.slope = slope,
        self.impervious_pct = impervious_pct,
        # Depression storage
        self.depr_loss_prv = depr_loss_prv_in,
        self.depr_loss_prv = depr_loss_imp_in,
        # Horton's infiltration parameters
        self.f0 = f0_in_hr,
        self.fi = fi_in_hr,
        self.alpha = alpha,
        

def horton_t(
    f0: float,
    fi: float,
    alpha: float,
    t: float
):
    ft = f0 + (fi - f0) * np.pow(np.e, -alpha*t)
    return ft

if __name__ == "__main__":
    print("h4lloo")

    #Use the following values while debugging / testing Horton's
    # See table B-1 in CUHP user manual for recommnded values by soil type
    #Soil Group B
    fi = 4.5
    f0 = 0.6
    alpha = 0.0018
    depr_loss_prv_in = 0.4
    depr_loss_imp_imp = 0.1

    Basin_1 = Subcatch(
        swmm_node = "Node_1"
        raingage = "Gage_A"
        soil_group = "B"
        area_ac = 12.0
        length_ft = 1022
        length_to_centroid_ft = 511 
        slope = 0.02
        impervious_pct = 0.60  # Use a decimal, not a percent
        f0_in_hr = 0.6
        fi_in_hr = 4.5
        alpha = 0.0018
        depr_loss_prv_in = 0.4
        depr_loss_imp_imp = 0.1
    )