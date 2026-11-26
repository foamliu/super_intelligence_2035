
import sys
import os

# Add django to path
sys.path.insert(0, os.path.join(os.getcwd(), 'django'))

from django.db.models.query_utils import Q

print("Q class methods:")
for attr in dir(Q):
    if '__' in attr:
        print(f"  {attr}")

print("\nDoes Q have __xor__?", hasattr(Q, '__xor__'))
