
import sys
sys.path.insert(0, '.')
import xarray as xr
import numpy as np

my_data = xr.DataArray(np.arange(1,10), dims="x")

# Option 1: take a center-justified rolling average
result1 = my_data.rolling(x=3, center=True).mean().values
print("result1:", result1)

# Option 2: try to manually iterate, but the result is not centered
my_data_rolling = my_data.rolling(x=3, center=True)
print("my_data_rolling.center:", my_data_rolling.center)
print("window:", my_data_rolling.window)
result2 = [window.mean().values.item() for label, window in my_data_rolling]
print("result2:", result2)

# Let's also print each window
print("\nWindows:")
for i, (label, window) in enumerate(my_data_rolling):
    print(f"i={i}, label={label.item()}, window={window.values}, mean={window.mean().values.item()}")

# Test that they are equal
print("\nAre results equal?", np.allclose(result1, result2, equal_nan=True))
