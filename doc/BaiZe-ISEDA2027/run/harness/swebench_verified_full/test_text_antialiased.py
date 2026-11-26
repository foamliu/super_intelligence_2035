import sys
import os
# Add the repo matplotlib to path first
sys.path.insert(0, os.path.abspath('./matplotlib/lib'))
import matplotlib.pyplot as plt
import matplotlib as mpl

# Test 1: Text object with explicit antialiased=False
fig, ax = plt.subplots()
t1 = ax.text(0.2, 0.5, 'Antialiased OFF', fontsize=20, antialiased=False)
print(f"t1.get_antialiased() = {t1.get_antialiased()}")
assert t1.get_antialiased() == False, "Explicit antialiased=False not respected"

# Test 2: Text object with explicit antialiased=True
t2 = ax.text(0.2, 0.7, 'Antialiased ON', fontsize=20, antialiased=True)
print(f"t2.get_antialiased() = {t2.get_antialiased()}")
assert t2.get_antialiased() == True, "Explicit antialiased=True not respected"

# Test 3: Default value uses rcParams
old_aa = mpl.rcParams['text.antialiased']
mpl.rcParams['text.antialiased'] = False
t3 = ax.text(0.2, 0.3, 'Default (rcParams OFF)', fontsize=20)
print(f"t3.get_antialiased() = {t3.get_antialiased()} (rcParams was False)")
assert t3.get_antialiased() == False, "Default antialiased doesn't match rcParams"

mpl.rcParams['text.antialiased'] = True
t4 = ax.text(0.2, 0.1, 'Default (rcParams ON)', fontsize=20)
print(f"t4.get_antialiased() = {t4.get_antialiased()} (rcParams was True)")
assert t4.get_antialiased() == True, "Default antialiased doesn't match rcParams"

# Test 4: Annotation also supports antialiased parameter
ann = ax.annotate('Annotation AA OFF', xy=(0.5, 0.5), xytext=(0.6, 0.6), 
                  fontsize=15, antialiased=False)
print(f"ann.get_antialiased() = {ann.get_antialiased()}")
assert ann.get_antialiased() == False, "Annotation antialiased not respected"

ann2 = ax.annotate('Annotation AA ON', xy=(0.5, 0.3), xytext=(0.6, 0.2), 
                  fontsize=15, antialiased=True)
print(f"ann2.get_antialiased() = {ann2.get_antialiased()}")
assert ann2.get_antialiased() == True, "Annotation antialiased not respected"

# Test 5: set_antialiased works
t1.set_antialiased(True)
print(f"After set_antialiased(True), t1.get_antialiased() = {t1.get_antialiased()}")
assert t1.get_antialiased() == True, "set_antialiased not working"

# Restore rcParam
mpl.rcParams['text.antialiased'] = old_aa

plt.close(fig)
print("All tests passed! Text objects support get/set_antialiased as expected.")
