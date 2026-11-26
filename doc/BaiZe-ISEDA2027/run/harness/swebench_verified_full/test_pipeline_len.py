import sys
import os
sys.path.insert(0, os.path.abspath('./scikit_learn_repo'))

from sklearn import svm
from sklearn.datasets import make_classification
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.pipeline import Pipeline

# generate some data to play with
X, y = make_classification(
    n_informative=5, n_redundant=0, random_state=42)

anova_filter = SelectKBest(f_regression, k=5)
clf = svm.SVC(kernel='linear')
pipe = Pipeline([('anova', anova_filter), ('svc', clf)])

print("Testing len(pipe)...")
try:
    length = len(pipe)
    print(f"len(pipe) = {length}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

print("\nTesting pipe[:len(pipe)]...")
try:
    sliced = pipe[:len(pipe)]
    print(f"Sliced pipe: {sliced}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

print("\nTesting pipe[:2]...")
try:
    sliced = pipe[:2]
    print(f"Sliced pipe: {sliced}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
