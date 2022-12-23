from hasty_coder.tasklib.write_tests import write_test

code_example = """
def get_email(key_obj):
    cache_path = "/tmp"
    filepath = f"{cache_path}/{key_obj.key}"
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except FileNotFoundError:
        data = key_obj.get_contents_as_string()
        with open(filepath, "wb+") as f:
            f.write(data)

    with open(filepath, "rb") as f:
        return f.read()
"""


def test_write_test():
    test_code = write_test(code_example)

    print(test_code)
