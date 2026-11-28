#!/usr/bin/env python3
import os
import tempfile
import shutil
from sphinx.cmd.build import build_main

def test_internal_link_with_anchor():
    # Create a temporary directory for our test project
    with tempfile.TemporaryDirectory() as tmpdir:
        srcdir = os.path.join(tmpdir, 'source')
        outdir = os.path.join(tmpdir, 'build')
        os.makedirs(srcdir)
        
        # Create conf.py
        conf_py = """
project = 'proj'
author = 'me'
release = '1.0'
language = 'en'
extensions = []
linkcheck_anchors = True
"""
        with open(os.path.join(srcdir, 'conf.py'), 'w') as f:
            f.write(conf_py)
        
        # Create index.rst
        index_rst = """
Test Project
============

See :doc:`other#non-existent-anchor`

See :doc:`other#existing-anchor`
"""
        with open(os.path.join(srcdir, 'index.rst'), 'w') as f:
            f.write(index_rst)
        
        # Create other.rst
        other_rst = """
Other Page
==========

.. _existing-anchor:

This section has an anchor.
"""
        with open(os.path.join(srcdir, 'other.rst'), 'w') as f:
            f.write(other_rst)
        
        # Run linkcheck
        argv = ['-b', 'linkcheck', srcdir, outdir]
        result = build_main(argv)
        
        # Read the output
        output_txt = os.path.join(outdir, 'output.txt')
        if os.path.exists(output_txt):
            with open(output_txt, 'r') as f:
                output = f.read()
            print("Linkcheck output.txt:")
            print(output)
        
        # Check if non-existent anchor is broken
        if "non-existent-anchor" in output and "broken" in output:
            print("\n✅ SUCCESS: Non-existent anchor in local file is marked as broken!")
            return True
        else:
            print("\n❌ FAIL: Non-existent anchor not marked as broken!")
            return False

if __name__ == "__main__":
    success = test_internal_link_with_anchor()
    exit(0 if success else 1)