from hasty_coder.models import SoftwareStack


def test_software_stack_as_markdown():
    software_stack = SoftwareStack(
        primary_programming_language="Python",
        secondary_programming_languages=["JavaScript", "Go"],
        primary_framework="Flask",
        secondary_frameworks=["React", "Echo"],
        testing_tooling=["pytest", "Jest"],
    )

    markdown = software_stack.as_markdown()
    expected_markdown = """
- Programming Languages: **Python**. JavaScript, Go
- Frameworks: **Flask**. React, Echo
- Testing Tooling: pytest, Jest
    """
    assert markdown.strip() == expected_markdown.strip()
