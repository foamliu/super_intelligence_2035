
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
ab.set_gid('My_label')
ax.add_artist(ab)

print(f"GID = {ab.get_gid()}")

fig.savefig("example.svg", format="svg")

# Check if the gid is present in the SVG
with open("example.svg", "r") as f:
    svg_content = f.read()

if 'My_label' in svg_content:
    print("SUCCESS: GID found in SVG!")
else:
    print("FAILURE: GID NOT found in SVG!")
    print("Looking for 'My_label' in SVG content:")
    print(svg_content[:500] + "...")
