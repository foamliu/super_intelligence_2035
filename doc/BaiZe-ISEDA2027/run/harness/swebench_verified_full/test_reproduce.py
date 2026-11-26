import ast
from sphinx_repo.sphinx.domains.python import _parse_annotation

# Test the empty tuple case
try:
    nodes = _parse_annotation("Tuple[()]")
    print("Success! Result:", nodes)
except IndexError as e:
    print(f"Error reproduced: {e}")
    import traceback
    traceback.print_exc()
