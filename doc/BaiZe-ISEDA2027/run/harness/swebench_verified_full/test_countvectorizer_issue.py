
# Test script to reproduce the issue
from sklearn.feature_extraction.text import CountVectorizer

# Test case 1: No vocabulary provided, should raise error
print("Test 1: No vocabulary provided")
vectorizer1 = CountVectorizer()
corpus = [
    'This is the first document.',
    'This is the second second document.',
    'And the third one.',
    'Is this the first document?',
]
try:
    vectorizer1.get_feature_names()
    print("ERROR: Should have raised NotFittedError!")
except Exception as e:
    print(f"✓ Correctly raised: {type(e).__name__}")

# Test case 2: Vocabulary provided, should NOT raise error
print("\nTest 2: Vocabulary provided")
vocabulary = ['and', 'document', 'first', 'is', 'one', 'second', 'the', 'third', 'this']
vectorizer2 = CountVectorizer(vocabulary=vocabulary)
try:
    features = vectorizer2.get_feature_names()
    print(f"✓ Got feature names: {features}")
    print(f"✓ Feature names match vocabulary: {features == vocabulary}")
except Exception as e:
    print(f"ERROR: Got unexpected error: {type(e).__name__}: {e}")

# Test case 3: transform still works as expected
print("\nTest 3: transform with pre-provided vocabulary")
try:
    transformed = vectorizer2.transform(corpus)
    print(f"✓ Transform succeeded, shape: {transformed.shape}")
    features_after_transform = vectorizer2.get_feature_names()
    print(f"✓ Feature names after transform: {features_after_transform}")
except Exception as e:
    print(f"ERROR: Transform failed: {type(e).__name__}: {e}")
