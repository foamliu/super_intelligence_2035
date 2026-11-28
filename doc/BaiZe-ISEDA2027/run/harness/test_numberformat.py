import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'swebench_verified_full', 'django'))

from decimal import Decimal
from django.conf import settings
settings.configure(
    USE_L10N=False,
    USE_THOUSAND_SEPARATOR=False,
)
from django.utils.numberformat import format as nformat

# Test cases from the issue
print("Testing 1e-199 with decimal_pos=2:", nformat(Decimal('1e-199'), '.', decimal_pos=2))
print("Testing 1e-200 with decimal_pos=2:", nformat(Decimal('1e-200'), '.', decimal_pos=2))

# Additional test cases
print("\nAdditional tests:")
print("Testing 0.001 with decimal_pos=2:", nformat(Decimal('0.001'), '.', decimal_pos=2))
print("Testing 0.01 with decimal_pos=2:", nformat(Decimal('0.01'), '.', decimal_pos=2))
print("Testing 0.1 with decimal_pos=2:", nformat(Decimal('0.1'), '.', decimal_pos=2))
print("Testing 1 with decimal_pos=2:", nformat(Decimal('1'), '.', decimal_pos=2))
print("Testing 1e200 with decimal_pos=2:", nformat(Decimal('1e200'), '.', decimal_pos=2)[:30] + "...") # Truncate long output
print("Testing -1e-200 with decimal_pos=2:", nformat(Decimal('-1e-200'), '.', decimal_pos=2))
print("Testing 1e-5 with decimal_pos=4:", nformat(Decimal('1e-5'), '.', decimal_pos=4))
print("Testing 1e-4 with decimal_pos=4:", nformat(Decimal('1e-4'), '.', decimal_pos=4))
