#!/usr/bin/env python3
"""Simple test for Referrer-Policy header logic."""

# Let's just test the logic directly without full Django imports
class MockResponse(dict):
    def setdefault(self, key, value):
        if key not in self:
            self[key] = value
        return self[key]

# Test the logic that would run in process_response
def test_referrer_policy_logic(referrer_policy_setting, existing_header=None):
    response = MockResponse()
    if existing_header:
        response['Referrer-Policy'] = existing_header
    
    if referrer_policy_setting:
        response.setdefault('Referrer-Policy', referrer_policy_setting)
    
    return response.get('Referrer-Policy')

print("Testing Referrer-Policy logic:")
print("-" * 50)

# Test default case
result = test_referrer_policy_logic('same-origin')
print(f"Default setting 'same-origin': {result}")
assert result == 'same-origin'
print("✓ Correct")

# Test custom value
result = test_referrer_policy_logic('strict-origin-when-cross-origin')
print(f"Custom setting 'strict-origin-when-cross-origin': {result}")
assert result == 'strict-origin-when-cross-origin'
print("✓ Correct")

# Test None setting
result = test_referrer_policy_logic(None)
print(f"None setting: {result}")
assert result is None
print("✓ Correct")

# Test existing header is preserved
result = test_referrer_policy_logic('same-origin', 'no-referrer')
print(f"Existing header 'no-referrer' with setting 'same-origin': {result}")
assert result == 'no-referrer'
print("✓ Correct, existing header not overridden")

print("\nAll logic tests passed! ✅")

# Now let's verify the actual code changes by checking the file contents
print("\nVerifying code changes:")
print("-" * 50)

# Check global_settings.py
with open('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django/django/conf/global_settings.py', 'r') as f:
    content = f.read()
    if "SECURE_REFERRER_POLICY = 'same-origin'" in content:
        print("✓ SECURE_REFERRER_POLICY default added to global_settings.py")
    else:
        print("✗ SECURE_REFERRER_POLICY missing from global_settings.py")

# Check security.py init
with open('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django/django/middleware/security.py', 'r') as f:
    content = f.read()
    if 'self.referrer_policy = settings.SECURE_REFERRER_POLICY' in content:
        print("✓ SECURE_REFERRER_POLICY loaded in SecurityMiddleware __init__")
    else:
        print("✗ SECURE_REFERRER_POLICY not loaded in __init__")
    
    if "if self.referrer_policy:\n            response.setdefault('Referrer-Policy', self.referrer_policy)" in content:
        print("✓ Referrer-Policy header set in process_response")
    else:
        print("✗ Referrer-Policy header not set in process_response")

print("\nAll verifications complete!")
