import ast
import sys
sys.path.insert(0, 'sphinx_repo')

# Let's directly copy the fixed unparse function here to test
from sphinx.domains.python import addnodes, nodes

def test_unparse():
    def unparse(node: ast.AST) -> list:
        if isinstance(node, ast.Attribute):
            return [nodes.Text("%s.%s" % (unparse(node.value)[0], node.attr))]
        elif isinstance(node, ast.Expr):
            return unparse(node.value)
        elif isinstance(node, ast.Index):
            return unparse(node.value)
        elif isinstance(node, ast.List):
            result = [addnodes.desc_sig_punctuation('', '[')]
            for elem in node.elts:
                result.extend(unparse(elem))
                result.append(addnodes.desc_sig_punctuation('', ', '))
            if len(result) > 1:
                result.pop()
            result.append(addnodes.desc_sig_punctuation('', ']'))
            return result
        elif isinstance(node, ast.Module):
            return sum((unparse(e) for e in node.body), [])
        elif isinstance(node, ast.Name):
            return [nodes.Text(node.id)]
        elif isinstance(node, ast.Subscript):
            result = unparse(node.value)
            result.append(addnodes.desc_sig_punctuation('', '['))
            result.extend(unparse(node.slice))
            result.append(addnodes.desc_sig_punctuation('', ']'))
            return result
        elif isinstance(node, ast.Tuple):
            result = []
            for elem in node.elts:
                result.extend(unparse(elem))
                result.append(addnodes.desc_sig_punctuation('', ', '))
            if result:
                result.pop()
            return result
        else:
            raise SyntaxError

    # Test 1: Empty tuple Tuple[()] - should not crash
    print("Test 1: Tuple[()]")
    try:
        tree = ast.parse("Tuple[()]", mode='eval').body
        result = unparse(tree)
        text_parts = []
        for node in result:
            if hasattr(node, 'astext'):
                text_parts.append(node.astext())
            else:
                text_parts.append(str(node))
        print(f"✓ Success! Output: {''.join(text_parts)}")
        assert ''.join(text_parts) == 'Tuple[]' or ''.join(text_parts) == 'Tuple[()]'
    except IndexError as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 2: Normal tuple Tuple[int, str]
    print("\nTest 2: Tuple[int, str]")
    try:
        tree = ast.parse("Tuple[int, str]", mode='eval').body
        result = unparse(tree)
        text_parts = []
        for node in result:
            if hasattr(node, 'astext'):
                text_parts.append(node.astext())
            else:
                text_parts.append(str(node))
        print(f"✓ Success! Output: {''.join(text_parts)}")
        assert ''.join(text_parts) == 'Tuple[int, str]'
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 3: List with elements List[int, str]
    print("\nTest 3: List[int, str]")
    try:
        tree = ast.parse("List[int, str]", mode='eval').body
        result = unparse(tree)
        text_parts = []
        for node in result:
            if hasattr(node, 'astext'):
                text_parts.append(node.astext())
            else:
                text_parts.append(str(node))
        print(f"✓ Success! Output: {''.join(text_parts)}")
        assert ''.join(text_parts) == 'List[int, str]'
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_unparse()
    sys.exit(0 if success else 1)
