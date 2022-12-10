from hasty_coder.tasklib.create_code_project_plan import flesh_out_project_plan
from hasty_coder.tasklib.implement_code_project_plan import implement_project_plan


def write_code(description, parent_folder, show_work=True):
    program_description = flesh_out_project_plan(description)
    if show_work:
        print(program_description.render())
    project_path = implement_project_plan(program_description, parent_folder)
    print(f"Project '{program_description.software_name}' created at {project_path}")
