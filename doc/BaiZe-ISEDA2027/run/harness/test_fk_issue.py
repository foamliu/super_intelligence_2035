import os
import sys
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
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
)

django.setup()

# Define test models
class Product(models.Model):
    sku = models.CharField(primary_key=True, max_length=50)
    
    class Meta:
        app_label = 'test'

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Product)
    schema_editor.create_model(Order)

# Test the issue scenario
print("Testing the issue scenario...")
try:
    with transaction.atomic():
        order = Order()
        order.product = Product()
        order.product.sku = "foo"
        order.product.save()
        order.save()
        
        # Check the assertions from the issue
        assert not Order.objects.filter(product_id="").exists(), "Order should not have empty product_id"
        assert Order.objects.filter(product=order.product).exists(), "Order should be linked to product"
        
        # Also check the values directly
        order.refresh_from_db()
        assert order.product_id == "foo", f"Expected product_id 'foo', got '{order.product_id}'"
        
        print("✅ Test passed! The issue is fixed.")
        
except AssertionError as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)

# Test with auto primary key
print("\nTesting with AutoField primary key...")
class AutoProduct(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        app_label = 'test'

class AutoOrder(models.Model):
    product = models.ForeignKey(AutoProduct, on_delete=models.CASCADE)
    
    class Meta:
        app_label = 'test'

with connection.schema_editor() as schema_editor:
    schema_editor.create_model(AutoProduct)
    schema_editor.create_model(AutoOrder)

try:
    with transaction.atomic():
        order = AutoOrder()
        order.product = AutoProduct(name="test")
        order.product.save()
        order.save()
        
        order.refresh_from_db()
        assert order.product_id == order.product.id, f"Expected product_id {order.product.id}, got {order.product_id}"
        assert AutoOrder.objects.filter(product=order.product).exists()
        
        print("✅ AutoField test passed!")
        
except AssertionError as e:
    print(f"❌ AutoField test failed: {e}")
    sys.exit(1)

print("\nAll tests passed!")
