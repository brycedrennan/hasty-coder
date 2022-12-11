from hasty_coder.tasklib.generate_software_project_plan import generate_project_plan
from hasty_coder.tasklib.implement_software_project import implement_project_plan


def write_code(parent_folder, description="", show_work=True):
    description = description.strip()

    program_description = generate_project_plan(description)
    if show_work:
        print(program_description.as_markdown())
    project_path = implement_project_plan(program_description, parent_folder)
    print(f"Project '{program_description.software_name}' created at {project_path}")


def make_repo_plan(description=None):
    project_description = generate_project_plan(description)
    print(project_description.as_markdown())


# if __name__ == "__main__":
#     import os.path
#     from hasty_coder.log_utils import configure_logging
#
#     configure_logging("DEBUG")
#     # write_code(Path("."), show_work=True)
#     program_description = generate_project_plan(generate_project_description_short())
#     dest_path = os.path.dirname(os.path.dirname(__file__)) + "/demo_projects/README.md"
#     with open(dest_path, "w") as f:
#         f.write(program_description.as_markdown())
