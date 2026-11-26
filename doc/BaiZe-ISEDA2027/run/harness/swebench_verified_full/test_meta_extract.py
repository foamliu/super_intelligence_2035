from sphinx.ext.autodoc import extract_metadata

doc = ":meta public:"
metadata = extract_metadata(doc)
print(f"Metadata for '{doc}': {metadata}")

doc2 = """This is a test.

:meta public:
"""
metadata2 = extract_metadata(doc2)
print(f"Metadata for doc2: {metadata2}")
