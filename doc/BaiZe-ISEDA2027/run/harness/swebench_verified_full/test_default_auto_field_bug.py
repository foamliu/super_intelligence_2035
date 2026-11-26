import os
import sys
# Add the django directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'django'))
import django
from django.conf import settings

# Configure Django settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='test-secret-key',
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
    DEFAULT_AUTO_FIELD = "test_app.models.MyBigAutoField",
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)

# Create test app directory
test_app_dir = os.path.join(os.getcwd(), 'test_app')
os.makedirs(test_app_dir, exist_ok=True)

# Create __init__.py
with open(os.path.join(test_app_dir, '__init__.py'), 'w') as f:
    f.write('')

# Create models.py with custom BigAutoField
with open(os.path.join(test_app_dir, 'models.py'), 'w') as f:
    f.write("""
from django.db import models

class MyBigAutoField(models.BigAutoField):
    pass

class MyModel(models.Model):
    name = models.CharField(max_length=100)
""")

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Initialize Django
django.setup()

# Try to import the model
try:
    from test_app.models import MyModel
    print("Success! No error occurred.")
except ValueError as e:
    print(f"Error occurred: {e}")
    print("Bug reproduced!")
