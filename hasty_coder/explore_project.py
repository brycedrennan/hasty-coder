import os.path

PROJECT_ROOT_FILES = ("pyproject.toml", "setup.py", ".git")


def find_project_root(starting_path, trigger_files=PROJECT_ROOT_FILES, max_depth=4):
    """Find the root of a project by looking for trigger files."""
    trigger_files = set(trigger_files)

    current_path = os.path.abspath(starting_path)
    for _ in range(max_depth):
        if any(os.path.exists(os.path.join(current_path, f)) for f in trigger_files):
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            return None
        current_path = parent_path
    return None
