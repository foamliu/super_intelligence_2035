from django.contrib.admindocs.utils import replace_named_groups

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
