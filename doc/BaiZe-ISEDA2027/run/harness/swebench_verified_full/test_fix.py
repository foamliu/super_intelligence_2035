
import sys
import os

# Add Django to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

import django
from django.conf import settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='test-secret-key',
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)
django.setup()

from django.contrib.auth.forms import AuthenticationForm

form = AuthenticationForm()
username_field = form['username']
rendered = str(username_field)

print("Rendered username field:")
print(rendered)
print("\nChecking for maxlength attribute:")
if 'maxlength' in rendered:
    print("✅ SUCCESS: maxlength attribute found!")
    # Extract the value
    import re
    match = re.search(r'maxlength="(\d+)"', rendered)
    if match:
        print(f"   Max length value: {match.group(1)}")
else:
    print("❌ FAILURE: maxlength attribute missing!")
