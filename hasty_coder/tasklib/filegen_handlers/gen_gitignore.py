import json
import logging
from functools import lru_cache

from hasty_coder.filecache import get_cached_url_contents
from hasty_coder.models import SoftwareProjectPlan

logger = logging.getLogger(__name__)


def gen_gitignore(filepath, description, project_plan: SoftwareProjectPlan):
    """Generate a .gitignore file from a SoftwareProjectPlan object."""
    return gen_gitignore_for_language(
        project_plan.software_stack.primary_programming_language
    )


def gen_gitignore_for_language(programming_language):
    available_gitignore_templates = get_available_gitignore_templates()
    programming_language = programming_language.lower().strip().replace(" ", "")
    language_template_name = available_gitignore_templates.get(
        programming_language, None
    )
    contents = build_default_gitignore()
    if language_template_name:
        contents += retreive_gitignore_template(language_template_name)
    else:
        logger.warning("No gitignore template found for %s", programming_language)
    return contents


def get_available_gitignore_templates():
    """Get a list of available gitignore templates from the GitHub API."""
    url = "https://api.github.com/repos/github/gitignore/git/trees/main"
    contents = get_cached_url_contents(url)
    data = json.loads(contents.decode("utf-8"))
    paths = [t["path"] for t in data["tree"] if t["path"].endswith(".gitignore")]
    # strip .gitignore ending
    language_names = [p[:-10] for p in paths]

    return {lang.lower(): lang for lang in language_names}


@lru_cache(maxsize=1)
def build_default_gitignore():
    templates = [
        # Common OS's
        "Global/Windows",
        "Global/macOS",
        "Global/Linux",
        # Common Editors
        "Global/Emacs",
        "Global/JetBrains",
        "Global/VisualStudioCode",
    ]

    template_contents = []
    for t in templates:
        template_contents.append(f"## {t}")
        template_contents.append(retreive_gitignore_template(t))
    template_contents.extend([".idea"])

    return "\n".join(template_contents)


def retreive_gitignore_template(template_name):
    """Retreive a gitignore template from the GitHub API."""
    url = f"https://raw.githubusercontent.com/github/gitignore/main/{template_name}.gitignore"
    contents = get_cached_url_contents(url)
    return contents.decode("utf-8")


if __name__ == "__main__":
    print(gen_gitignore_for_language("python"))
    # print(build_default_gitignore())
