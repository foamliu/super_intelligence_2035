
import matplotlib
print(f"Matplotlib version: {matplotlib.__version__}")
print(f"Matplotlib path: {matplotlib.__file__}")
from matplotlib.contour import ContourSet
import inspect
print(f"ContourSet._process_contour_level_args source:\n{inspect.getsource(ContourSet._process_contour_level_args)}")
