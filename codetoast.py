import ast

with open("sourcecode.py", "r") as f:
    code = f.read()

tree = ast.parse(code)
ast_output = ast.dump(tree, indent=2)

with open("ast_output.txt", "w") as f:
    f.write(ast_output)

print("AST output saved to ast_output.txt")
