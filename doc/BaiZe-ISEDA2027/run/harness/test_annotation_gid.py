import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import xml.etree.ElementTree as ET

# Create test image
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

# Save to SVG in memory
import io
svg_buffer = io.BytesIO()
fig.savefig(svg_buffer, format="svg")
svg_buffer.seek(0)

# Parse SVG and check for the gid
tree = ET.parse(svg_buffer)
root = tree.getroot()

# Find all elements with id attribute
found_gid = False
for elem in root.iter():
    if 'id' in elem.attrib and elem.attrib['id'] == 'My_label':
        found_gid = True
        print(f"Found gid 'My_label' in SVG!")
        # Check that it contains the image element
        has_image = any(child.tag.endswith('image') for child in elem)
        print(f"Group contains image element: {has_image}")
        break

if not found_gid:
    print("ERROR: GID 'My_label' not found in SVG output!")
else:
    print("SUCCESS: GID is correctly present in SVG!")
