from itertools import zip_longest
import math

class Point:
    def __init__(self, *coords):
        self.coords = coords
    
    def __iter__(self):
        return iter(self.coords)
    
    def distance(self, other):
        """Calculate Euclidean distance between two points, handling different dimensions by padding with 0s."""
        return math.sqrt(sum((a - b)**2 for a, b in zip_longest(self, other, fillvalue=0)))

# Test the fix
if __name__ == "__main__":
    p1 = Point(2, 0)
    p2 = Point(1, 0, 2)
    dist = p1.distance(p2)
    print(f"Distance between {p1.coords} and {p2.coords}: {dist}")
    print(f"Expected: sqrt(5) ≈ {math.sqrt(5)}")
    assert abs(dist - math.sqrt(5)) < 1e-9, f"Expected {math.sqrt(5)}, got {dist}"
    print("✅ Fix works correctly!")
