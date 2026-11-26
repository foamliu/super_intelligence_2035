# Fix for inspectdb not handling foreign keys to non-PK unique fields

## Problem
When a foreign key references a non-primary key unique field of another table, `inspectdb` was incorrectly generating a ForeignKey that references the primary key of the related table instead of the actual referenced field.

## Example
For these tables:
```sql
CREATE TABLE foo ( id serial primary key, other_id int UNIQUE);
CREATE TABLE bar (
	id serial primary key, other_id int,
	constraint myconst FOREIGN KEY(other_id) references foo(other_id)
);
```

Before the fix, inspectdb generated for bar:
```python
other = models.ForeignKey(Foo, models.DO_NOTHING)
```

After the fix, it correctly generates:
```python
other = models.ForeignKey(Foo, models.DO_NOTHING, to_field='other_id')
```

## Changes made
1. Added `table_primary_keys` cache in `handle_inspection` to store primary key columns for processed tables
2. Cache primary key of each table when processing it
3. Modified relation handling to:
   - Extract both referenced column and referenced table from the relations dict
   - Fetch primary key of referenced table if not already cached
   - Add `to_field` parameter to ForeignKey if referenced column is not the primary key of the related table

## Backward Compatibility
- No breaking changes: ForeignKeys to primary keys continue to work exactly as before (no `to_field` added, which is default behavior)
- Works with all database backends that support foreign key introspection
- Handles self-referential foreign keys correctly
- Works regardless of the order tables are processed in
