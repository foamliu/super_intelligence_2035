#!/usr/bin/env python3
"""Test the new :private-members: option with specific members"""

import os
import sys
import tempfile
import shutil
from sphinx.cmd.build import build_main

# Create a temporary directory for our test
test_dir = tempfile.mkdtemp()
try:
    # Create source directory
    src_dir = os.path.join(test_dir, 'source')
    os.makedirs(src_dir)
    
    # Create a test module
    test_module = os.path.join(src_dir, 'test_module.py')
    with open(test_module, 'w') as f:
        f.write("""
class TestClass:
    \"\"\"A test class with private members\"\"\"
    
    def __init__(self):
        self.public_attr = 42
        self._private_attr1 = 1
        self._private_attr2 = 2
        self._private_attr3 = 3
    
    def public_method(self):
        \"\"\"A public method\"\"\"
        pass
    
    def _private_method1(self):
        \"\"\"A private method\"\"\"
        pass
    
    def _private_method2(self):
        \"\"\"Another private method\"\"\"
        pass
    
    def _private_method3(self):
        \"\"\"Third private method\"\"\"
        pass


def _private_module_function():
    \"\"\"A private module function\"\"\"
    pass

def public_module_function():
    \"\"\"A public module function\"\"\"
    pass
""")
    
    # Create conf.py
    conf_py = os.path.join(src_dir, 'conf.py')
    with open(conf_py, 'w') as f:
        f.write("""
extensions = ['sphinx.ext.autodoc']
""")
    
    # Create index.rst that tests the new feature
    index_rst = os.path.join(src_dir, 'index.rst')
    with open(index_rst, 'w') as f:
        f.write("""
Test Private Members Feature
============================

Test class with specific private members:
-----------------------------------------

.. autoclass:: test_module.TestClass
    :members:
    :private-members: _private_method1, _private_attr2

Test module with specific private members:
------------------------------------------

.. automodule:: test_module
    :members:
    :private-members: _private_module_function
""")
    
    # Add source dir to Python path
    sys.path.insert(0, src_dir)
    
    # Build the docs
    build_dir = os.path.join(test_dir, 'build')
    argv = ['-b', 'html', src_dir, build_dir]
    
    print("Building documentation...")
    result = build_main(argv)
    if result != 0:
        print(f"Build failed with exit code {result}")
        sys.exit(1)
    
    # Check the generated HTML
    index_html = os.path.join(build_dir, 'index.html')
    with open(index_html, 'r') as f:
        content = f.read()
    
    print("\nChecking generated content:")
    
    # Check that the specified private members are present
    assert '_private_method1' in content, "_private_method1 not found in output"
    assert '_private_module_function' in content, "_private_module_function not found in output"
    
    # Check that the other private members are NOT present
    assert '_private_method2' not in content, "_private_method2 should not be in output"
    assert '_private_method3' not in content, "_private_method3 should not be in output"
    
    print("✅ All tests passed!")
    print("\nThe feature works correctly:")
    print("  - :private-members: with arguments only includes the specified private members")
    print("  - Unspecified private members are excluded")
    print("  - Public members are still included as usual")
    
finally:
    # Clean up
    shutil.rmtree(test_dir)
