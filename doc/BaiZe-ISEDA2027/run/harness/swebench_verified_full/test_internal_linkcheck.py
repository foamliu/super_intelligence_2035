#!/usr/bin/env python3
import os
import tempfile
import shutil
from sphinx.cmd.build import build_main

def test_internal_linkcheck():
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
"""
        with open(os.path.join(srcdir, 'conf.py'), 'w') as f:
            f.write(conf_py)
        
        # Create index.rst with the broken links as described in the issue
        index_rst = """
Test Project
============

broken external-link_
broken local-link_

.. _external-link: https://lkfqhlkghflkhs
.. _local-link: doesntexist
"""
        with open(os.path.join(srcdir, 'index.rst'), 'w') as f:
            f.write(index_rst)
        
        # Run linkcheck
        argv = ['-b', 'linkcheck', srcdir, outdir]
        result = build_main(argv)
        
        # Read the output
        output_txt = os.path.join(outdir, 'output.txt')
        output_json = os.path.join(outdir, 'output.json')
        
        if os.path.exists(output_txt):
            with open(output_txt, 'r') as f:
                output = f.read()
            print("Linkcheck output.txt:")
            print(output)
        
        if os.path.exists(output_json):
            with open(output_json, 'r') as f:
                json_content = f.read()
            print("\nLinkcheck output.json:")
            print(json_content)
        
        # Check if local link is marked as broken
        if "doesntexist" in output and "broken" in output:
            print("\n✅ SUCCESS: Local link is correctly marked as broken!")
            return True
        else:
            print("\n❌ FAIL: Local link is not marked as broken!")
            return False

if __name__ == "__main__":
    success = test_internal_linkcheck()
    exit(0 if success else 1)