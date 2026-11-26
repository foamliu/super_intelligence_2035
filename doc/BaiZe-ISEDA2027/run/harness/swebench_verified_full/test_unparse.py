import ast
from typing import List

class Node:
    pass

class Text(Node):
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return f"Text({self.s!r})"

class Punctuation(Node):
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return f"Punctuation({self.s!r})"

def unparse(node: ast.AST) -> List[Node]:
    if isinstance(node, ast.Attribute):
        return [Text("%s.%s" % (unparse(node.value)[0].s, node.attr))]
    elif isinstance(node, ast.Expr):
        return unparse(node.value)
    elif isinstance(node, ast.Index):
        return unparse(node.value)
    elif isinstance(node, ast.List):
        result = [Punctuation('[')]
        for elem in node.elts:
            result.extend(unparse(elem))
            result.append(Punctuation(', '))
        if result:  # Only pop if there are elements
            result.pop()
        result.append(Punctuation(']'))
        return result
    elif isinstance(node, ast.Module):
        return sum((unparse(e) for e in node.body), [])
    elif isinstance(node, ast.Name):
        return [Text(node.id)]
    elif isinstance(node, ast.Subscript):
        result = unparse(node.value)
        result.append(Punctuation('['))
        result.extend(unparse(node.slice))
        result.append(Punctuation(']'))
        return result
    elif isinstance(node, ast.Tuple):
        result = []
        for elem in node.elts:
            result.extend(unparse(elem))
            result.append(Punctuation(', '))
        if result:  # Fix: only pop if not empty
            result.pop()
        return result
    else:
        raise SyntaxError  # unsupported syntax

# Test empty tuple
code = "Tuple[()]"
tree = ast.parse(code, mode='eval')
print("Testing", code)
result = unparse(tree.body)
print("Result:", result)
# Expected: [Text('Tuple'), Punctuation('['), Punctuation(']')]

# Test normal tuple
code2 = "Tuple[int, str]"
tree2 = ast.parse(code2, mode='eval')
print("\nTesting", code2)
result2 = unparse(tree2.body)
print("Result:", result2)
# Expected: [Text('Tuple'), Punctuation('['), Text('int'), Punctuation(', '), Text('str'), Punctuation(']')]

# Test empty list
code3 = "List[]"
tree3 = ast.parse(code3, mode='eval')
print("\nTesting", code3)
result3 = unparse(tree3.body)
print("Result:", result3)
