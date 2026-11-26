
import django
django.setup()

from django.db.models import (
    Case, Exists, Expression, ExpressionList, ExpressionWrapper, F, Func,
    OuterRef, RowRange, Subquery, Value, ValueRange, When, Window, WindowFrame
)
from django.utils.deconstruct import deconstructible

# Test each class
test_classes = [
    (F, ('name',)),
    (OuterRef, ('name',)),
    (Value, (1,)),
    (Func, (F('a'), F('b'),), {'function': 'GREATEST'}),
    (ExpressionList, (F('a'), F('b'))),
    (ExpressionWrapper, (F('a') + F('b'),), {'output_field': django.db.models.IntegerField()}),
    (When, (), {'condition': F('a') > 1, 'then': Value('yes')}),
    (Case, (When(a__gt=1, then=Value('yes')),), {'default': Value('no')}),
    (Subquery, (django.db.models.QuerySet(model=django.contrib.contenttypes.models.ContentType).values('id')[:1],)),
    (Exists, (django.db.models.QuerySet(model=django.contrib.contenttypes.models.ContentType).filter(id=1),)),
    (Window, (Func(F('a'), function='SUM'),), {'partition_by': F('b')}),
    (WindowFrame, (), {'start': 0, 'end': 1}),
    (RowRange, (), {'start': -2, 'end': 0}),
    (ValueRange, (), {'start': -1, 'end': 1}),
]

print("Testing deconstruction paths:")
print("=" * 80)

all_ok = True
for cls, args, kwargs in test_classes + [(cls, args, {}) for cls, args, kwargs in test_classes if kwargs]:
    instance = cls(*args, **kwargs)
    path, _args, _kwargs = instance.deconstruct()
    expected_path = f"django.db.models.{cls.__name__}"
    ok = path == expected_path
    all_ok &= ok
    status = "✓" if ok else "✗"
    print(f"{status} {cls.__name__}: {path} {'(correct)' if ok else f'(expected: {expected_path})'}")

print("=" * 80)
if all_ok:
    print("All deconstruction paths are correct!")
else:
    print("Some paths are incorrect.")
