#!/usr/bin/env python3
import os
import tempfile
import shutil
from sphinx.cmd.build import build_main

def test_internal_label_linkcheck():
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
        
        # Create index.rst with a reference to a non-existent label
        index_rst = """
Test Project
============

See :ref:`non-existent-label` for more info.

Another reference to a non-existent document: :doc:`non-existent-doc`
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
            print("Linkcheck output.txt:")
            print(output)
        
        # Check if references are marked as broken
        has_ref_broken = "non-existent-label" in output
        has_doc_broken = "non-existent-doc" in output
        
        if has_ref_broken and has_doc_broken:
            print("\n✅ SUCCESS: Both label and document references are marked as broken!")
            return True
        else:
            if not has_ref_broken:
                print("\n❌ FAIL: Label reference not marked as broken!")
            if not has_doc_broken:
                print("\n❌ FAIL: Document reference not marked as broken!")
            return False

if __name__ == "__main__":
    success = test_internal_label_linkcheck()
    exit(0 if success else 1)