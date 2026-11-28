from flask import Blueprint

# This should raise ValueError but currently doesn't
try:
    bp = Blueprint("", __name__)
    print("ERROR: Empty blueprint name allowed! This is the bug.")
except ValueError as e:
    print(f"SUCCESS: Got expected error: {e}")

# This should work as normal
try:
    bp = Blueprint("test", __name__)
    print("SUCCESS: Normal blueprint name works.")
except Exception as e:
    print(f"ERROR: Normal blueprint name failed: {e}")
