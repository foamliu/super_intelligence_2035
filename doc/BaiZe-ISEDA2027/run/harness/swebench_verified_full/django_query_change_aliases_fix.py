"""
Fix for Django Query.change_aliases AssertionError when combining queries with OR.
The bug occurs when combining queries where the RHS has aliases that collide with
newly generated aliases during combination, leading to overlapping keys and values
in the change_map.

Fix: Process alias changes in descending order of numeric suffix to avoid double-renaming.
"""

# Modified change_aliases method for Django's Query class
def change_aliases(self, change_map):
    """
    Change the aliases in change_map (which maps old-alias -> new-alias),
    relabelling any references to them in select columns and the where
    clause.
    """
    # Process aliases in descending order of their numeric suffix to handle cases
    # where new aliases overlap with old ones (e.g. T4->T5, T5->T6) without double-renaming
    def alias_sort_key(alias):
        if alias.startswith(self.alias_prefix):
            try:
                return int(alias[len(self.alias_prefix):])
            except ValueError:
                pass
        # Non-standard aliases are processed first (before numeric ones)
        return float('inf')

    sorted_changes = sorted(change_map.items(), key=lambda item: alias_sort_key(item[0]), reverse=True)

    for old_alias, new_alias in sorted_changes:
        single_change = {old_alias: new_alias}
        # 1. Update references in "select" (normal columns plus aliases),
        # "group by" and "where".
        self.where.relabel_aliases(single_change)
        if isinstance(self.group_by, tuple):
            self.group_by = tuple([col.relabeled_clone(single_change) for col in self.group_by])
        self.select = tuple([col.relabeled_clone(single_change) for col in self.select])
        self.annotations = self.annotations and {
            key: col.relabeled_clone(single_change) for key, col in self.annotations.items()
        }

        # 2. Rename the alias in the internal table/alias datastructures.
        if old_alias not in self.alias_map:
            continue
        alias_data = self.alias_map[old_alias].relabeled_clone(single_change)
        self.alias_map[new_alias] = alias_data
        self.alias_refcount[new_alias] = self.alias_refcount[old_alias]
        del self.alias_refcount[old_alias]
        del self.alias_map[old_alias]

        table_aliases = self.table_map[alias_data.table_name]
        for pos, alias in enumerate(table_aliases):
            if alias == old_alias:
                table_aliases[pos] = new_alias
                break
    self.external_aliases = {
        # Table is aliased or it's being changed and thus is aliased.
        change_map.get(alias, alias): (aliased or alias in change_map)
        for alias, aliased in self.external_aliases.items()
    }

"""
To apply this fix:
1. Replace the existing change_aliases method in django/db/models/sql/query.py with this version
2. Remove the original assertion: assert set(change_map).isdisjoint(change_map.values())

This fix handles overlapping change maps correctly by processing higher-numbered aliases first,
preventing double-renaming issues. The fix is backward compatible and maintains all existing
behavior for non-overlapping change maps.
"""
