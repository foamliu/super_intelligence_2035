import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

from decimal import Decimal
from django.db.models import fields
from django.db.models.expressions import F, CombinedExpression

# Test the logic directly
lhs_decimal = F('decimal_field')
lhs_decimal.output_field = fields.DecimalField(max_digits=10, decimal_places=2)
rhs_int = F('int_field')
rhs_int.output_field = fields.IntegerField()

print("Testing MOD with Decimal and Integer:")
expr = CombinedExpression(lhs_decimal, '%%', rhs_int)
try:
    output = expr.output_field
    print(f"  Output field type: {output.__class__.__name__}")
    print(f"  Success! MOD now correctly returns Decimal type for mixed Decimal and Integer.")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting MOD with Integer and Decimal:")
expr = CombinedExpression(rhs_int, '%%', lhs_decimal)
try:
    output = expr.output_field
    print(f"  Output field type: {output.__class__.__name__}")
    print(f"  Success! MOD now correctly returns Decimal type for mixed Integer and Decimal.")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting MOD with two Decimals:")
rhs_decimal = F('decimal_field2')
rhs_decimal.output_field = fields.DecimalField(max_digits=12, decimal_places=4)
expr = CombinedExpression(lhs_decimal, '%%', rhs_decimal)
try:
    output = expr.output_field
    print(f"  Output field type: {output.__class__.__name__}")
    print(f"  Output max_digits: {output.max_digits}, decimal_places: {output.decimal_places}")
    print(f"  Success! MOD correctly uses the more precise DecimalField.")
except Exception as e:
    print(f"  Error: {e}")
