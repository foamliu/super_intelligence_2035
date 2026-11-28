
The bug occurs because when `sqf_list` is given an input that is an unexpanded product of polynomial powers, the factorization processes each term separately, resulting in multiple factors with identical multiplicity values.

## Root Cause
In the `_symbolic_factor_list` function, when the input is a `Mul` expression (product of terms), each term is factorized independently. For inputs like `(x-2)**3 * (x-3)**3`, this produces two separate factors `(x-2, 3)` and `(x-3, 3)` instead of combining them into a single square-free factor `(x²-5x+6, 3)`.

## Fix Applied
Added/ensured the following code in `sympy/polys/polytools.py` at the end of `_symbolic_factor_list`:
```python
if method == 'sqf':
    factors = [(reduce(mul, (f for f, _ in factors if _ == k)), k)
               for k in sorted({i for _, i in factors})]
```
This code:
1. Groups all factors by their multiplicity value `k`
2. Multiplies together factors that share the same multiplicity to form composite square-free factors
3. Sorts factors by increasing multiplicity to maintain consistent output ordering

## Verification
Test cases:
1. `sqf_list((x**2 + 1) * (x - 1)**2 * (x - 2)**3 * (x - 3)**3)` now correctly returns:
   ```
   (1, [(x**2 + 1, 1), (x - 1, 2), (x**2 - 5*x + 6, 3)])
   ```
2. Existing correct behavior for expanded polynomials is preserved:
   `sqf_list(x**5 - 2*x**4 - 2*x**3 + 4*x**2 + x - 2)` still returns:
   ```
   (1, [(x - 2, 1), (x**2 - 1, 2)])
   ```
