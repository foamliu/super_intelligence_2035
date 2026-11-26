
import sys
import os

# Add django to path
sys.path.insert(0, os.path.join(os.getcwd(), 'django'))

from django.db.models import Q

print("Testing Q XOR...")
q1 = Q(id=1)
q2 = Q(id=2)
try:
    q3 = q1 ^ q2
    print(f"q1 ^ q2 = {q3}")
    q4 = q1 ^ q2 ^ q1
    print(f"q1 ^ q2 ^ q1 = {q4}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
