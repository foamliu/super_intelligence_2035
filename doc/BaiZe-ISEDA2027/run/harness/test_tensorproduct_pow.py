import sys
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/sympy_fix')
from sympy import *
from sympy.physics.quantum import TensorProduct as tp
from sympy.physics.quantum import tensor_product_simp as tps
from sympy.physics.paulialgebra import Pauli
a = Symbol('a', commutative=False)

print("Test 1: tp(1,1)*tp(1,1)")
t1 = tp(1,1)*tp(1,1)
print(f"Input: {t1}")
print(f"tps(t1): {tps(t1)}")
print(f"t1.expand(tensorproduct=True): {t1.expand(tensorproduct=True)}")
print(f"Expected: 1 or 1x1")

print("\nTest 2: tp(1,Pauli(3))*tp(1,Pauli(3))")
t2 = tp(1,Pauli(3))*tp(1,Pauli(3))
print(f"Input: {t2}")
print(f"tps(t2): {tps(t2)}")
print(f"t2.expand(tensorproduct=True): {t2.expand(tensorproduct=True)}")
print(f"Expected: 1 or 1x1")

print("\nTest 3: tps(tp(1,1)*tp(1,a)).subs(a, 1)")
res = tps(tp(1,1)*tp(1,a)).subs(a, 1)
print(f"Result: {res}")

print("\nTest 4: tps(tp(1,Pauli(3))*tp(1,a)).subs(a, Pauli(3))")
res2 = tps(tp(1,Pauli(3))*tp(1,a)).subs(a, Pauli(3))
print(f"Result: {res2}")

print("\nTest 5: (tp(a, a)**3).expand(tensorproduct=True)")
t3 = (tp(a, a)**3)
print(f"Input: {t3}")
print(f"Expanded: {t3.expand(tensorproduct=True)}")
print(f"Expected: (a**3)x(a**3)")

