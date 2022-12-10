import logging

from hasty_coder.models import SoftwareProjectDescription
from hasty_coder.utils import LoggedOpenAI, phraseify


def flesh_out_project_description(short_description):
    project_plan = SoftwareProjectDescription(short_description=short_description)
    project_plan.software_name = generate_project_name(short_description)
    project_plan.primary_programming_language = determine_programming_language(
        short_description
    )
    project_plan.components = generate_programming_components(project_plan)
    project_plan.requirements = generate_project_requirements(project_plan)
    project_plan.project_files = generate_project_file_structure(project_plan)
    return project_plan


def generate_project_description():
    prompt = "Write a single sentence description of python software you want to write:"
    return LoggedOpenAI(temperature=1)(prompt).strip()


def generate_project_name(short_description):
    prompt = f"""
## SOFTWARE DESCRIPTION
{short_description}

Based on the description above. What would be a good short name for this project? Ideally it would be witty, clever,
and memorable.
## SOFTWARE PROJECT NAME
"""
    software_name = LoggedOpenAI(temperature=0.9)(prompt)
    software_name = phraseify(software_name.strip())
    return software_name


def determine_programming_language(short_description):
    llm = LoggedOpenAI(temperature=0.01)
    prompt = f"""
SOFTWARE DESCRIPTION: {short_description}

Based on the description above, what programming language should this software be written in? Choose a single language.
PROGRAMMING LANGUAGE:
"""
    programming_language = llm(prompt)
    return programming_language.strip()


def generate_programming_components(project_plan):
    llm = LoggedOpenAI(temperature=0.02)
    prompt = f"""
{project_plan.as_markdown()}

Based on the description above, lets break down the software into components. Write a list of components and 
a short description of their purpose. Write your answer as a json dictionary of where the key is the component name
and the value is the description.

SOFTWARE COMPONENTS:
    """
    components = llm(prompt, as_json=True)
    return components


def generate_project_requirements(project_plan):
    llm = LoggedOpenAI(temperature=0.02)
    prompt = f"""
{project_plan.as_markdown()}

Based on the description above, let's write a list of requirements for the completion of the software. 
Write your answer as a json list of strings.

REQUIREMENTS:
    """
    return llm(prompt, as_json=True)


def generate_project_file_structure(project_plan):
    llm = LoggedOpenAI(temperature=0.02)
    prompt = f"""
{project_plan.as_markdown()}

INSTRUCTIONS:
Based on the description above, let's layout the project file structure. No code should be in the root of the project
folder. Show all the files in each folder. The base project folder should have a README.md file, a Makefile, a Dockerfile, and a .gitignore file.
Make sure the project specifies it's library dependencies. There should be a thorough test suite that mimics the structure of the code.
Write project files as a json list of strings.
    
PROJECT FILES (json list of strings):
"""
    files = llm(prompt, as_json=True)
    file_text = "\n".join(f" - {file}" for file in files)
    prompt = f"""
{project_plan.as_markdown()}

PROJECT FILES:
{file_text}


[Based on the project plan above, let's create short descriptions of the contents of each file. The descriptions should start with a verb in the "present simple" tense.
Write the descriptions as a json dictionary where the key is the filepath and the value is the description.]

FILE DESCRIPTIONS (json dictionary):
"""
    file_descriptions = llm(prompt, as_json=True)
    structure = {path: file_descriptions.get(path, "") for path in files}
    return structure


# terminal_mode = """I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd."""

if __name__ == "__main__":
    # print(determine_programming_language("test", "test"))
    logging.basicConfig(level=logging.INFO)

    # program_description = flesh_out_project_description(
    #     "flask-joker",
    #     "flask app that tells jokes using the openai client library (from pypi.org). doesn't use a database"
    # )
    # short_description = "a flask app that creates poetry based on a prompt from the user. it uses the openai client library from pypi.org"
    _short_description = generate_project_description()
    print(f"Description: {_short_description}")
    program_description = flesh_out_project_description(_short_description)
    print("")
    print(program_description)
    print("")
    print(program_description.as_markdown())
