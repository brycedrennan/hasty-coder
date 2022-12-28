import ast
import os.path
import textwrap
import tokenize
from dataclasses import dataclass
from io import BytesIO

from black import FileMode, format_str

from hasty_coder.filewalk import get_nonignored_file_paths

from .foo import bar

bar.me()


def extract_first_docstring(code_text):
    """
    Extract the first docstring from a code text.

    todo: should I have used ast.get_docstring?
    """
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


def get_file_docstring(path):
    """Return the docstring of a given Python file."""
    with open(path, encoding="utf-8") as f:
        file_sourcecode = f.read()
    mod_ast = ast.parse(file_sourcecode)
    return ast.get_docstring(mod_ast)


def add_docstring_to_file(filename, docstring):
    with open(filename, encoding="utf-8") as f:
        file_sourcecode = f.read()
    tree = ast.parse(file_sourcecode)

    tree.doc = docstring
    ast.fix_missing_locations(tree)

    code = ast.unparse(tree)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)


def add_docstring_to_sourcecode(sourcecode, docstring):
    tokens = tokenize.tokenize(BytesIO(sourcecode.encode("utf-8")).readline)
    new_tokens = []
    prev_token = None
    token_line_offset = 0
    docstring_linecount = docstring.count("\n") + 1
    for token in tokens:
        if prev_token and prev_token.type == tokenize.ENCODING:
            docstring_wrapped = f'"""{docstring}"""\n'
            doc_token = tokenize.TokenInfo(
                type=tokenize.STRING,
                string=docstring_wrapped,
                start=(prev_token.end[0] + 1, 0),
                end=(prev_token.end[0] + 1 + docstring_linecount, 0),
                line=docstring_wrapped,
            )
            token_line_offset = docstring_linecount
            new_tokens.append(doc_token)

        new_token = token._replace(
            start=(token.start[0] + token_line_offset, token.start[1]),
            end=(token.end[0] + token_line_offset, token.end[1]),
        )

        new_tokens.append(new_token)
        prev_token = new_token

    return tokenize.untokenize(new_tokens).decode("utf-8")


def validate_python_ast_equal(code_text_a, code_text_b):
    """Validate that two pieces of Python code have the same abstract syntax tree (AST)."""
    tree_a = ast.parse(textwrap.dedent(code_text_a))
    tree_b = ast.parse(textwrap.dedent(code_text_b))
    for node_a, node_b in zip(ast.walk(tree_a), ast.walk(tree_b), strict=True):
        try:
            ds = ast.get_docstring(node_b)
            if ds:
                node_b.body.pop(0)
                break

        except TypeError:
            pass
        assert type(node_a) == type(node_b)

    if ast.dump(tree_a) != ast.dump(tree_b):
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
                name=node.name,
            )
            snippets.append(snippet)
    return snippets


def format_code(code_text):
    return format_str(code_text, mode=FileMode())


@dataclass
class CodeSnippet:
    code_text: str
    start_line: int = None
    end_line: int = None
    filepath: str = None
    snippet_type: str = None
    name: str = None

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
        Use ast to find assigned variables in a code snippet.
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
        Use ast to find all references in the function body.
        """
        tree = ast.parse(self.code_text)
        refs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                refs.append(node.id)
        return refs


def walk_python_files(path):
    return get_nonignored_file_paths(path, extensions=[".py"])


def get_func_and_class_snippets_in_path(path):
    """Return snippets of functions and classes from a given path."""
    for rel_path in get_nonignored_file_paths(path, extensions=[".py"]):
        full_path = os.path.join(path, rel_path)
        with open(full_path, encoding="utf-8") as f:
            file_sourcecode = f.read()

        for snippet in get_func_and_class_snippets(file_sourcecode, filepath=full_path):
            yield snippet
