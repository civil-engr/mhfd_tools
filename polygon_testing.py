import numpy as np
from scipy.optimize import minimize
from matplotlib import pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots()
ax.axis([-4, 4, -4, 4])

coord_array = np.array([[-1, 0], [0, -1], [1, 0]])
# coord_array = np.array(((-1, 0), (-1, -1), (1, 0)))
water = patches.Polygon(coord_array)

# ax.add_patch(water)

x = [0,1,2]
y1 = np.array([1,2,3])
#y2 = [2,3,4]
y2 = -y1
plt.fill_between(x,y1,y2,color='blue',alpha=0.5)

plt.show()

