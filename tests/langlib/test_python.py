import pytest

from hasty_coder.langlib.python import (
    add_docstring_to_sourcecode,
    get_func_and_class_snippets,
)

sample_code = """
BASE_PATH = ""
max_words = 32

def get_file_contents(filename):
    with open(filename, "rb") as f:
        return f.read()

def count_words(filename):
    # this is a comment
    max_words = max_words + 1
    contents = get_file_contents(BASE_PATH + filename)
    return len(contents.split())
""".lstrip()

shebang = "#!/usr/bin/env python3\n# *_* coding: utf-8 *_*\n"
single_line_docstring = "'''single line docstring'''\n"
multi_line_docstring = "'''multi\nline\ndocstring'''\n"

sample_code_params = [
    pytest.param("", id="empty string"),
    pytest.param(sample_code, id="sample code"),
    pytest.param(f"{shebang}{sample_code}", id="shebang"),
    pytest.param(
        f"{shebang}{single_line_docstring}{sample_code}",
        id="shebang-single-line-docstring",
    ),
    pytest.param(
        f"{shebang}{multi_line_docstring}{sample_code}",
        id="shebang-multi-line-docstring",
    ),
    pytest.param(f"{single_line_docstring}{sample_code}", id="single-line-docstring"),
    pytest.param(f"{multi_line_docstring}{sample_code}", id="multi-line-docstring"),
]


# def test_get_func_and_class_snippets():
#     snippets = get_func_and_class_snippets(sample_code)
#     assert len(snippets) == 2
#     assert snippets[0].code_text.startswith("def get_file_contents(filename):")
#     assert snippets[1].code_text.startswith("def count_words(filename):")
#
#     s = snippets[1]
#     assert s.assigned_variables == ["max_words", "contents"]


@pytest.mark.parametrize("sourcecode", sample_code_params)
def test_add_docstring_to_sourcecode(sourcecode):
    add_docstring_to_sourcecode(sourcecode, "added docstring")
