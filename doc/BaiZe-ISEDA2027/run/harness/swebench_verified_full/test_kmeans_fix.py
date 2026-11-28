from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

# Generate some data
X, y = make_blobs(n_samples=10000, centers=10, n_features=2, random_state=2)

# Run KMeans with various n_jobs values
for n_jobs in range(1, 5):
    kmeans = KMeans(n_clusters=10, random_state=2, n_jobs=n_jobs, n_init=10)
    kmeans.fit(X)
    print(f'(n_jobs={n_jobs}) kmeans.inertia_ = {kmeans.inertia_}')
