import ast
print("Tuple[()]:")
print(ast.dump(ast.parse("Tuple[()]", mode='eval'), indent=2))
print("\nTuple[Tuple[()]]:")
print(ast.dump(ast.parse("Tuple[Tuple[()]]", mode='eval'), indent=2))
print("\nTuple[int,]:")
print(ast.dump(ast.parse("Tuple[int,]", mode='eval'), indent=2))
