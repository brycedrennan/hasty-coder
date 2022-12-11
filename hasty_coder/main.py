from hasty_coder.tasklib.generate_software_project_description import (
    flesh_out_project_description,
    generate_project_description,
)
from hasty_coder.tasklib.implement_software_project import implement_project_plan


def write_code(parent_folder, description="", show_work=True):
    description = description.strip()
    if not description:
        description = generate_project_description()

    program_description = flesh_out_project_description(description)
    if show_work:
        print(program_description.as_markdown())
    project_path = implement_project_plan(program_description, parent_folder)
    print(f"Project '{program_description.software_name}' created at {project_path}")


# if __name__ == "__main__":
#     import os.path
#     from hasty_coder.log_utils import configure_logging
#
#     configure_logging("DEBUG")
#     # write_code(Path("."), show_work=True)
#     program_description = flesh_out_project_description(generate_project_description())
#     dest_path = os.path.dirname(os.path.dirname(__file__)) + "/demo_projects/README.md"
#     with open(dest_path, "w") as f:
#         f.write(program_description.as_markdown())
