from sympy import Point

p1 = Point(2, 0)
p2 = Point(1, 0, 2)

print(f"p1: {p1}, dim: {p1.ambient_dimension}")
print(f"p2: {p2}, dim: {p2.ambient_dimension}")

normalized = Point._normalize_dimension(p1, p2)
print(f"Normalized p1: {normalized[0]}, dim: {normalized[0].ambient_dimension}")
print(f"Normalized p2: {normalized[1]}, dim: {normalized[1].ambient_dimension}")

dist = p1.distance(p2)
print(f"Distance: {dist}")
print(f"Expected: sqrt(5) = {5**0.5}")
