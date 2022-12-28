from hasty_coder.tasklib.describe_project import fill_in_project_plan_from_path
from hasty_coder.tasklib.filegen import generate_file_contents
from hasty_coder.tasklib.generate_software_project_plan import generate_project_plan
from hasty_coder.tasklib.implement_software_project import implement_project_plan


def write_project(parent_folder, description="", *, show_work=True):
    """Generate and implement a project plan for a software project in a given parent folder."""
    description = description.strip()

    program_description = generate_project_plan(description)
    if show_work:
        pass
    project_path = implement_project_plan(program_description, parent_folder)


def make_project_plan(description=None):
    """Generate and print a project plan as markdown."""
    project_description = generate_project_plan(description)


def write_file(path, description=""):
    """Write a single file."""
    project_plan = fill_in_project_plan_from_path(path)
    project_plan.project_files[path] = description or ""
    contents = generate_file_contents(path, project_plan)


def add_comments(path):
    """Add comments to all python files in PATH."""


def lint(path):
    """AI linting of a file or path."""


def write_tests(path, function_name=None):
    """Write tests for a file or path."""
