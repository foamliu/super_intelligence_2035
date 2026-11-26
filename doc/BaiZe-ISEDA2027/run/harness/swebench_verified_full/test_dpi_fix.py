import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pickle
import platform

# Set backend to Agg for testing (no GUI needed)
matplotlib.use('Agg')

print('Matplotlib ver:', matplotlib.__version__)
print('Platform:', platform.platform())


def dump_load_get_dpi(fig):
    with open('test_dpi.pickle','wb') as file:
        pickle.dump(fig, file)

    with open('test_dpi.pickle', 'rb') as blob:
        fig2 = pickle.load(blob)
    return fig2, fig2.dpi


def run():
    fig = plt.figure(dpi=100)  # Use 100 DPI for easier testing
    x = np.linspace(0,2*np.pi)
    y = np.sin(x)
    ax = fig.add_subplot()
    ax.plot(x, y)
    
    # Simulate MacOSX backend device pixel ratio of 2
    # This is what the MacOSX backend does when creating the canvas
    fig._original_dpi = fig.dpi
    fig.canvas._set_device_pixel_ratio(2)
    
    print(f'Initial DPI after scaling: {fig.dpi}')
    
    for i in range(5):
        print(f'Iteration {i}: {fig.dpi}')
        fig, dpi = dump_load_get_dpi(fig)
        # Apply device pixel ratio again (as would happen when unpickling on Mac)
        fig.canvas._set_device_pixel_ratio(2)
    
    print(f'Final DPI: {fig.dpi}')
    # Check if DPI remains 200 (100 * 2) instead of doubling each time
    assert fig.dpi == 200, f"Expected DPI to be 200, got {fig.dpi}"
    print("✅ Test passed! DPI no longer doubles when unpickling.")
    
    # Clean up
    import os
    os.remove('test_dpi.pickle')


if __name__ == '__main__':
    run()
