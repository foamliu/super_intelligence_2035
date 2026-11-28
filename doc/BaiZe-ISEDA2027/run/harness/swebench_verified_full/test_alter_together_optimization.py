

import sys
import os
sys.path.insert(0, os.path.abspath('django'))

# Import only what we need to avoid circular imports
from django.db.migrations.operations.models import AlterUniqueTogether, AlterIndexTogether
from django.db.migrations.optimizer import MigrationOptimizer

# Test case from the issue
operations = [
    AlterUniqueTogether(
        name='mymodel',
        unique_together=set(),
    ),
    AlterIndexTogether(
        name='mymodel',
        index_together=set(),
    ),
    AlterUniqueTogether(
        name='mymodel',
        unique_together={("col",)},
    ),
    AlterIndexTogether(
        name='mymodel',
        index_together={("col",)},
    ),
]

optimizer = MigrationOptimizer()
optimized = optimizer.optimize(operations)

print("Original operations:")
for op in operations:
    print(f"  {op.describe()}")

print("\nOptimized operations:")
for op in optimized:
    print(f"  {op.describe()}")

# Verify the result
assert len(optimized) == 2, f"Expected 2 operations, got {len(optimized)}"
assert isinstance(optimized[0], AlterUniqueTogether)
assert optimized[0].unique_together == {("col",)}
assert isinstance(optimized[1], AlterIndexTogether)
assert optimized[1].index_together == {("col",)}

print("\n✅ Test passed! The operations are correctly optimized.")

# Test another case with multiple consecutive same-type operations
operations2 = [
    AlterUniqueTogether(name='mymodel', unique_together={('a', 'b')}),
    AlterUniqueTogether(name='mymodel', unique_together={('a', 'b'), ('c', 'd')}),
    AlterUniqueTogether(name='mymodel', unique_together={('c', 'd')}),
]

optimized2 = optimizer.optimize(operations2)
print("\nTest 2 - multiple same-type operations:")
print(f"Original length: {len(operations2)}, Optimized length: {len(optimized2)}")
assert len(optimized2) == 1
assert optimized2[0].unique_together == {('c', 'd')}
print("✅ Test 2 passed!")

