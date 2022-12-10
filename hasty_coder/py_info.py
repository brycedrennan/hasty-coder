import ast


def get_function_info(code):
    # Parse the code and create an AST object
    tree = ast.parse(code)

    # Define a function that will traverse the AST and build the outline
    def build_outline(node):
        # Create a dictionary to store the information for this function

        # If the node is a FunctionDef, extract the name and external references
        if not isinstance(node, ast.FunctionDef):
            return None
        info = {}
        # Get the function name
        info["function_name"] = node.name

        # Get the list of external references in the function
        info["external_references"] = []
        defined_names = set()
        for n in ast.walk(node):
            print(n.__class__.__name__)
            if isinstance(n, ast.Name) and n.id not in defined_names:
                info["external_references"].append(n.id)
            elif isinstance(n, ast.Assign):
                defined_names.update(
                    [t.id for t in n.targets if isinstance(t, ast.Name)]
                )

        # Return the dictionary
        return info

    # Traverse the AST and build the outline
    return [info for info in map(build_outline, ast.walk(tree)) if info is not None]


# Define some Python code
code = """
def my_func(x, y):
    global z
    z = z
    z = x + y
    return z
"""

# Get the function info
info = get_function_info(code)

# Output the function info
print(info)
