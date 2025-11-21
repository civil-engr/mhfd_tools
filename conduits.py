import numpy as np
from scipy.optimize import minimize
from matplotlib import pyplot as plt
import matplotlib.patches as patches

class Circular_Pipe():

    def __init__(self, diameter, slope, mannings_n):
        self.diameter = diameter
        self.slope = slope
        self.mannings_n = mannings_n
        self.max_Q = circ_full_Q(D=diameter, slope=slope, manning_n=mannings_n)

def plot_pipe_water_level(depth, diameter, Q, Q_max):
    """
    Plot a circular pipe cross-section with a water level shown as a fill.

    Parameters
    ----------
    percent_D : float
        Water level as a percent of the pipe diameter (0–100).
    """
    # Percent of full depth
    percent_D = max(0, min(1.0, depth/diameter))

    # Pipe geometry. This is post hydraulics cals so a unit circle is fine
    R = 1
    # Since D != 1, there's a conversion step
    water_depth = percent_D * 2 * R
    # y_list-coordinate of converted depth
    depth_y = -R + water_depth # y_list-location of the water line

    # Prepare figure
    fig, ax = plt.subplots(figsize=(6, 6))

    # Draw pipe interior as circle
    circle = plt.Circle((0, 0), R, fill=False, linewidth=3)
    ax.add_patch(circle)

    ## Color in the water (Not needed by looks better)
    ## Note: use of np.maximum() is to catch tiny (10^-10 size) negative vals that don't do sqrt
    # Linear depth intervals. We could save points by going around perimeter, but that's complex
    y_list = np.linspace(-R, depth_y, 300)
    # Positive x-coords
    x_right_list =  np.sqrt(np.maximum(0, R**2 - y_list**2))
    # Negative x-coords
    x_left_list = -x_right_list
    # Fantastic drawing function here. Revisit for irregular channels
    ax.fill_betweenx(y_list, x_left_list, x_right_list, color='cornflowerblue')

    # Phreatic surface
    x_top_right = np.sqrt(np.abs(R**2 - depth_y**2))
    x_top_left = -x_top_right
    # x_line = np.linspace(-R, R, 400)
    x_line = np.linspace(x_top_left, x_top_right, 100)
    #mask = x_line**2 + depth_y**2 <= R**2  # only draw line where inside circle
    # ax.plot(x_line[mask], depth_y * np.ones_like(x_line[mask]),
    #         color='blue', linewidth=2)
    ax.plot(x_line, depth_y * np.ones_like(x_line), color='blue', linewidth=2)

    Label_str =(
        f"""Given flow: {Q} cfs\n
        Normal depth in the pipe: {depth} ft.
        Max Flow in the pipe: {Q_max} cfs""")


    # Formatting
    ax.set_aspect('equal')
    ax.set_xlim(-1.2*R, 1.2*R)
    ax.set_ylim(-1.2*R, 1.2*R)
    ax.axis('off')

    plt.title(f"Water Level: {100*percent_D:.1f}% of Diameter")
    plt.show()

def rect_normal_given_Q(
    Q: float,
    b: float,
    slope: float,
    manning_n: float,
):
    def Q_error(y):
        a = b * y
        p = b + (2 * y)
        rh = a/p
        error = abs(Q - (1.49 / manning_n * a * np.pow(rh, 2/3) * np.sqrt(slope)))
        print(f'Error in the rectangular channel calc = {error}')
        return error

    y_0 = 0.2981

    # q_test_0 = 9
    # def easy_one(q_test):
    #     return abs(Q - q_test)

    # y_q = minimize(easy_one, q_test_0, method='Powell')

    y_q = minimize(Q_error, y_0, method='SLSQP')

    return y_q.x

def circ_normal_given_Q(
    Q: float,
    D: float,
    slope: float,
    manning_n: float,
):
    # NOTE: numpy trig funcitons use radians by default
    # find theta
    debug=True
    def theta_error(theta):
        if theta < 0:
            print(f"THETA: {theta}")
            print(f"NEGATIVE VALUE IN TRIAL: theta = {theta}")
        # https://www.engr.scu.edu/~emaurer/hydr-watres-book/flow-in-open-channels.html
        c = 13.53 # English units
        error = np.pow(theta, -2/3) \
                * np.pow(theta - np.sin(theta), 5/3) \
                - c * manning_n * Q * np.pow(D, -8/3) / np.sqrt(slope) 
        return abs(error)
    
    theta_0 = 1
    bounds=((0, 2*np.pi),)

    theta_q = minimize(theta_error, theta_0, method='Powell', bounds=bounds)

    y = D / 2 * (1 - np.cos(theta_q.x/2))

    return y

def circ_full_Q(
    D: float,
    slope: float,
    manning_n: float,
):
    a = np.pi/4 * D**2
    p = np.pi * D
    rh = a/p
    return 1.49/manning_n * a * np.pow(rh, 2/3) * np.sqrt(slope)


if __name__ == "__main__":
    
    # test_basin = SubBasin(
    #     name = "A1",
    #     C5 = 0.7,
    #     Li = 100,
    #     Si = 0.01,
    #     Lt = 100,
    #     St = 0.015,
    #     K = 20
    # )

    circ_depth = circ_normal_given_Q(
        Q = 10, 
        D = 1.5,
        slope = 0.05,
        manning_n= 0.014
    )

    # rect_depth = rect_normal_given_Q(
    #     Q=10,
    #     b=3,
    #     slope=0.03,
    #     manning_n=0.012
    # )

    max_circ_q_check = circ_full_Q(
        D = 1.5,
        slope = 0.05,
        manning_n= 0.014
    )

    # print(f'depth in the circular channel = {circ_depth}')
    # print(f'depth in the rectangular channel = {rect_depth}')
    # print(f'theoretical max flow under gravity in circ = {max_circ_q_check}')

    steady_flow = 2.3 #cfs
    pipe_1 = Circular_Pipe(diameter=1.5, slope=0.05, mannings_n=0.014)
    pipe_1_depth_1 = circ_normal_given_Q(
        Q = steady_flow,
        D = pipe_1.diameter,
        slope = pipe_1.slope,
        manning_n = pipe_1.mannings_n)[0]

    plot_pipe_water_level(
        depth = pipe_1_depth_1,
        diameter = pipe_1.diameter,
        Q = steady_flow,
        Q_max = pipe_1.max_Q
    )
    debug=True