
# Fix for double single quote bug in FITS Card CONTINUE handling
# The bug is in the _split method of the Card class, where joined values from CONTINUE cards
# are wrapped in quotes without re-escaping single quotes, leading to double unescaping.

# The fix is to modify the line where valuecomment is constructed for CONTINUE cards:
# Original line:
# valuecomment = f"'{''.join(values)}' / {' '.join(comments)}"
# Fixed line:
# valuecomment = f"'{''.join(values).replace(\"'\", \"''\")}' / {' '.join(comments)}"

# Let's verify the fix with the user's test case:

test_code = """
from astropy.io import fits

# Test case 1: string ending with ''
print("Test 1: Strings ending with ''")
for n in range(60, 70):
    card1 = fits.Card('CONFIG', "x" * n + "''")
    card2 = fits.Card.fromstring(str(card1))
    print(n, card1.value == card2.value)
    if not card1.value == card2.value:
        print(f"Expected: {repr(card1.value)}")
        print(f"Got:      {repr(card2.value)}")

# Test case 2: '' in the middle of string
print("\\nTest 2: '' in the middle of string")
for n in range(50, 70):
    card1 = fits.Card('CONFIG', "x" * n + "''" + "x"*10)
    card2 = fits.Card.fromstring(str(card1))
    print(n, len(card1.value), card1.value == card2.value)
    if not card1.value == card2.value:
        print(f"Expected: {repr(card1.value)}")
        print(f"Got:      {repr(card2.value)}")
"""

print("The bug occurs because when processing CONTINUE cards:")
print("1. Each chunk's '' is replaced with ' during parsing")
print("2. Joined values already have the correct single quotes")
print("3. When wrapping the joined values in quotes again for re-parsing,")
print("   any adjacent single quotes become '' which are then replaced with ' again,")
print("   leading to double unescaping.")
print("\nFix: Re-escape single quotes in the joined values before wrapping in quotes:")
print("valuecomment = f\"'{''.join(values).replace(\"'\", \"''\")}' / {' '.join(comments)}\"")
