#!/usr/bin/env python3

from sphinx.application import Sphinx


__version__ = '1.0'


def replace_content(content: str) -> str:
    return content.replace("&REPLACE_ME;", "REPLACED")


def handle_source_read(app: Sphinx, docname, source):
    source[0] = replace_content(source[0])


def handle_include_read(app: Sphinx, path, parent_docname, source):
    source[0] = replace_content(source[0])


def setup(app: Sphinx):
    app.connect('source-read', handle_source_read)
    app.connect('include-read', handle_include_read)

    return dict(
        version=__version__,
        parallel_read_safe=True,
        parallel_write_safe=True
    )
