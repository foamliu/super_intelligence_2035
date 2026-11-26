import numpy as np
import matplotlib
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import check_figures_equal

# Copy of the test
@check_figures_equal()
def test_huge_range_log(fig_test, fig_ref, x):
    # parametrize over bad lognorm -1 values and large range 1 -> 1e20
    data = np.full((5, 5), x, dtype=np.float64)
    data[0:2, :] = 1E20

    ax = fig_test.subplots()
    ax.imshow(data, norm=colors.LogNorm(vmin=1, vmax=data.max()),
              interpolation='nearest', cmap='viridis')

    data = np.full((5, 5), x, dtype=np.float64)
    data[0:2, :] = 1000

    ax = fig_ref.subplots()
    cmap = matplotlib.colormaps['viridis'].with_extremes(under='w')
    ax.imshow(data, norm=colors.Normalize(vmin=1, vmax=data.max()),
              interpolation='nearest', cmap=cmap)

# Run for x=-1 and x=1
for x in [-1, 1]:
    print(f"\nTesting x={x}...")
    try:
        # Create figures manually
        fig_test = plt.figure()
        fig_ref = plt.figure()
        test_huge_range_log(fig_test, fig_ref, x)
        
        # Draw both figures
        fig_test.canvas.draw()
        fig_ref.canvas.draw()
        
        print(f"✓ Test passed for x={x}")
        
        plt.close('all')
    except Exception as e:
        print(f"✗ Test failed for x={x}: {e}")
        import traceback
        traceback.print_exc()
