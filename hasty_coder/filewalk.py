import os
from functools import lru_cache
from pathlib import Path

import pathspec


@lru_cache(maxsize=1024)
def find_project_root(start_path):
    """
    Traverse up from a starting path to find the project root.

    The project root is identified by the presence of a '.git' directory inside it.
    """
    current_path = Path(start_path)

    while current_path != current_path.root:
        if (current_path / ".git").is_dir():
            return str(current_path)

        if (current_path / ".hg").is_dir():
            return current_path, ".hg directory"

        if (current_path / "pyproject.toml").is_file():
            return current_path, "pyproject.toml"

        current_path = current_path.parent

    return None


ALWAYS_IGNORE = """
.git
__pycache__
.direnv
.eggs
.git
.hg
.mypy_cache
.nox
.tox
.venv
venv
.svn
.ipynb_checkpoints
_build
buck-out
build
dist
__pypackages__
"""


@lru_cache(maxsize=128)
def load_gitignore_spec_relevant_to_path(path):
    """Returns the gitignore spec relevant to the given path."""
    path = Path(path)
    if path.is_file():
        path = path.parent
    project_root = Path(find_project_root(path))
    if project_root is None:
        raise ValueError("Could not find project root. Must be in a git repository.")
    curpath = path
    ignore_spec = pathspec.GitIgnoreSpec([])
    while project_root in curpath.parents or curpath == project_root:
        path_ignore_spec = load_gitignore_spec(curpath / ".gitignore")
        ignore_spec.patterns = ignore_spec.patterns + path_ignore_spec.patterns
        curpath = curpath.parent
    return ignore_spec


@lru_cache(maxsize=128)
def load_gitignore_spec(gitignore_path):
    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as f:
            patterns = f.read().split("\n")
        ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    else:
        ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", [])
    return ignore_spec


def get_nonignored_filepaths(directory, extensions=()):
    """Return a list of filepaths in a directory, ignoring files in .gitignore."""
    file_paths = []
    directory = Path(directory)

    for entry in os.scandir(directory):
        ignore_spec = load_gitignore_spec_relevant_to_path(entry.path)
        entry_relative_path = Path(entry.path).relative_to(directory)
        if ignore_spec.match_file(entry_relative_path):
            continue

        if entry.is_file():
            if extensions:
                if any(entry.path.endswith(ext) for ext in extensions):
                    file_paths.append(entry_relative_path)
            else:
                file_paths.append(entry_relative_path)

        elif entry.is_dir():
            subdir_file_paths = get_nonignored_filepaths(
                entry.path, extensions=extensions
            )
            for subpath in subdir_file_paths:
                file_paths.append(entry_relative_path / subpath)

    file_paths.sort(key=lambda p: ("/" in str(p), p))

    return file_paths
