import ast
import os.path
import textwrap
import tokenize
from dataclasses import dataclass
from io import BytesIO

from black import FileMode, format_str


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


def get_func_and_class_snippets(code: str, filepath: str = None):
    """Return snippets of functions and classes from a given code string."""
    tree = ast.parse(code)
    lines = code.splitlines()
    snippets = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = len(lines) + 1
            end_line = 0

            for decorator in node.decorator_list:
                start_line = min(start_line, decorator.lineno)
                end_line = max(end_line, decorator.end_lineno)
            start_line = min(start_line, node.lineno)
            end_line = max(end_line, node.end_lineno)
            code_text = "\n".join(lines[start_line - 1 : end_line]) + "\n"
            snippet = CodeSnippet(
                code_text=code_text,
                start_line=start_line,
                end_line=end_line,
                filepath=filepath,
            )
            snippets.append(snippet)
    return snippets


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


def format_code(code_text):
    return format_str(code_text, mode=FileMode())


@dataclass
class CodeSnippet:
    code_text: str
    start_line: int = None
    end_line: int = None
    filepath: str = None
    snippet_type: str = None

    @property
    def docstring(self):
        return extract_first_docstring(self.code_text)

    @property
    def formatted_code_text(self):
        code_text = textwrap.dedent(self.code_text)
        return format_code(code_text)

    @property
    def assigned_variables(self):
        """
        Use ast to find assigned variables in a code snippet
        """
        tree = ast.parse(self.code_text)
        variables = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)

    @property
    def references(self):
        """
        Use ast to find all references in the function body
        """
        tree = ast.parse(self.code_text)
        refs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                refs.append(node.id)
        return refs


def walk_nonignored_files(path, extensions=None):
    for root, dirs, files in os.walk(path):
        # exclude directories in ignore_dirs by editing dirs in place
        dirs[:] = [
            d for d in dirs if d not in ignore_dirs and not d.endswith(".egg-info")
        ]
        for file in files:
            full_path = os.path.join(root, file)
            if extensions is not None:
                if not any(full_path.endswith(e) for e in extensions):
                    continue

            yield full_path


def walk_python_files(path):
    return walk_nonignored_files(path, extensions=[".py"])


def get_func_and_class_snippets_in_path(path):
    """Return snippets of functions and classes from a given path"""
    for full_path in walk_nonignored_files(path, extensions=".py"):
        with open(full_path, "r", encoding="utf-8") as f:
            file_sourcecode = f.read()

        for snippet in get_func_and_class_snippets(file_sourcecode, filepath=full_path):
            yield snippet
