import os.path
from pathlib import Path

from hasty_coder.filewalk import find_project_root, get_nonignored_file_paths
from hasty_coder.langlib.python import get_file_docstring
from hasty_coder.models import SoftwareProjectPlan
from hasty_coder.utils import slugify


def fill_in_project_plan_from_path(path):
    """
    Fill in a project plan with information from the path.

    If the path is a file, the project name is the name of the file without the extension.
    If the path is a directory, the project name is the name of the directory.
    """
    project_root_path = Path(find_project_root(path))
    if project_root_path is None:
        raise ValueError("Could not find project root. Must be in a git repository.")

    project_name = slugify(project_root_path.name).replace("-", " ").title()

    project_files = get_nonignored_file_paths(project_root_path)

    project_plan = SoftwareProjectPlan(
        software_name=project_name,
        project_files={f: "" for f in project_files},
    )
    return project_plan


def get_project_files_and_descriptions(root_path):
    """Return a dictionary of project files and descriptions."""
    file_descriptions = {}
    project_files = get_nonignored_file_paths(root_path)
    for file_path in project_files:
        abs_path = os.path.join(root_path, file_path)
        description = ""
        if abs_path.endswith(".py"):
            description = get_file_docstring(abs_path)
        file_descriptions[file_path] = description or ""
    return file_descriptions
