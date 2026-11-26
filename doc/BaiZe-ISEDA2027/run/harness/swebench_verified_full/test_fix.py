import sys
import os
sys.path.insert(0, os.path.abspath('./sphinx_repo'))

from sphinx.ext.autodoc import ModuleDocumenter
from sphinx.ext.autodoc.directive import DocumenterBridge
from sphinx.environment import BuildEnvironment
from docutils.statemachine import StateMachine, State

# Import our test module
import test_inherited_attr

# Create a minimal environment
env = BuildEnvironment('.', '.', '_build')
env.app = type('MockApp', (), {
    'registry': type('MockRegistry', (), {
        'documenters': {},
        'autodoc_attrgettrs': {}
    })()
})()

# Create a mock directive
state = State(StateMachine())
directive = type('MockDirective', (), {
    'env': env,
    'genopt': {'members': True, 'inherited-members': True},
    'state': state,
    'result': [],
    'filename_set': set()
})()

# Test documenting the Derived class
doc = ModuleDocumenter(directive, 'test_inherited_attr')
doc.generate()

# Print the generated reST
print("Generated reST:")
print('\n'.join([line for line in directive.result if line.strip()]))

# Check if inherited_attr has the docstring
print("\n\nChecking for inherited_attr docstring:")
for line in directive.result:
    if 'inherited_attr' in line:
        print(f"Found inherited_attr line: {line.strip()}")
    if 'This is an inherited attribute' in line:
        print(f"SUCCESS: Found inherited attribute docstring: {line.strip()}")
