import ast
code = "Tuple[()]"
tree = ast.parse(code, mode='eval')
print(ast.dump(tree, indent=2))
