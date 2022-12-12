import logging

from hasty_coder.langlib.python import (
    add_docstring,
    extract_first_docstring,
    get_func_and_class_snippets_in_path,
)
from hasty_coder.utils import LoggedOpenAI, parallel_run

logger = logging.getLogger(__name__)


def describe_code_snippet(code_snippet):
    prompt = f"""
Write a very-short, concise single-line docstring for each function and class below.

The docstrings describe the purpose of the code.
The docstrings should not be generic.  Things that look like "Create a FooBar object..." are too generic.
The docstrings should be in the imperative mood. 

Return your docstrings in a json dict where the keys are line numbers and the values are descriptions.

INPUT CODE:
```
{code_snippet}
```

DOCSTRINGS (as json dict):
```json
"""
    comments = LoggedOpenAI(temperature=0)(
        prompt, as_json=True, stop=["INPUT CODE", "```"]
    )
    comment = list(comments.values())[0]
    logger.info(f"Got docstring: {comment}")
    return comment


def _add_comments_to_code_snippet(code_snippet_row):
    full_path, start_line_no, end_line_no, code_snippet = code_snippet_row
    docstring = describe_code_snippet(code_snippet)
    new_code_snippet = add_docstring(code_snippet, docstring)

    # shorten the snippets
    code_snippet, new_code_snippet = _remove_identical_lines_from_end(
        code_snippet, new_code_snippet
    )
    return (
        full_path,
        start_line_no,
        start_line_no + len(code_snippet.splitlines()) - 1,
        code_snippet,
        new_code_snippet,
    )


def _remove_identical_lines_from_end(text_a, text_b):
    """Remove identical lines from the end of two texts."""
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    while lines_a and lines_b and lines_a[-1] == lines_b[-1]:
        lines_a.pop()
        lines_b.pop()
    return "".join(lines_a), "".join(lines_b)


def add_comments_to_all_code_in_path(path):
    # gather code snippets
    code_snippet_rows = []
    for (
        full_path,
        start_line_no,
        end_line_no,
        code_snippet,
    ) in get_func_and_class_snippets_in_path(path):
        docstring = extract_first_docstring(code_snippet)
        if docstring:
            continue
        code_snippet_rows.append((full_path, start_line_no, end_line_no, code_snippet))
    logger.info(f"Found {len(code_snippet_rows)} code snippets in need of docstrings.")

    result_rows = parallel_run(_add_comments_to_code_snippet, code_snippet_rows)

    # edit in reverse order so the line numbers don't become inaccurate as we make edits
    result_rows.sort(reverse=True)
    for (
        full_path,
        start_line_no,
        end_line_no,
        code_snippet,
        new_code_snippet,
    ) in result_rows:
        # todo: do all edits to a single file at once
        edit_file(full_path, start_line_no, end_line_no, new_code_snippet)


def edit_file(filepath, start_line_no, end_line_no, injected_content):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    replacing = lines[start_line_no - 1 : end_line_no]
    print("REPLACING:")
    print("|" + "".join(replacing) + "|")
    print("WITH:")
    print(f"|{injected_content}|")
    lines[start_line_no - 1 : end_line_no] = injected_content.splitlines(keepends=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    project_path = "/Users/bryce/projects/pwdgen"
    add_comments_to_all_code_in_path(project_path)
