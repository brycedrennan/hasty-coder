import ast
import os.path
import re
import textwrap
import tokenize
from ast import iter_child_nodes
from collections import deque
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from black import FileMode, format_str

from hasty_coder.filewalk import get_nonignored_filepaths


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


def walk(node):
    """
    Recursively yield all descendant nodes in the tree starting at *node*
    (including *node* itself), in no specified order.  This is useful if you
    only want to modify nodes in place and don't care about the context.
    """
    to_visit = deque([node])
    while to_visit:
        node = to_visit.popleft()
        to_visit.extend(iter_child_nodes(node))


def get_func_and_class_snippets(
    code: str, filepath: str = None, project_root: str = None
):
    """Return snippets of functions and classes from a given code string."""
    tree = ast.parse(code)
    lines = code.splitlines()
    import_nodes = []
    snippets = []
    to_visit = deque([tree])
    filepath = Path(filepath) if filepath else None
    project_root = Path(project_root) if project_root else None
    project_path = None
    if project_root:
        project_path = filepath.relative_to(project_root)
    while to_visit:
        node = to_visit.popleft()

        for child in ast.iter_child_nodes(node):
            child.parent = node
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_nodes.append(node)
            # import_line_nums.add(node.lineno)
            # import_lines = sorted(import_line_nums)
            # import_lines = [lines[i - 1] for i in import_lines]
            # import_code = "\n".join(import_lines)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = len(lines) + 1
            end_line = 0

            for decorator in node.decorator_list:
                start_line = min(start_line, decorator.lineno)
                end_line = max(end_line, decorator.end_lineno)
            start_line = min(start_line, node.lineno)
            end_line = max(end_line, node.end_lineno)
            code_text = "\n".join(lines[start_line - 1 : end_line]) + "\n"

            parent_path = []
            cur_node = node
            while cur_node is not None:
                parent_path.append(cur_node)
                cur_node = getattr(cur_node, "parent", None)
            refs = []
            for fnode in ast.walk(node):
                if isinstance(fnode, ast.Name):
                    refs.append(fnode.id)
            imports_src = filter_imports(import_nodes, refs)

            s = CodeSnippet(
                code_text=code_text,
                start_line=start_line,
                end_line=end_line,
                filepath=filepath,
                project_path=project_path,
                project_root=project_root,
                imports_src=imports_src,
                name=node.name,
                snippet_type=node.__class__.__name__,
                ast_path=parent_path,
            )

            snippets.append(s)

        to_visit.extend(iter_child_nodes(node))
    return snippets


def filter_imports(imports, var_names):
    var_set = set(var_names)
    filtered_imports = []
    for node in imports:
        if isinstance(node, ast.ImportFrom):
            node.names = [name for name in node.names if name.name in var_set]
            if node.names:
                filtered_imports.append(node)
        elif isinstance(node, ast.Import):
            node.names = [name for name in node.names if name.name in var_set]
            if node.names:
                filtered_imports.append(node)
    root_node = ast.Module(body=filtered_imports)
    return ast.unparse(root_node)


def format_code(code_text):
    return format_str(code_text, mode=FileMode())


@dataclass
class CodeSnippet:
    code_text: str
    start_line: int = None
    end_line: int = None
    filepath: str = None
    project_path: str = None
    project_root: str = None
    snippet_type: str = None
    imports_src: str = None
    name: str = None
    ast_path: list = None

    @property
    def docstring(self):
        return extract_first_docstring(self.code_text)

    @property
    def formatted_code_text(self):
        code_text = textwrap.dedent(self.code_text)
        return format_code(code_text)

    @property
    def formatted_code_text_with_imports(self):
        code_text = textwrap.dedent(self.code_text)
        formatted_code = format_code(self.imports_src + "\n\n" + code_text)
        return formatted_code

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

    @property
    def module_path(self):
        """
        Return the python import path of a code snippet.

        Uses the sys.path to find the module path of a code snippet based on it's filepath
        """
        if not self.project_path:
            return None
        filepath = os.path.abspath(self.filepath)
        filepath = os.path.splitext(filepath)[0]
        proj_root = str(self.project_root) + os.sep

        if not filepath.startswith(proj_root):
            raise ValueError("The file is not in any of the PYTHONPATH directories")

        relpath = filepath[len(proj_root) :]

        dirs = relpath.split(os.sep)

        # Compute the dotted import path by replacing the os.sep separator with a dot and joining the directories
        import_path = ".".join(dirs).replace(os.sep, ".")
        return import_path

    @property
    def ast_path_str(self):
        named_nodes = [n for n in self.ast_path if hasattr(n, "name")]
        named_nodes.reverse()
        return ".".join(n.name for n in named_nodes)

    @property
    def expected_test_location(self):
        """
        Return the expected location of the test for this snippet.
        """
        if self.module_path.startswith("tests"):
            return "", ""
        module_path_parts = self.module_path.split(".")

        module_path_parts[0] = "tests"
        module_path_parts[-1] = f"test_{module_path_parts[-1]}"
        test_module_path = ".".join(module_path_parts)

        test_ast_path = camel_to_snake(self.ast_path_str.replace(".", "_"))
        test_ast_path = "test_" + test_ast_path
        test_ast_path = test_ast_path.strip("_")
        test_ast_path = re.sub(r"_+", "_", test_ast_path)

        return test_module_path, test_ast_path


def walk_python_files(path):
    return get_nonignored_filepaths(path, extensions=[".py"])


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def import_path_to_file_path(import_path):
    """
    Convert an import path to a file path.

    This is the inverse of the CodeSnippet.module_path property.
    """
    import_path = import_path.replace(".", os.sep)
    import_path += ".py"
    return import_path


def get_func_and_class_snippets_in_path(path, project_root=None):
    """Return snippets of functions and classes from a given path."""
    path = Path(path)
    for rel_path in get_nonignored_filepaths(path, extensions=[".py"]):
        full_path = path / rel_path
        with open(full_path, encoding="utf-8") as f:
            file_sourcecode = f.read()

        for snippet in get_func_and_class_snippets(
            file_sourcecode, filepath=full_path, project_root=project_root
        ):
            yield snippet
