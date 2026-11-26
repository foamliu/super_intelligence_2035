"""Test that :meta public: works for variables."""
import os
import tempfile
import shutil
from sphinx.cmd.build import build_main

def test_meta_public_for_variables():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create source files
        srcdir = os.path.join(tmpdir, 'src')
        outdir = os.path.join(tmpdir, 'out')
        os.makedirs(srcdir)
        
        # example.py
        with open(os.path.join(srcdir, 'example.py'), 'w') as f:
            f.write("""_foo = None  #: :meta public:
_bar = 123  #: This is a private variable without public meta.
public_var = 456  #: This is a public variable.
""")
        
        # index.rst
        with open(os.path.join(srcdir, 'index.rst'), 'w') as f:
            f.write(""".. automodule:: example
   :members:
""")
        
        # conf.py
        with open(os.path.join(srcdir, 'conf.py'), 'w') as f:
            f.write("""extensions = ['sphinx.ext.autodoc']
master_doc = 'index'
""")
        
        # Build the docs
        args = ['-b', 'html', srcdir, outdir]
        result = build_main(args)
        assert result == 0, "Build failed"
        
        # Check the output
        index_html = os.path.join(outdir, 'index.html')
        with open(index_html, 'r') as f:
            content = f.read()
        
        # Check that _foo is present (public meta)
        assert '_foo' in content, "_foo should be present (has :meta public:)"
        # Check that _bar is not present (no public meta)
        assert '_bar' not in content, "_bar should not be present (no :meta public:)"
        # Check that public_var is present
        assert 'public_var' in content, "public_var should be present"
        
        print("Test passed! :meta public: works for variables.")

if __name__ == '__main__':
    test_meta_public_for_variables()
