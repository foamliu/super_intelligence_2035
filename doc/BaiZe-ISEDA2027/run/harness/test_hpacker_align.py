import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.offsetbox import DrawingArea, HPacker, VPacker, AnchoredOffsetbox, TextArea
from matplotlib.patches import Rectangle

# Test both align values
for align in ["bottom", "top"]:
    # Create new objects each time to avoid "single artist in multiple figures" error
    da1 = DrawingArea(10, 20)
    rect1 = Rectangle((0, 0), 10, 20, color='red')
    da1.add_artist(rect1)

    da2 = DrawingArea(10, 30)
    rect2 = Rectangle((0, 0), 10, 30, color='blue')
    da2.add_artist(rect2)
    
    fig, ax = plt.subplots(figsize=(3, 3))
    
    pack = HPacker(children=[da1, da2], pad=10, sep=10, align=align)
    title = TextArea(f"align='{align}'")
    pack = VPacker(children=[title, pack], sep=10, pad=10, align="center")
    
    box = AnchoredOffsetbox(child=pack, loc="center")
    
    ax.add_artist(box)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.savefig(f"test_align_{align}.png", dpi=100, bbox_inches='tight')
    plt.close()
    
print("Test completed. Check test_align_bottom.png and test_align_top.png")
