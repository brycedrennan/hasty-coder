import logging
from dataclasses import is_dataclass

from hasty_coder.models import SoftwareProjectDescription
from hasty_coder.tasklib.fragments import REQUIRED_PROJECT_FILES
from hasty_coder.utils import LoggedOpenAI, phraseify

logger = logging.getLogger(__name__)


def flesh_out_project_description(short_description):
    short_description = rewrite_project_description(short_description)
    project_plan = SoftwareProjectDescription(short_description=short_description)
    generation_plan = {
        "long_description": generate_project_description_long,
        "software_name": generate_project_name,
        "tagline": generate_project_tagline,
        "emoji_tagline": generate_project_emoji_tagline,
        "software_stack": generate_software_stack,
        "installation_instructions": generate_installation_instructions,
        "quick_start": generate_quick_start,
        "features": generate_software_feature_list,
        "todo": generate_project_todo,
        "project_files": generate_project_file_structure,
    }
    for attr, generator in generation_plan.items():
        attr_value = getattr(project_plan, attr, None)
        if attr_value is None or is_dataclass(attr_value):
            setattr(project_plan, attr, generator(project_plan))

    return project_plan


def generate_software_stack(project_plan):
    prompt = f"""
SOFTWARE PROJECT DESCRIPTION:
```
{project_plan.as_markdown()}
```
INSTRUCTIONS:
Based on the software project description above, determine what an appropriate tech stack would be. 
Use the format provided in the JSON template below. Replace the parts contained in angle brackets with the appropriate values.

JSON TEMPLATE:
```
{{
    "project_type": "<PROJECT_TYPE>",  # one of "webapp", "cli", "library", "mobile app", "desktop app"
    "programming_language": <STR>,  # for webapps, cli, and libraries prefer python unless the project description says otherwise
    "framework": <STR>,
    "database": <null or STR>,
    "testing_framework": <STR>
}}
```
TECH STACK:
```
"""
    stack = LoggedOpenAI(temperature=0.02)(prompt, as_json=True, stop=["```"])
    logger.info("Tech Stack: %s", stack)
    return stack


def _meta_generate(
    data_name, project_plan, instructions, as_json=False, temperature=0.01
):
    data_name_display = data_name.replace("_", " ").title()
    json_extra = " (in json format)" if as_json else ""
    prompt = f"""
{project_plan.as_markdown()}

INSTRUCTIONS:
Based on the description above, {instructions}

{data_name_display.upper()}{json_extra}:
"""
    answer = LoggedOpenAI(temperature=temperature)(prompt, as_json=as_json)
    # strip quotes from the ends of the answer
    if isinstance(answer, str):
        answer = answer.strip('"')

    logger.info(f"{data_name_display}: {answer}")
    return answer


def generate_project_description():
    prompt = "Write a very brief and concise idea for a small python project in a single, short sentence. Write as if it's a description of existing software. Do not use the project name in the description. Make it something funny:"
    description = LoggedOpenAI(temperature=0.8)(prompt).strip()
    logger.info("Yolo Idea: %s", description)
    return description


def generate_project_description_long(project_plan):
    description = _meta_generate(
        data_name="long_description",
        project_plan=project_plan,
        instructions="Write a concise and witty paragraph expanding on the short description. Make it funny.",
        temperature=0.05,
    )

    return description


def rewrite_project_description(description):
    prompt = f"""
Re-write the following description for a software project into a more clear and concise thought.

DESCRIPTION:
{description}

RE-WRITTEN DESCRIPTION:
"""
    rewritten = LoggedOpenAI(temperature=0)(prompt)
    logger.info("Rewritten Description: %s", rewritten)
    return rewritten


def generate_project_name(project_plan):
    software_name = _meta_generate(
        data_name="software_project_name",
        project_plan=project_plan,
        instructions=(
            "Write a short and witty name for this project. It should be a complex noun phrase that communicates what type of data it deals with. "
            "\nGood Example: 'Hasty Coder' \nBad Example: 'Code Generator'"
            "\nGood Example: 'Acti-Planner' \nBad Example: 'Dynamic Automation Orchestration'"
        ),
        temperature=0.9,
    )
    return phraseify(software_name)


def generate_project_tagline(project_plan):
    return _meta_generate(
        data_name="tagline",
        project_plan=project_plan,
        instructions=(
            "Write a clever and witty tagline for the project. "
            "Do not use the name of the project in the tagline. Do not use punctuation."
        ),
        temperature=0.9,
    )


def generate_project_emoji_tagline(project_plan):
    emoji_tagline = _meta_generate(
        data_name="emoji_tagline",
        project_plan=project_plan,
        instructions=(
            f"Represent the tagline, '{project_plan.tagline}' using only emoji. Ideally no more than 3 emoji"
        ),
        temperature=0.9,
    )
    emoji_tagline = emoji_tagline.replace(" ", "")
    return emoji_tagline


def generate_installation_instructions(project_plan):
    instructions = _meta_generate(
        data_name="installation_instructions",
        project_plan=project_plan,
        instructions=(
            "Write installation instructions as a single terminal command. Write with markdown formatting."
        ),
        temperature=0.05,
    )

    return instructions


def generate_quick_start(project_plan):
    instructions = _meta_generate(
        data_name="usage_instructions",
        project_plan=project_plan,
        instructions=(
            "Write instructions to start the program as a single terminal command. Assume the program is already installed.  Write with markdown formatting."
        ),
        temperature=0.05,
    )

    return instructions


def determine_programming_language(project_plan):
    return _meta_generate(
        data_name="programming_language",
        project_plan=project_plan,
        instructions=(
            "what programming language should this software be written in? Choose a single language."
        ),
        temperature=0,
    )


def generate_software_feature_list(project_plan):
    feature_list = _meta_generate(
        "components",
        project_plan=project_plan,
        instructions=(
            "write a concise list of the customer-oriented key features of this software project. Each feature should be in the format:"
            "\n<FEATURE_NAME>: <FEATURE_DESCRIPTION>"
            "\nWrite your answer as a json list of strings."
        ),
        as_json=True,
        temperature=0.02,
    )
    return feature_list


def generate_project_todo(project_plan):
    llm = LoggedOpenAI(temperature=0.02)
    prompt = f"""
{project_plan.as_markdown()}
INSTRUCTIONS:
Based on the description above, let's break-down the work needed to create the software. Create a list of smaller tasks
that will help us complete the software. Write the list as a json list of strings.

TODO LIST:
```
    """
    requirements = llm(prompt, as_json=True, stop=["```"])
    logger.info("Requirements: %s", requirements)
    return requirements


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
    files = sorted(list(set(files + REQUIRED_PROJECT_FILES)))

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
    logger.info("File Structure: %s", structure)
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
