"""
Base classes for all estimators.
"""

# Author: Gael Varoquaux <gael.varoquaux@normalesup.org>
# License: BSD 3 clause

import copy
import inspect
import warnings

import numpy as np

from .exceptions import NotFittedError
from .utils.deprecation import deprecated
from .utils._joblib import Memory
from .utils.validation import check_is_fitted, check_array


class BaseEstimator:
    """Base class for all estimators in scikit-learn

    Notes
    -----
    All estimators should specify all the parameters that can be set
    at the class level in their ``__init__`` as explicit keyword
    arguments (no ``*args`` or ``**kwargs``).
    """

    @classmethod
    def _get_param_names(cls):
        """Get parameter names for the estimator"""
        # fetch the constructor or the original constructor before
        # deprecation wrapping if any
        init = getattr(cls.__init__, 'deprecated_original', cls.__init__)
        if init is object.__init__:
            # No explicit constructor to introspect
            return []

        # introspect the constructor arguments to find the model parameters
        # to represent
        init_signature = inspect.signature(init)
        # Consider the constructor parameters excluding 'self'
        parameters = [p for p in init_signature.parameters.values()
                      if p.name != 'self' and p.kind != p.VAR_KEYWORD]
        for p in parameters:
            if p.kind == p.VAR_POSITIONAL:
                raise RuntimeError("scikit-learn estimators should always "
                                   "specify their parameters in the signature"
                                   " of their __init__ (no varargs)."
                                   " %s with constructor %s doesn't "
                                   " follow this convention."
                                   % (cls, init_signature))
        # Extract and sort argument names excluding 'self'
        return sorted([p.name for p in parameters])

    def get_params(self, deep=True):
        """Get parameters for this estimator.

        Parameters
        ----------
        deep : boolean, optional
            If True, will return the parameters for this estimator and
            contained subobjects that are estimators.

        Returns
        -------
        params : mapping of string to any
            Parameter names mapped to their values.
        """
        out = dict()
        for key in self._get_param_names():
            try:
                value = getattr(self, key)
            except AttributeError:
                warnings.warn("From version 0.24, get_params will raise an "
                              "AttributeError if a parameter doesn't "
                              "exist as an instance attribute.",
                              FutureWarning)
                value = None
            if deep and hasattr(value, 'get_params'):
                deep_items = value.get_params().items()
                out.update((key + '__' + k, val) for k, val in deep_items)
            out[key] = value
        return out

    def set_params(self, **params):
        """Set the parameters of this estimator.

        The method works on simple estimators as well as on nested objects
        (such as pipelines). The latter have parameters of the form
        ``<component>__<parameter>`` so that it's possible to update each
        component of a nested object.

        Returns
        -------
        self
        """
        if not params:
            # Simple optimization to gain speed (inspect is slow)
            return self
        valid_params = self.get_params(deep=True)

        nested_params = dict()  # grouped by prefix
        for key, value in params.items():
            key, delim, sub_key = key.partition('__')
            if key not in valid_params:
                raise ValueError('Invalid parameter %s for estimator %s. '
                                 'Check the list of available parameters '
                                 'with `estimator.get_params().keys()`.' %
                                 (key, self))

            if delim:
                nested_params[key][sub_key] = value
            else:
                setattr(self, key, value)
                valid_params[key] = value

        for key, sub_params in nested_params.items():
            valid_params[key].set_params(**sub_params)

        return self

    def __repr__(self, n_char_max=700):
        from .utils._pprint import _EstimatorPrettyPrinter
        return _EstimatorPrettyPrinter(
            indent=1, width=80, depth=None,
            n_char_max=n_char_max).pformat(self)

    def __getstate__(self):
        try:
            state = super().__getstate__()
        except AttributeError:
            state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        try:
            super().__setstate__(state)
        except AttributeError:
            self.__dict__.update(state)


class ClassifierMixin:
    """Mixin class for all classifiers in scikit-learn."""
    _estimator_type = "classifier"

    def score(self, X, y, sample_weight=None):
        """Returns the mean accuracy on the given test data and labels.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Test samples.

        y : array-like, shape = (n_samples)
            True labels for X.

        sample_weight : array-like, shape = (n_samples,), optional
            Sample weights.

        Returns
        -------
        score : float
            Mean accuracy of self.predict(X) wrt. y.
        """
        from .metrics import accuracy_score
        return accuracy_score(y, self.predict(X), sample_weight=sample_weight)


class RegressorMixin:
    """Mixin class for all regression estimators in scikit-learn."""
    _estimator_type = "regressor"

    def score(self, X, y, sample_weight=None):
        """Returns the coefficient of determination R^2 of the prediction.

        The coefficient R^2 is defined as (1 - u/v), where u is the residual
        sum of squares ((y_true - y_pred) ** 2).sum() and v is the total
        sum of squares ((y_true - y_true.mean()) ** 2).sum().
        The best possible score is 1.0 and it can be negative (because the
        model can be arbitrarily worse). A constant model that always
        predicts the expected value of y, disregarding the input features,
        would get a R^2 score of 0.0.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Test samples.

        y : array-like, shape = (n_samples)
            True values for X.

        sample_weight : array-like, shape = (n_samples,), optional
            Sample weights.

        Returns
        -------
        score : float
            R^2 of self.predict(X) wrt. y.
        """
        from .metrics import r2_score
        return r2_score(y, self.predict(X), sample_weight=sample_weight)


class ClusterMixin:
    """Mixin class for all cluster estimators in scikit-learn."""
    _estimator_type = "clusterer"

    def fit_predict(self, X, y=None):
        """Performs clustering on X and returns cluster labels.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            Input data.

        y : Ignored

        Returns
        -------
        labels : ndarray, shape (n_samples,)
            cluster labels
        """
        # default implementation calls fit and then predict
        self.fit(X)
        return self.labels_


class BiclusterMixin:
    """Mixin class for all bicluster estimators in scikit-learn."""

    @property
    def biclusters_(self):
        """Convenient way to get row and column indicators together.

        Requires the ``rows_`` and ``columns_`` attributes to be available.
        """
        return self.rows_, self.columns_

    def get_indices(self, i):
        """Row and column indices of the i'th bicluster.

        Parameters
        ----------
        i : int
            The index of the cluster.

        Returns
        -------
        row_ind : np.array, dtype=np.intp
            Indices of rows in the dataset that belong to the bicluster.
        col_ind : np.array, dtype=np.intp
            Indices of columns in the dataset that belong to the bicluster.
        """
        check_is_fitted(self, 'rows_')
        check_is_fitted(self, 'columns_')

        rows = self.rows_[i]
        columns = self.columns_[i]
        return np.nonzero(rows)[0], np.nonzero(columns)[0]

    def get_shape(self, i):
        """Shape of the i'th bicluster.

        Parameters
        ----------
        i : int
            The index of the cluster.

        Returns
        -------
        shape : (int, int)
            Number of rows and columns (respectively) in the bicluster.
        """
        check_is_fitted(self, 'rows_')
        check_is_fitted(self, 'columns_')
        return self.rows_[i].sum(), self.columns_[i].sum()

    def get_submatrix(self, i, data):
        """Returns the submatrix corresponding to bicluster `i`.

        Parameters
        ----------
        i : int
            The index of the cluster.
        data : array-like, shape = (n_samples, n_features)
            The data.

        Returns
        -------
        submatrix : array, shape (n_rows, n_cols)
            The submatrix corresponding to bicluster i.

        Notes
        -----
        Works with sparse matrices. Only works if ``rows_`` and
        ``columns_`` attributes are available.
        """
        data = check_array(data, accept_sparse='csr')
        row_ind, col_ind = self.get_indices(i)
        return data[row_ind[:, np.newaxis], col_ind]


class TransformerMixin:
    """Mixin class for all transformers in scikit-learn."""

    def fit_transform(self, X, y=None, **fit_params):
        """Fit to data, then transform it.

        Fits transformer to X and y with optional parameters fit_params
        and returns a transformed version of X.

        Parameters
        ----------
        X : numpy array of shape [n_samples, n_features]
            Training set.

        y : numpy array of shape [n_samples]
            Target values.

        Returns
        -------
        X_new : numpy array of shape [n_samples, n_features]
            Transformed array.
        """
        # non-optimized default implementation; override when a better
        # method is possible for a given algorithm
        if y is None:
            # fit method of arity 1 (unsupervised transformation)
            return self.fit(X, **fit_params).transform(X)
        else:
            # fit method of arity 2 (supervised transformation)
            return self.fit(X, y, **fit_params).transform(X)


class DensityMixin:
    """Mixin class for density estimators."""
    _estimator_type = "DensityEstimator"

    def score(self, X, y=None):
        """Returns the score of the model on the data X.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)

        y : Ignored

        Returns
        -------
        score: float
        """
        pass


class OutlierMixin:
    """Mixin class for outlier detector."""
    _estimator_type = "outlier_detector"

    def fit_predict(self, X, y=None):
        """Performs outlier detection on X.

        Returns -1 for outliers and 1 for inliers.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Input data.

        y : Ignored

        Returns
        -------
        y_pred : ndarray, shape (n_samples,)
            1 for inliers, -1 for outliers.
        """
        self.fit(X)
        return self.predict(X)


def clone(estimator, safe=True):
    """Constructs a new estimator with the same parameters.

    Clone does a deep copy of the model in an estimator
    without actually copying attached data. It yields a new estimator
    with the same parameters that has not been fit on any data.

    Parameters
    ----------
    estimator : estimator object, or list, tuple or set of objects
        The estimator or group of estimators to be cloned.

    safe : boolean, optional
        If safe is false, clone will fall back to a deep copy on objects
        that are not estimators.

    """
    estimator_type = type(estimator)
    # XXX: not handling dictionaries
    if estimator_type in (list, tuple, set, frozenset):
        return estimator_type([clone(e, safe=safe) for e in estimator])
    elif not hasattr(estimator, 'get_params') or isinstance(estimator, type):
        if not safe:
            return copy.deepcopy(estimator)
        else:
            raise TypeError("Cannot clone object '%s' (type %s): "
                            "it does not implement a get_params method."
                            % (estimator, estimator_type))
    else:
        new_object_params = estimator.get_params(deep=False)
        for name, param in new_object_params.items():
            new_object_params[name] = clone(param, safe=False)
        new_object = estimator.__class__(**new_object_params)

        # determine if the estimator should be fitted or not.
        # we need to handle the case where the estimator has an _pairwise
        # attribute which is not set via __init__
        if hasattr(estimator, '_pairwise'):
            new_object._pairwise = estimator._pairwise

        return new_object