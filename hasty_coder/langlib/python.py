import ast
import os.path
import textwrap
import tokenize
from io import BytesIO


def extract_first_docstring(code_text):
    """Extract the first docstring from a code text."""
    tokens = tokenize.tokenize(BytesIO(code_text.encode("utf-8")).readline)

    in_function_definition = False
    func_def_seen = False

    for token in tokens:
        if token.type == tokenize.NAME and token.string in ["def", "class"]:
            in_function_definition = True
            func_def_seen = True
        # if we see a newline token, and we're currently in a function definition,
        # this means the function definition has ended
        elif token.type == tokenize.NEWLINE and in_function_definition:
            in_function_definition = False
            continue

        if func_def_seen and not in_function_definition:
            if token.type == tokenize.INDENT:
                continue
            if token.type == tokenize.STRING:
                return token.string
            break

    return ""


def add_docstring(code_text, docstring_text):
    """Add a docstring to a given code text."""

    tokens = tokenize.tokenize(BytesIO(code_text.encode("utf-8")).readline)

    in_function_definition = False
    indentation_level = 0

    for token in tokens:
        # print(tok_name[token.type], token.string)
        if token.type == tokenize.NAME and token.string in ["def", "class"]:
            # if this is the start of a function definition, set the flag to indicate that
            in_function_definition = True
            indentation_level = token.start[1]
        elif token.type == tokenize.NEWLINE:
            # if we see a newline, and we are inside a function definition. line breaks inside the definition are
            # `tokenize.NL` tokens
            # this means the function definition has ended, so we can insert the docstring
            if in_function_definition:
                code_lines = code_text.splitlines()
                # pad the docstring with newlines to match the indentation of the code
                docstring_text = (
                    " " * (indentation_level + 4) + f'"""{docstring_text.strip()}"""'
                )
                code_lines.insert(token.end[0], docstring_text)
                new_code_text = "\n".join(code_lines)
                validate_python_ast_equal(code_text, new_code_text)
                return new_code_text + "\n"

    return code_text


def validate_python_ast_equal(code_text_a, code_text_b):
    """Validate that two pieces of Python code have the same abstract syntax tree (AST)."""
    tree_a = ast.parse(textwrap.dedent(code_text_a))
    tree_b = ast.parse(textwrap.dedent(code_text_b))
    # print(ast.dump(tree_a))
    # print(ast.dump(tree_b))
    for node_a, node_b in zip(ast.walk(tree_a), ast.walk(tree_b)):
        try:
            ds = ast.get_docstring(node_b)
            if ds:
                node_b.body.pop(0)
                break

        except TypeError:
            pass
        # print(type(node_a), type(node_b))
        # assert type(node_a) == type(node_b)

    if ast.dump(tree_a) != ast.dump(tree_b):
        print(ast.dump(tree_a))
        print(ast.dump(tree_b))
        raise ValueError("ASTs are not equal")


def get_func_and_class_snippets(code: str):
    """Return snippets of functions and classes from a given code string."""
    tree = ast.parse(code)
    lines = code.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = len(lines) + 1
            end_line = 0

            for decorator in node.decorator_list:
                start_line = min(start_line, decorator.lineno)
                end_line = max(end_line, decorator.end_lineno)
            start_line = min(start_line, node.lineno)
            end_line = max(end_line, node.end_lineno)

            yield start_line, end_line, "\n".join(
                lines[start_line - 1 : end_line]
            ) + "\n"


# todo pull in gitignore files from https://github.com/github/gitignore
ignore_dirs = [
    "venv",
    ".git",
    "node_modules",
    "__pycache__",
    "build",
    ".idea",
    "dist",
    "",
]


def get_func_and_class_snippets_in_path(path):
    """Return snippets of functions and classes from a given path"""

    for root, dirs, files in os.walk(path):
        # exclude directories in ignore_dirs by editing dirs in place
        dirs[:] = [
            d for d in dirs if d not in ignore_dirs and not d.endswith(".egg-info")
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)

            with open(full_path, "r", encoding="utf-8") as f:
                file_sourcecode = f.read()
                for (
                    start_line_no,
                    end_line_no,
                    code_snippet,
                ) in get_func_and_class_snippets(file_sourcecode):
                    yield full_path, start_line_no, end_line_no, code_snippet
