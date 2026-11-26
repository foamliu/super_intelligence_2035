import numpy as np
import matplotlib.colors as colors

norm_invalid = colors.LogNorm(vmin=0, vmax=1e20)
data = np.array([1, 10, 100])

print(f"vmin={norm_invalid.vmin}, vmax={norm_invalid.vmax}")
print(f"transform([vmin, vmax]): {norm_invalid._trf.transform([norm_invalid.vmin, norm_invalid.vmax])}")
print(f"Are finite: {np.isfinite(norm_invalid._trf.transform([norm_invalid.vmin, norm_invalid.vmax])).all()}")

try:
    t_value = norm_invalid._trf.transform(data)
    print(f"t_value: {t_value}")
    t_value = np.ma.masked_invalid(t_value, copy=False)
    print(f"Masked t_value: {t_value}")
    
    result = norm_invalid(data)
    print(f"\nResult: {result}")
except ValueError as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
