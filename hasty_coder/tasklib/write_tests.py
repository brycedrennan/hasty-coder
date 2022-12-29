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

from hasty_coder import openai_cli
from hasty_coder.langlib.python import get_func_and_class_snippets_in_path


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


def build_out_test_suite(path):
    pass


def enumerate_needed_tests(path):
    testable_functions = {}
    existing_tests = {}
    have_tests = []
    needed_tests = []
    for snippet in get_func_and_class_snippets_in_path(path):
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



if __name__ == "__main__":
    enumerate_needed_tests("/Users/bryce/projects/hasty-coder")
