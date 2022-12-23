from hasty_coder.langlib.python import get_func_and_class_snippets

sample_code = """
BASE_PATH = ""
max_words = 32

def get_file_contents(filename):
    with open(filename, "rb") as f:
        return f.read()
        
def count_words(filename):
    max_words = max_words + 1
    contents = get_file_contents(BASE_PATH + filename)
    return len(contents.split())
    
"""


def test_get_func_and_class_snippets():
    snippets = get_func_and_class_snippets(sample_code)
    assert len(snippets) == 2
    assert snippets[0].code_text.startswith("def get_file_contents(filename):")
    assert snippets[1].code_text.startswith("def count_words(filename):")

    s = snippets[1]
    assert s.assigned_variables == ["max_words", "contents"]
