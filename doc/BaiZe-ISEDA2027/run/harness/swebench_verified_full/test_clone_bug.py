from sklearn.preprocessing import StandardScaler
from sklearn.base import clone

# Test the bug
try:
    result = clone(StandardScaler(with_mean=StandardScaler))
    print("Success! Cloned result:", result)
    print("No error occurred, fix works.")
except TypeError as e:
    print(f"Error occurred: {e}")
    print("Bug is present.")