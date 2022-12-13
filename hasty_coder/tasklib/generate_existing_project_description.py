import logging
from hasty_coder.utils import LoggedOpenAI
from hasty_coder.models import SoftwareProjectDescription, SoftwareStack
import os

logger = logging.getLogger(__name__)

def generate_existing_project_description(description, repo_path, file):
    project_description = SoftwareProjectDescription()
    project_description.software_name = os.path.dirname(repo_path)
    project_description.project_files = generate_project_file_structure(repo_path)
    project_description.short_description = generate_project_short_description(project_description.project_files)
    project_description.long_description = generate_project_long_description(project_description.project_files)

def generate_project_file_structure(project_path):

    file_structure = {}
    unorganzied_primary_programming_languages = []
    unorganzied_secondary_programming_languages = []
    for root, dirs, filenames in os.walk(project_path):
        if root.startswith("./."):
            continue
        for filename in filenames:
            if filename.startswith("."):
                continue
            filepath = os.path.join(root, filename)
            print(filepath)
            with open(filepath) as f:
                file_contents = f.read()

            file_structure = file_structure | generate_file_description(filepath, file_contents)

def generate_project_short_description(project_files):
    llm = LoggedOpenAI(temperature=0.02)

    prompt = f"""
    PROJECT CONTENT: 
    {project_files}


    [Based on the the descriptions given in this json, where the key is the file path and the value is the description of the file's content,
     let's create a short description of the whole project. The description should start with a verb in the "present simple" tense.
    Write the description as paragraph that starts and ends with 3 double quotation marks.]
            """
    project_description = llm(prompt, as_json=True)

def generate_project_long_description(project_files):
    llm = LoggedOpenAI(temperature=0.02)

    prompt = f"""
    PROJECT CONTENT: 
    {project_files}


    [Based on the the descriptions given in this json, where the key is the file path and the value is the description of the file's content,
     let's create a long description of the whole project. The description should start with a verb in the "present simple" tense.
    Write the description in several paragraphs that starts and ends with 3 double quotation marks.]
            """
    project_description = llm(prompt, as_json=True)

def generate_file_description(file_path, file_content):
    llm = LoggedOpenAI(temperature=0.02)

    prompt = f"""
FILE PATH: 
{file_path}

FILES CONTENT:
{file_content}



[Based on the file content and file path above, let's create a short description of the content of the file. The description should start with a verb in the "present simple" tense.
Write the description as a json dictionary where the key is the filepath and the value is the description.]

FILE DESCRIPTION (json dictionary):
        """
    file_description = llm(prompt, as_json=True)
    structure = {file_path: file_description.get(file_path, "")}
    logger.info("File Structure: %s", structure)
    return structure