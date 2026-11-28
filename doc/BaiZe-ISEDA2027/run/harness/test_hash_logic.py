# Simulate the fix
creation_counter = 1

class MockField:
    def __init__(self):
        global creation_counter
        self.creation_counter = creation_counter
        creation_counter += 1
    
    def __eq__(self, other):
        if isinstance(other, MockField):
            return (
                self.creation_counter == other.creation_counter
                and getattr(self, 'model', None) is getattr(other, 'model', None)
            )
        return NotImplemented
    
    # OLD __hash__ (buggy)
    # def __hash__(self):
    #     if hasattr(self, 'model'):
    #         return hash((self.creation_counter, self.model))
    #     return hash(self.creation_counter)
    
    # NEW __hash__ (fixed)
    def __hash__(self):
        return hash(self.creation_counter)

# Test case
f = MockField()
d = {f: 1}
print(f"Hash before assignment: {hash(f)}")
print(f"Is f in d before assignment? {f in d}")

# Assign "model"
class MockModel:
    pass

f.model = MockModel
print(f"Hash after assignment: {hash(f)}")
print(f"Is f in d after assignment? {f in d}")

assert f in d, "Field not found after assignment!"
print("Test passed!")

# Also verify equality still works for different models
f2 = MockField()
f2.creation_counter = f.creation_counter
f2.model = MockModel()
print(f"\nSame creation_counter, different model: f == f2? {f == f2}")
print(f"Same hash: {hash(f) == hash(f2)}")
d2 = {f: 1, f2: 2}
print(f"Both in dict, len(d2) = {len(d2)} (should be 2)")
assert len(d2) == 2, "Different fields with same creation_counter incorrectly considered equal!"
print("All tests passed!")
