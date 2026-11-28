import re

# Match the beginning of a named or unnamed group.
named_group_matcher = re.compile(r'\(\?P(<\w+>)')

def replace_named_groups(pattern):
    r"""
    Find named groups in `pattern` and replace them with the group name. E.g.,
    1. ^(?P<a>\w+)/b/(\w+)$ ==> ^<a>/b/(\w+)$
    2. ^(?P<a>\w+)/b/(?P<c>\w+)/$ ==> ^<a>/b/<c>/$
    3. ^(?P<a>\w+)/b/(\w+) ==> ^<a>/b/(\w+)
    4. ^(?P<a>\w+)/b/(?P<c>\w+) ==> ^<a>/b/<c>
    """
    named_group_indices = [
        (m.start(0), m.end(0), m.group(1))
        for m in named_group_matcher.finditer(pattern)
    ]
    # Tuples of (named capture group pattern, group name).
    group_pattern_and_name = []
    # Loop over the groups and their start and end indices.
    for start, end, group_name in named_group_indices:
        # Handle nested parentheses, e.g. '^(?P<a>(x|y))/b'.
        unmatched_open_brackets, prev_char = 1, None
        for idx, val in enumerate(pattern[end:]):
            # Check for unescaped `(` and `)`. They mark the start and end of a
            # nested group.
            if val == '(' and prev_char != '\\':
                unmatched_open_brackets += 1
            elif val == ')' and prev_char != '\\':
                unmatched_open_brackets -= 1
            prev_char = val
            # If brackets are balanced, the end of the string for the current
            # named capture group pattern has been reached.
            if unmatched_open_brackets == 0:
                group_pattern_and_name.append((pattern[start:end + idx + 1], group_name))
                break
        # If we reached the end of the string and brackets are balanced, add the group
        else:
            if unmatched_open_brackets == 0:
                group_pattern_and_name.append((pattern[start:], group_name))

    # Replace the string for named capture groups with their group names.
    for group_pattern, group_name in group_pattern_and_name:
        pattern = pattern.replace(group_pattern, group_name)
    return pattern

# Test case from the issue
test_path = r'entries/(?P<pk>[^/.]+)/relationships/(?P<related_field>\w+)'
expected = 'entries/<pk>/relationships/<related_field>'
result = replace_named_groups(test_path)
print(f"Test without trailing slash:")
print(f"Input:    {test_path}")
print(f"Expected: {expected}")
print(f"Got:      {result}")
print(f"Pass: {result == expected}\n")

# Test with trailing slash (already worked)
test_path_trailing = r'entries/(?P<pk>[^/.]+)/relationships/(?P<related_field>\w+)/'
expected_trailing = 'entries/<pk>/relationships/<related_field>/'
result_trailing = replace_named_groups(test_path_trailing)
print(f"Test with trailing slash:")
print(f"Input:    {test_path_trailing}")
print(f"Expected: {expected_trailing}")
print(f"Got:      {result_trailing}")
print(f"Pass: {result_trailing == expected_trailing}\n")

# Test nested groups
test_nested = r'^(?P<a>(x|y))/b/(?P<c>\w+)'
expected_nested = '^<a>/b/<c>'
result_nested = replace_named_groups(test_nested)
print(f"Test nested groups:")
print(f"Input:    {test_nested}")
print(f"Expected: {expected_nested}")
print(f"Got:      {result_nested}")
print(f"Pass: {result_nested == expected_nested}\n")

# Test group at end with $
test_end_dollar = r'^items/(?P<id>\d+)$'
expected_end_dollar = '^items/<id>$'
result_end_dollar = replace_named_groups(test_end_dollar)
print(f"Test group at end with $:")
print(f"Input:    {test_end_dollar}")
print(f"Expected: {expected_end_dollar}")
print(f"Got:      {result_end_dollar}")
print(f"Pass: {result_end_dollar == expected_end_dollar}")
