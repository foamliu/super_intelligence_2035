
import re

# Current regex from the file
current_regex = r'\A[\w.@+-]+\Z'
# Old regex mentioned in the issue
old_regex = r'^[\w.@+-]+$'

test_cases = [
    "validuser",
    "user.name123",
    "user@domain.com",
    "user+tag",
    "user-name",
    "invalid user",  # space should fail
    "user\n",  # trailing newline
    "\nuser",  # leading newline
    "user\nname",  # newline in middle
]

print("Testing current regex (\\A...\\Z):")
for test in test_cases:
    match = re.match(current_regex, test)
    if match:
        print(f"✓ '{test}' matched")
    else:
        print(f"✗ '{test}' did not match")

print("\nTesting old regex (^...$):")
for test in test_cases:
    match = re.match(old_regex, test)
    if match:
        print(f"✓ '{test}' matched")
    else:
        print(f"✗ '{test}' did not match")
