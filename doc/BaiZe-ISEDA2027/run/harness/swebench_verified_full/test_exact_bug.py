import sympy as sy

def buggy_eval_row_join(self, other):
    if self.rows == 0:
        return other
    if other.rows == 0:
        return self
    cols = self.cols
    def entry(i, j):
        if j < cols:
            return self[i, j]
        return other[i, j - cols]
    return sy.Matrix(self.rows, self.cols + other.cols, entry)

# Test 0 rows case
M1 = sy.Matrix.zeros(0, 0)
M2 = sy.Matrix.zeros(0, 1)
M3 = sy.Matrix.zeros(0, 2)
M4 = sy.Matrix.zeros(0, 3)

res = M1
for m in [M2, M3, M4]:
    res = buggy_eval_row_join(res, m)
    print(f"Step: {res.shape}")

print(f"Final shape: {res.shape}") # This will be (0, 3), exactly what the user reported!

# Test 1 row case
M1 = sy.Matrix.zeros(1, 0)
M2 = sy.Matrix.zeros(1, 1)
M3 = sy.Matrix.zeros(1, 2)
M4 = sy.Matrix.zeros(1, 3)

res = M1
for m in [M2, M3, M4]:
    res = buggy_eval_row_join(res, m)
print(f"1 row case shape: {res.shape}") # This will be (1, 6), correct!
