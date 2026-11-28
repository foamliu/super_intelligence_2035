import sympy as sy
from sympy.matrices.matrixbase import MatrixBase

# Simulate sympy 1.1 row_join without the special case
def buggy_row_join(self, other):
    # No special case for empty cols with matching rows
    if self.rows != other.rows:
        raise Exception(f"Shape error: {self.rows} vs {other.rows}")
    
    cols = self.cols
    def entry(i, j):
        if j < cols:
            return self[i, j]
        return other[i, j - cols]
    
    return sy.Matrix(self.rows, self.cols + other.cols, entry)

# Test with 0 rows
M1 = sy.Matrix.zeros(0, 0)
M2 = sy.Matrix.zeros(0, 1)
M3 = sy.Matrix.zeros(0, 2)
M4 = sy.Matrix.zeros(0, 3)

# Let's do the reduce manually with buggy row_join
res = M1
for m in [M2, M3, M4]:
    res = buggy_row_join(res, m)
    print(f"After adding {m.shape}: {res.shape}")

print(f"Final shape with buggy join: {res.shape} (expected: (0, 6))")

# Test with 1 row (should work)
M1 = sy.Matrix.zeros(1, 0)
M2 = sy.Matrix.zeros(1, 1)
M3 = sy.Matrix.zeros(1, 2)
M4 = sy.Matrix.zeros(1, 3)

res = M1
for m in [M2, M3, M4]:
    res = buggy_row_join(res, m)
print(f"With 1 row, shape: {res.shape} (expected: (1, 6))")
