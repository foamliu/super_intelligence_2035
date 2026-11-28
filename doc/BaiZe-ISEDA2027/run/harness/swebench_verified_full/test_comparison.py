import sympy
from sympy import Basic, Integer

class Foo():
    def __eq__(self, other):
        if isinstance(other, Basic):
            # For test, say Foo equals any Integer with value 5
            if isinstance(other, Integer) and other == 5:
                return True
        return NotImplemented

# Test case
f = Foo()
s = Integer(5)
s2 = Integer(6)

print(f"f == s: {f == s}") # Should be True
print(f"s == f: {s == f}") # Should be True if __eq__ returns NotImplemented for non-Basic
print(f"f == s2: {f == s2}") # Should be False
print(f"s2 == f: {s2 == f}") # Should be False

# Test rich comparisons
class Bar():
    def __lt__(self, other):
        if isinstance(other, Integer):
            return int(other) > 10
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Integer):
            return int(other) < 10
        return NotImplemented

b = Bar()
print(f"\nb < 5: {b < Integer(5)}") # Should be False (5 > 10 is False)
print(f"5 < b: {Integer(5) < b}") # Should call Bar.__gt__(5) which returns True (5 <10 is True)
print(f"b < 15: {b < Integer(15)}") # Should be True (15>10 is True)
print(f"15 < b: {Integer(15) < b}") # Should call Bar.__gt__(15) which returns False (15<10 is False)

# Test that if both sides return NotImplemented, we get False/True as expected
class Dummy():
    pass

d = Dummy()
print(f"\n5 == d: {Integer(5) == d}") # Should be False
print(f"5 != d: {Integer(5) != d}") # Should be True
print(f"5 < d: {Integer(5) < d}") # Should raise TypeError? Wait no, sympy returns a Relational object?
print(f"type(5 < d): {type(Integer(5) < d)}")


