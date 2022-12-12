import logging
import re

from hasty_coder.models import SoftwareProjectPlan
from hasty_coder.utils import LoggedOpenAI

logger = logging.getLogger(__name__)


def generate_file_contents(filepath, project_plan: SoftwareProjectPlan):
    """Generate file contents for a given filepath and SoftwareProjectPlan object."""
    description = project_plan.project_files.get(filepath, "")
    logger.info("Generating %s", filepath)
    handler = match_file_handler(filepath)
    if handler:
        return handler(filepath, description, project_plan)

    end_token = "ENDOFFILE_ZZZ"
    prompt = f"""
{project_plan.as_markdown()}

INSTRUCTIONS
Based on the description above. Write the contents of the {filepath} file. Denote the end of the file with the string "{end_token}"
The {filepath} file is described as "{description}".
{filepath} FILE CONTENTS:
"""
    llm = LoggedOpenAI(temperature=0.01)
    file_contents = None
    for i in range(3):
        file_contents = llm(prompt, stop=[end_token])
        if file_contents:
            break

    return file_contents


def gen_readme(filepath, description, project_plan: SoftwareProjectPlan):
    """Generate a README.md file from a SoftwareProjectPlan object."""
    readme_md = project_plan.as_markdown(excluded_sections=["project_files"])
    bio = gen_hasty_bio()
    readme_md += f"""
    
## About the Author

{bio}
"""
    return readme_md


def gen_hasty_bio():
    """Generate a humorous bio for an AI named Hasty."""
    prompt = """
Write a humorous bio for an AI named Hasty that writes a lot of code but doesn't do a good job.  Allude to the many disasters Hasty has caused. Hasty is a big fan of the phrase "move fast and break things". But he does meet deadlines! Write it in first-person tense. 
"""
    bio = LoggedOpenAI(temperature=0.9)(prompt)
    bio += "\n\n - [HastyCoder](https://github.com/brycedrennan/hasty-coder) 🤖📝💻🚀💥"
    return bio


def match_file_handler(filepath):
    """Return the handler associated with the given filepath, or None if no match is found."""
    filename = filepath.split("/")[-1]
    for pattern, handler in FILENAME_PATTERN_HOOKS.items():
        if re.match(pattern, filename, flags=re.IGNORECASE):
            return handler
    return None


FILENAME_PATTERN_HOOKS = {
    r"readme\.md": gen_readme,
}
