"""
Write tests.

Steps to write a unit test for a single function
  - autoformat code (maintain indentation)
  - obtain context
    - function
      - code
      - list of external references (functions, variables, classes, etc)
    - class
      - signature of parent class and sibling functions if it exists
    - file
        - filepath relative to project root
        - signature of sibling functions in file
        - import statements in the same file
        - docstring of the file
    - project
        - project "readme"
        - signature of any functions used in the function
        - examples of it being called from other parts of the codebase
  - look for gaps in context
    - create missing docstrings
    - create missing readme
  - generate tests
    - summarize code line by line
    - create list of scenarios and subscenarios we want to test
    - create list of rare or unexpected edge cases (with examples)
    - for each test:
       - check if valid code and autoformat
  - output test to proper location


"""
import logging
import os.path
from pathlib import Path

from hasty_coder import openai_cli
from hasty_coder.filewalk import find_project_root
from hasty_coder.langlib.python import (
    CodeSnippet,
    format_code,
    get_func_and_class_snippets_in_path,
    import_path_to_file_path,
)
from hasty_coder.log_utils import configure_logging
from hasty_coder.utils import ensure_dir_exists

logger = logging.getLogger(__name__)


def write_test(code_snippet, project_plan=None):
    prompt = f"""
INSTRUCTIONS:
Write unit tests for the following code snippet. Use the pytest library. Use the pytest `monkeypatch` fixture to mock any external calls.

CODE SNIPPET:
```
{code_snippet}
```

UNIT TESTS:"""
    test_code = openai_cli.completion(prompt)
    return test_code


def write_single_test(snippet: CodeSnippet, project_plan=None):
    test_module_path, test_function_name = snippet.expected_test_location
    prompt = f"""
INSTRUCTIONS:
Write a single unit test, `{test_function_name}`, that tests `{snippet.ast_path_str}` which is imported from `{snippet.module_path}`.
The code snippet to be tests is below.
Use the pytest library. Use the pytest `monkeypatch` fixture to mock any external calls.
If it makes sense, use parameters (@pytest.mark.parametrize) to test multiple scenarios (no more than 20 scenarios).

CODE SNIPPET:
```
{snippet.formatted_code_text_with_imports}
```

UNIT TESTS:"""
    test_code = openai_cli.completion(prompt)
    format_code(test_code)
    return test_code


def build_out_test_suite(path):
    pass


def enumerate_needed_tests(path):
    testable_functions = {}
    existing_tests = {}
    have_tests = []
    needed_tests = []
    project_root = find_project_root(path)

    for snippet in get_func_and_class_snippets_in_path(path, project_root=project_root):
        if snippet.module_path.startswith("tests"):
            existing_tests[(snippet.module_path, snippet.ast_path_str)] = snippet
            continue
        testable_functions[snippet.expected_test_location] = snippet

    for test_location, snippet in testable_functions.items():
        if test_location in existing_tests:
            have_tests.append(test_location)
        else:
            needed_tests.append((*test_location, snippet))

    needed_tests = list(needed_tests)
    needed_tests.sort()

    return needed_tests


def create_test_suite(path):
    needed_tests = enumerate_needed_tests(path)
    project_root = find_project_root(path)
    for test_import_path, test_function_name, snippet in needed_tests:
        assert "." not in test_function_name
        logger.info(
            f"Writing test {test_import_path}:{test_function_name} for {snippet.module_path}:{snippet.ast_path_str}"
        )
        logger.debug(f"Snippet: {snippet.code_text}")

        test_filepath = import_path_to_file_path(test_import_path)
        test_filepath = os.path.join(project_root, test_filepath)

        test_dir = os.path.dirname(test_filepath)
        ensure_dir_exists(test_dir)
        Path(test_filepath).touch()

        test_code = write_single_test(snippet, test_function_name)
        # test_code = ""
        logger.debug(f"Test code: {test_code}")

        with open(test_filepath) as f:
            f.write("\n")
            f.write(test_code)
            f.write("\n\n")


if __name__ == "__main__":
    configure_logging("DEBUG")
    create_test_suite(
        "/Users/bryce/projects/hasty-coder/hasty_coder/tasklib/filegen_handlers"
    )
