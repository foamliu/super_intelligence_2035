
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)

# Create dummy test image
arr_img = np.random.rand(100, 100, 3)

fig, ax = plt.subplots()

xy = [0.3, 0.55]

imagebox = OffsetImage(arr_img, zoom=0.1)
imagebox.image.axes = ax

ab = AnnotationBbox(imagebox, xy,
                    xybox=(120., -80.),
                    xycoords='data',
                    boxcoords="offset points",
                    pad=0.5,
                    arrowprops=dict(
                        arrowstyle="->",
                        connectionstyle="angle,angleA=0,angleB=90,rad=3")
                    )
# Don't set gid this time
ax.add_artist(ab)

fig.savefig("example_no_gid.svg", format="svg")

print("Generated SVG without gid, no errors thrown!")
