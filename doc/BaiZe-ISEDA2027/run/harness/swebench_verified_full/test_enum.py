
import sys
sys.path.insert(0, 'django')
from django.db import models

# Test if TextChoices exists
try:
    from django.db.models import TextChoices
    print("TextChoices exists!")
except ImportError as e:
    print(f"TextChoices import error: {e}")

# Try IntegerChoices
try:
    from django.db.models import IntegerChoices
    print("IntegerChoices exists!")
except ImportError as e:
    print(f"IntegerChoices import error: {e}")
