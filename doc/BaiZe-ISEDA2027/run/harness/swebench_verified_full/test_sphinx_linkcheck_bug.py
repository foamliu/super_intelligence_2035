#!/usr/bin/env python3
import os
import tempfile
import shutil
from sphinx.cmd.build import build_main

def test_linkcheck_bug():
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
        
        # Create index.rst with the broken link
        index_rst = """
Test Project
============

`foo <https://google.com/test.txt#test>`_
"""
        with open(os.path.join(srcdir, 'index.rst'), 'w') as f:
            f.write(index_rst)
        
        # Run linkcheck
        argv = ['-b', 'linkcheck', srcdir, outdir]
        result = build_main(argv)
        
        # Read the output
        output_txt = os.path.join(outdir, 'output.txt')
        if os.path.exists(output_txt):
            with open(output_txt, 'r') as f:
                output = f.read()
            print("Linkcheck output:")
            print(output)
            
            # Check if the error is the correct 404, not anchor not found
            if "404 Client Error: Not Found" in output:
                print("\n✅ FIXED: Correctly reports 404 error instead of anchor not found!")
                return True
            elif "Anchor 'test' not found" in output:
                print("\n❌ BUG PRESENT: Reports anchor not found instead of 404 error!")
                return False
            else:
                print("\n⚠️  Unexpected output")
                return False
        else:
            print("No output.txt found, linkcheck may have failed to run")
            return False

if __name__ == "__main__":
    success = test_linkcheck_bug()
    exit(0 if success else 1)
