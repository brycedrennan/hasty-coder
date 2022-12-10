import os.path
import pathlib
import re
from datetime import datetime

from hasty_coder.tasklib.create_code_project_plan import SoftwareProjectPlan
from hasty_coder.utils import LoggedOpenAI, slugify, parallel_run


def implement_project_plan(project_plan: SoftwareProjectPlan, projects_path):
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
            with open(os.path.join(project_path, filepath), "w") as f:
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


def generate_file_contents(filepath, project_plan: SoftwareProjectPlan):
    llm = LoggedOpenAI(temperature=0.01)
    description = project_plan.project_files.get(filepath, "")
    end_token = "ENDOFFILE_ZZZ"
    prompt = f"""
{project_plan.render()}

INSTRUCTIONS
Based on the description above. Write the contents of the {filepath} file. Denote the end of the file with the string "{end_token}"
The {filepath} file is described as "{description}".
{filepath} FILE CONTENTS:
"""
    for i in range(3):
        file_contents = llm(prompt, stop=[end_token])
        if file_contents:
            break

    # strip all types of whitespace from ends
    file_contents = re.sub(r"^\s+|\s+$", "", file_contents)

    return file_contents


if __name__ == "__main__":
    plan = SoftwareProjectPlan(
        short_description="a flask app that creates poetry based on a prompt from the user. it uses the openai client library from pypi.org",
        software_name="Python\n\nPoetify.",
        programming_language="Python",
        start_cmd="",
        components={
            "Flask App": "A web application framework written in Python that will be used to create the Poetify application.",
            "OpenAI Client Library": "A library from pypi.org that will be used to generate the poetry based on the user's prompt.",
            "User Interface": "The user interface will be used to allow the user to input their prompt and view the generated poetry.",
            "Database": "A database will be used to store the user's prompt and the generated poetry.",
        },
        requirements=[
            "Create a Flask App",
            "Integrate OpenAI Client Library",
            "Design a User Interface",
            "Implement a Database",
        ],
        project_files={
            "README.md": "Describes the project and its components.",
            "Makefile": "Builds the project.",
            "Dockerfile": "Contains instructions for building a Docker image.",
            ".gitignore": "Ignores files that should not be tracked by git.",
            "requirements.txt": "Lists the project's dependencies.",
            "poetify/": "",
            "poetify/__init__.py": "Initializes the Flask app.",
            "poetify/app.py": "Defines the Flask app.",
            "poetify/config.py": "Configures the Flask app.",
            "poetify/models.py": "Defines the database models.",
            "poetify/views.py": "Defines the views for the Flask app.",
            "poetify/templates/": "",
            "poetify/templates/index.html": "Defines the HTML template for the user interface.",
            "poetify/static/": "",
            "poetify/static/css/": "Contains the CSS files for the user interface.",
            "poetify/static/js/": "Contains the JavaScript files for the user interface.",
            "poetify/tests/": "",
            "poetify/tests/test_app.py": "Tests the Flask app.",
            "poetify/tests/test_config.py": "Tests the Flask app configuration.",
            "poetify/tests/test_models.py": "Tests the database models.",
            "poetify/tests/test_views.py": "Tests the views for the Flask app.",
        },
    )
    implement_project_plan(plan, "/Users/bryce/projects/hasty-coder/demo_projects")
