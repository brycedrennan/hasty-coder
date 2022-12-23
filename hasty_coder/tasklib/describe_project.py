from pathlib import Path


def find_project_root(start_path):
    """
    Traverse up from a starting path to find the project root.

    The project root is identified by the presence of a '.git' directory inside it.
    """
    current_path = Path(start_path)

    while current_path != current_path.root:
        if (current_path / ".git").exists():
            return str(current_path)

        current_path = current_path.parent

    return None
