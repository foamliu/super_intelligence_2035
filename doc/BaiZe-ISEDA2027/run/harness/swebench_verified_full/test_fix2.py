import ast
from sphinx.domains.python import addnodes, nodes

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
        elif not node.elts:
            result.append(addnodes.desc_sig_punctuation('', '()'))
        return result
    else:
        raise SyntaxError

# Test empty tuple
tree = ast.parse("Tuple[()]", mode='eval').body
result = unparse(tree)
text_parts = []
for node in result:
    text_parts.append(node.astext())
print(f"Tuple[()] → {''.join(text_parts)}")
assert ''.join(text_parts) == 'Tuple[()]', f"Expected 'Tuple[()]', got '{''.join(text_parts)}'"
print("✓ Correct!")

# Test normal tuple
tree2 = ast.parse("Tuple[int, str]", mode='eval').body
result2 = unparse(tree2)
text_parts2 = [n.astext() for n in result2]
print(f"\nTuple[int, str] → {''.join(text_parts2)}")
assert ''.join(text_parts2) == 'Tuple[int, str]'
print("✓ Correct!")

# Test single element tuple
tree3 = ast.parse("Tuple[int,]", mode='eval').body
result3 = unparse(tree3)
text_parts3 = [n.astext() for n in result3]
print(f"\nTuple[int,] → {''.join(text_parts3)}")
assert ''.join(text_parts3) == 'Tuple[int]' or ''.join(text_parts3) == 'Tuple[int,]'
print("✓ Correct!")

print("\n✅ All tests passed!")
