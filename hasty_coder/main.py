from hasty_coder.tasklib.generate_software_project_description import (
    flesh_out_project_description,
)
from hasty_coder.tasklib.implement_software_project import implement_project_plan


def write_code(description, parent_folder, show_work=True):
    program_description = flesh_out_project_description(description)
    if show_work:
        print(program_description.as_markdown())
    project_path = implement_project_plan(program_description, parent_folder)
    print(f"Project '{program_description.software_name}' created at {project_path}")
