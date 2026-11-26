from sklearn.tree import DecisionTreeClassifier
from sklearn.tree.export import export_text
from sklearn.datasets import load_iris

# Test case from the issue
X, y = load_iris(return_X_y=True)
X = X[:, 0].reshape(-1, 1)  # Only one feature

tree = DecisionTreeClassifier()
tree.fit(X, y)
tree_text = export_text(tree, feature_names=['sepal_length'])
print("Test passed! Output:")
print(tree_text)

# Also test without feature names
print("\n\nTest without feature names:")
tree_text2 = export_text(tree)
print(tree_text2)

# Test with multi-feature to ensure we didn't break existing functionality
print("\n\nTest with multiple features (original functionality):")
X_full, y_full = load_iris(return_X_y=True)
tree_full = DecisionTreeClassifier(max_depth=2)
tree_full.fit(X_full, y_full)
tree_text_full = export_text(tree_full, feature_names=load_iris().feature_names)
print(tree_text_full)
