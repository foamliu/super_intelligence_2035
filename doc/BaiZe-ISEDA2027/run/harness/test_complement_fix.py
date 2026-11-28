from sympy import symbols, FiniteSet, Interval, Complement

x, y = symbols('x y')
a = FiniteSet(x, y, 2)
b = Interval(-10, 10)
result = Complement(a, b)
print(f"Complement({a}, {b}) = {result}")
print(f"Expected: Complement(FiniteSet(x, y), Interval(-10, 10))")

# Test another case: element definitely not in interval
c = FiniteSet(x, y, 11)
result2 = Complement(c, b)
print(f"\nComplement({c}, {b}) = {result2}")
print(f"Expected: Union(FiniteSet(11), Complement(FiniteSet(x, y), Interval(-10, 10)))")
