import pytest

from hasty_coder.utils import slugify


@pytest.mark.parametrize(
    "input_string,expected_output",
    [
        ("HelloWorld", "hello-world"),
        ("Hello World", "hello-world"),
        ("Hello-World", "hello-world"),
        ("Hello_World", "hello-world"),
        ("Hello World!", "hello-world"),
        ("Hello        World!", "hello-world"),
        ("SockOMatic", "sock-o-matic"),
    ],
)
def test_slugify(input_string, expected_output):
    """Test slugify function with various inputs and expected outputs"""
    assert slugify(input_string) == expected_output
