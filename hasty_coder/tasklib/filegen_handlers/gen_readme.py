from hasty_coder.models import SoftwareProjectPlan
from hasty_coder.utils import LoggedOpenAI


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
