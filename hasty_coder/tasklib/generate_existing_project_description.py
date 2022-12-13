import logging
from hasty_coder.utils import LoggedOpenAI
import os

logger = logging.getLogger(__name__)


def generate_file_description(file_path, file_content):
    llm = LoggedOpenAI(temperature=0.02)

    prompt = f"""
FILE PATH: 
{file_path}
    
FILES CONTENT:
{file_content}



[Based on the file content and file path above, let's create short descriptions of the content of the file. The descriptions should start with a verb in the "present simple" tense.
Write the descriptions as a json dictionary where the key is the filepath and the value is the description.]

FILE DESCRIPTION (json dictionary):
        """
    file_description = llm(prompt, as_json=True)
    structure = {file_path: file_description.get(file_path, "") }
    logger.info("File Structure: %s", structure)
    return structure


def generate_project_file_structure(project_path):
    llm = LoggedOpenAI(temperature=0.02)

    file_structure = {}
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
