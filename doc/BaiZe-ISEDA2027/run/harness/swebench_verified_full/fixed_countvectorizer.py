
# Fixed implementation of CountVectorizer that fixes the get_feature_names issue
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import _VectorizerMixin
from sklearn.feature_extraction.text import CountVectorizer as OriginalCountVectorizer
from sklearn.exceptions import NotFittedError


class FixedCountVectorizer(OriginalCountVectorizer):
    def get_feature_names(self):
        # Call _validate_vocabulary first, just like transform() does
        self._validate_vocabulary()
        # Now check if vocabulary_ exists (it should, if we got here)
        if not hasattr(self, 'vocabulary_'):
            raise NotFittedError(
                f"{self.__class__.__name__} - Vocabulary wasn't fitted."
            )
        return np.array(sorted(self.vocabulary_.keys(), key=self.vocabulary_.get))


# Test the fixed implementation
if __name__ == "__main__":
    print("Testing FixedCountVectorizer:")
    vocabulary = ['and', 'document', 'first', 'is', 'one', 'second', 'the', 'third', 'this']
    vectorizer = FixedCountVectorizer(vocabulary=vocabulary)
    
    print("\nCalling get_feature_names() before transform:")
    try:
        features = vectorizer.get_feature_names()
        print(f"✅ Success! Features: {features}")
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    
    print("\nCalling transform:")
    corpus = [
        'This is the first document.',
        'This is the second second document.',
        'And the third one.',
        'Is this the first document?',
    ]
    transformed = vectorizer.transform(corpus)
    print(f"✅ Transform success, shape: {transformed.shape}")
    
    print("\nCalling get_feature_names() after transform:")
    features_after = vectorizer.get_feature_names()
    print(f"✅ Features after transform: {features_after}")
    print(f"✅ Features match before and after transform: {np.array_equal(features, features_after)}")
    
    print("\nTesting without vocabulary (should still raise error):")
    vectorizer_no_vocab = FixedCountVectorizer()
    try:
        vectorizer_no_vocab.get_feature_names()
        print("❌ Should have raised NotFittedError!")
    except NotFittedError:
        print("✅ Correctly raised NotFittedError when no vocabulary provided")
