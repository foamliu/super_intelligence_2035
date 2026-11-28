from django.core.files.storage import FileSystemStorage, default_storage
from django.db.models.fields.files import FileField

def get_runtime_storage():
    """Callable storage that returns different storages based on runtime conditions."""
    import os
    if os.environ.get('ENVIRONMENT') == 'production':
        return FileSystemStorage(location='/production/media')
    else:
        return FileSystemStorage(location='/development/media')

# Test the bug fix
field = FileField(storage=get_runtime_storage, upload_to='documents')

# During makemigrations, deconstruct() is called
name, path, args, kwargs = field.deconstruct()

# Check that storage is the original callable, not evaluated instance
print(f"Storage in kwargs: {kwargs.get('storage')}")
print(f"Is it the original callable? {kwargs.get('storage') is get_runtime_storage}")
print(f"Is it a storage instance? {isinstance(kwargs.get('storage'), FileSystemStorage)}")

# Check runtime behavior still works
print(f"\nRuntime storage location (dev): {field.storage.location}")

# Check that upload_to behaves the same way
def dynamic_upload_path(instance, filename):
    return f'uploads/{filename}'

field2 = FileField(storage=get_runtime_storage, upload_to=dynamic_upload_path)
name2, path2, args2, kwargs2 = field2.deconstruct()
print(f"\nupload_to is original callable: {kwargs2.get('upload_to') is dynamic_upload_path}")
