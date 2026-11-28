import re

# Match the beginning of a named or unnamed group.
named_group_matcher = re.compile(r'\(\?P(<\w+>)')
# Match opening parentheses that are not part of a named group
unnamed_group_matcher = re.compile(r'\((?!\?P<)')


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


def replace_unnamed_groups(pattern):
    r"""
    Find unnamed groups in `pattern` and replace them with '<var>'. E.g.,
    1. ^(?P<a>\w+)/b/(\w+)$ ==> ^(?P<a>\w+)/b/<var>$
    2. ^(?P<a>\w+)/b/((x|y)\w+)$ ==> ^(?P<a>\w+)/b/<var>$
    """
    unnamed_group_indices = [m.start(0) for m in unnamed_group_matcher.finditer(pattern)]
    # Indices of the start of unnamed capture groups.
    group_indices = []
    # Loop over the start indices of the groups.
    for start in unnamed_group_indices:
        # Handle nested parentheses, e.g. '^b/((x|y)\w+)$'.
        unmatched_open_brackets, prev_char = 1, None
        for idx, val in enumerate(pattern[start + 1:]):
            # Check for unescaped `(` and `)`. They mark the start and end of
            # a nested group.
            if val == '(' and prev_char != '\\':
                unmatched_open_brackets += 1
            elif val == ')' and prev_char != '\\':
                unmatched_open_brackets -= 1
            prev_char = val
            if unmatched_open_brackets == 0:
                group_indices.append((start, start + 1 + idx + 1))
                break
        # If we reached the end of the string and brackets are balanced, add the group
        else:
            if unmatched_open_brackets == 0:
                group_indices.append((start, len(pattern)))

    # Remove unnamed group matches inside other unnamed capture groups.
    group_start_end_indices = []
    prev_end = None
    for start, end in group_indices:
        if prev_end and start > prev_end or not prev_end:
            group_start_end_indices.append((start, end))
        prev_end = end

    if group_start_end_indices:
        # Replace unnamed groups with <var>. Handle the fact that replacing the
        # string between indices will change string length and thus indices
        # will point to the wrong substring if not corrected.
        final_pattern, prev_end = [], None
        for start, end in group_start_end_indices:
            if prev_end:
                final_pattern.append(pattern[prev_end:start])
            else:
                final_pattern.append(pattern[:start])
            final_pattern.append('<var>')
            prev_end = end
        final_pattern.append(pattern[prev_end:])
        return ''.join(final_pattern)
    else:
        return pattern


def simplify_regex(pattern):
    r"""
    Clean up urlpattern regexes into something more readable by humans. For
    example, turn "^(?P<sport_slug>\w+)/athletes/(?P<athlete_slug>\w+)/$"
    into "/<sport_slug>/athletes/<athlete_slug>/".
    """
    pattern = replace_named_groups(pattern)
    pattern = replace_unnamed_groups(pattern)
    # clean up any outstanding regex-y characters.
    pattern = pattern.replace('^', '').replace('$', '').replace('?', '')
    if not pattern.startswith('/'):
        pattern = '/' + pattern
    return pattern


# Test case from the issue
test_path = r'entries/(?P<pk>[^/.]+)/relationships/(?P<related_field>\w+)'
expected = '/entries/<pk>/relationships/<related_field>'
result = simplify_regex(test_path)
print(f"Test simplify_regex without trailing slash:")
print(f"Input:    {test_path}")
print(f"Expected: {expected}")
print(f"Got:      {result}")
print(f"Pass: {result == expected}\n")

# Test with unnamed group at end
test_unnamed = r'items/(\d+)/details/(\w+)'
expected_unnamed = '/items/<var>/details/<var>'
result_unnamed = simplify_regex(test_unnamed)
print(f"Test simplify_regex with unnamed groups at end:")
print(f"Input:    {test_unnamed}")
print(f"Expected: {expected_unnamed}")
print(f"Got:      {result_unnamed}")
print(f"Pass: {result_unnamed == expected_unnamed}\n")

# Test with both named and unnamed at end
test_mixed = r'^(?P<category>\w+)/(\d+)/items/(?P<id>\w+)$'
expected_mixed = '/<category>/<var>/items/<id>'
result_mixed = simplify_regex(test_mixed)
print(f"Test simplify_regex mixed groups at end:")
print(f"Input:    {test_mixed}")
print(f"Expected: {expected_mixed}")
print(f"Got:      {result_mixed}")
print(f"Pass: {result_mixed == expected_mixed}")
