from hasty_coder.tasklib.describe_project import fill_in_project_plan_from_path
from hasty_coder.tasklib.filegen import generate_file_contents
from hasty_coder.tasklib.generate_software_project_plan import generate_project_plan
from hasty_coder.tasklib.implement_software_project import implement_project_plan


def write_project(parent_folder, description="", show_work=True):
    """Generate and implement a project plan for a software project in a given parent folder."""
    description = description.strip()

    program_description = generate_project_plan(description)
    if show_work:
        print(program_description.as_markdown())
    project_path = implement_project_plan(program_description, parent_folder)
    print(f"Project '{program_description.software_name}' created at {project_path}")


def make_project_plan(description=None):
    """Generate and print a project plan as markdown."""
    project_description = generate_project_plan(description)
    print(project_description.as_markdown())


def write_file(path, description=""):
    """Write a single file."""
    project_plan = fill_in_project_plan_from_path(path)
    project_plan.project_files[path] = description or ""
    contents = generate_file_contents(path, project_plan)
    print(contents)


def add_comments(path):
    """Add comments to all python files in PATH."""


def lint(path):
    """AI linting of a file or path"""


def write_tests(path, function_name=None):
    """Write tests for a file or path"""


# if __name__ == "__main__":
#     import os.path
#     from hasty_coder.log_utils import configure_logging
#
#     configure_logging("DEBUG")
#     # write_project(Path("."), show_work=True)
#     program_description = generate_project_plan(generate_project_description_short())
#     dest_path = os.path.dirname(os.path.dirname(__file__)) + "/demo_projects/README.md"
#     with open(dest_path, "w") as f:
#         f.write(program_description.as_markdown())
