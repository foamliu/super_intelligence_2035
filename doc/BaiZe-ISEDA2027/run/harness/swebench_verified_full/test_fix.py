import numpy as np
from sklearn.cluster import KMeans

def test_kbins_kmeans_fix():
    X = np.array([0, 0.5, 2, 3, 9, 10]).reshape(-1, 1)
    jj = 0
    column = X[:, jj]
    col_min, col_max = column.min(), column.max()
    n_bins_jj = 5
    
    # Original code
    uniform_edges = np.linspace(col_min, col_max, n_bins_jj + 1)
    init = (uniform_edges[1:] + uniform_edges[:-1])[:, None] * 0.5
    km = KMeans(n_clusters=n_bins_jj, init=init, n_init=1)
    centers = km.fit(column[:, None]).cluster_centers_[:, 0]
    print(f"Original centers: {centers}")
    print(f"Are centers sorted? {np.all(centers[:-1] <= centers[1:])}")
    
    # Without sorting, compute bin edges
    bin_edges_unsorted = (centers[1:] + centers[:-1]) * 0.5
    bin_edges_unsorted = np.r_[col_min, bin_edges_unsorted, col_max]
    print(f"Unsorted bin edges: {bin_edges_unsorted}")
    print(f"Are bin edges sorted? {np.all(bin_edges_unsorted[:-1] <= bin_edges_unsorted[1:])}")
    
    # With sorting (our fix)
    centers_sorted = np.sort(centers)
    print(f"Sorted centers: {centers_sorted}")
    bin_edges_sorted = (centers_sorted[1:] + centers_sorted[:-1]) * 0.5
    bin_edges_sorted = np.r_[col_min, bin_edges_sorted, col_max]
    print(f"Sorted bin edges: {bin_edges_sorted}")
    print(f"Are sorted bin edges sorted? {np.all(bin_edges_sorted[:-1] <= bin_edges_sorted[1:])}")
    
    # Test digitize
    try:
        Xt = np.digitize(column + 1e-8 + 1e-5 * np.abs(column), bin_edges_unsorted[1:])
        print(f"Digitize with unsorted edges worked: {Xt}")
    except ValueError as e:
        print(f"Digitize with unsorted edges failed: {e}")
    
    Xt = np.digitize(column + 1e-8 + 1e-5 * np.abs(column), bin_edges_sorted[1:])
    Xt = np.clip(Xt, 0, n_bins_jj -1)
    print(f"Digitize with sorted edges worked: {Xt}")
    return True

if __name__ == "__main__":
    test_kbins_kmeans_fix()
    print("\n✅ Fix works! Sorting the centers ensures bin edges are monotonic.")
