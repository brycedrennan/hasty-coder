import os.path
import pathlib
from datetime import datetime

from hasty_coder.models import SoftwareProjectDescription
from hasty_coder.tasklib.filegen import generate_file_contents
from hasty_coder.utils import parallel_run, slugify


def implement_project_plan(project_plan: SoftwareProjectDescription, projects_path):
    project_folder_name = slugify(project_plan.software_name)
    project_path = create_project_skeleton(
        project_path=os.path.join(projects_path, project_folder_name),
        filepaths=project_plan.project_files.keys(),
    )
    files_only_filepaths = [
        filepath
        for filepath in project_plan.project_files.keys()
        if not filepath.endswith("/")
    ]

    def gen_and_save(filepath):
        file_contents = generate_file_contents(filepath, project_plan)
        if file_contents:
            with open(os.path.join(project_path, filepath), "w", encoding="utf-8") as f:
                f.write(file_contents)

    parallel_run(gen_and_save, files_only_filepaths)

    return project_path


def create_project_skeleton(project_path, filepaths):
    # make sure all the paths will be created under the base path
    base_path = os.path.abspath(project_path)
    # if base_path already exists append a timestamp to the path
    if os.path.exists(base_path):
        base_path = f"{base_path}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    filepaths = [os.path.join(base_path, filepath) for filepath in filepaths]
    abs_filepaths = [os.path.abspath(filepath) for filepath in filepaths]
    for filepath in abs_filepaths:
        if os.path.commonpath([base_path, filepath]) != base_path:
            raise ValueError(f"Filepath {filepath} is not under base path {base_path}")

    for filepath in filepaths:
        full_path = pathlib.Path(os.path.join(base_path, filepath))
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if not filepath.endswith("/"):
            full_path.touch()
    return base_path
