import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'swebench_verified_full', 'django'))
import django
from django.db import models, transaction
from django.conf import settings

# Configure Django settings
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        '__main__',
    ],
)

django.setup()

# Define models
class Product(models.Model):
    sku = models.CharField(primary_key=True, max_length=50)
    
    def __str__(self):
        return self.sku

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Order for {self.product}"

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Product)
    schema_editor.create_model(Order)

print("Testing issue...")
try:
    with transaction.atomic():
        order = Order()
        order.product = Product()
        order.product.sku = "foo"
        order.product.save()
        order.save()
        
        # Check the issue
        assert Order.objects.filter(product_id="").exists(), "Expected order with product_id=''"
        print("❌ ISSUE CONFIRMED: Order has product_id='' instead of 'foo'")
        assert not Order.objects.filter(product=order.product).exists(), "Expected order not to be found with product"
        print("❌ ISSUE CONFIRMED: Order not found with product relation")
        
except Exception as e:
    print(f"Error: {e}")

print("\nTesting working case (PK set before assignment)...")
try:
    with transaction.atomic():
        order = Order()
        order.product = Product(sku="bar")
        order.product.save()
        order.save()
        
        assert Order.objects.filter(product=order.product).exists()
        print("✅ Working case passes: Order found correctly")
        assert Order.objects.filter(product_id="bar").exists()
        print("✅ Working case passes: product_id is set correctly")
        
except Exception as e:
    print(f"Error: {e}")

print("\nTesting with AutoField PK to confirm it works...")
class AutoProduct(models.Model):
    name = models.CharField(max_length=50)

class AutoOrder(models.Model):
    product = models.ForeignKey(AutoProduct, on_delete=models.CASCADE)

with connection.schema_editor() as schema_editor:
    schema_editor.create_model(AutoProduct)
    schema_editor.create_model(AutoOrder)

try:
    with transaction.atomic():
        order = AutoOrder()
        order.product = AutoProduct()
        order.product.name = "test"
        order.product.save()
        order.save()
        
        assert AutoOrder.objects.filter(product=order.product).exists()
        print("✅ AutoField PK case works correctly")
        
except Exception as e:
    print(f"Error: {e}")
