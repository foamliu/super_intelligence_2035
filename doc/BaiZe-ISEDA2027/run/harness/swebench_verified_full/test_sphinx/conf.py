import os
import sys
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'numpydoc',
]

project = 'Test'
copyright = '2026, Test'
author = 'Test'
release = '0.1'

html_theme = 'alabaster'
