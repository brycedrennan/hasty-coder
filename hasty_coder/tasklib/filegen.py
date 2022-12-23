import logging
import re

from hasty_coder.langlib import python
from hasty_coder.models import SoftwareProjectPlan
from hasty_coder.tasklib.filegen_handlers.gen_gitignore import gen_gitignore
from hasty_coder.tasklib.filegen_handlers.gen_readme import gen_readme
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

    if filepath.endswith(".py"):
        file_contents = python.format_code(file_contents)

    return file_contents


def match_file_handler(filepath):
    """Return the handler associated with the given filepath, or None if no match is found."""
    filename = filepath.split("/")[-1]
    for pattern, handler in FILENAME_PATTERN_HOOKS.items():
        if re.match(pattern, filename, flags=re.IGNORECASE):
            return handler
    return None


FILENAME_PATTERN_HOOKS = {
    r"readme\.md": gen_readme,
    r"\.gitignore": gen_gitignore,
}
