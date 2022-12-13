import sys
from pathlib import Path

import click

from hasty_coder.log_utils import configure_logging
from hasty_coder.main import write_code, add_to_repo
from hasty_coder.tasklib.generate_software_project_description import (
    flesh_out_project_description,
)


@click.group()
def cli():
    pass


@cli.command("repo")
@click.argument("description")
def make_repo(description):
    write_code(Path("."), description, show_work=True)


@cli.command("repo-plan")
@click.argument("description")
def make_repo_plan(description):
    project_description = flesh_out_project_description(description)
    print(project_description.as_markdown())


@cli.command("existing-repo")
@click.argument("description")
@click.argument("repo_path")
@click.argument("file")
def make_repo(description, repo_path, file):
    add_to_repo(description, repo_path, file, show_work=True)
    # write_code(Path("."), description, show_work=True)

def route_cmd():
    configure_logging()
    if len(sys.argv) == 2:
        if sys.argv[1].lower().startswith("yolo"):
            print("YOLO! 😎🤘🏼👊")
            sys.argv[1] = "repo"
            sys.argv.append("")
        else:
            sys.argv.insert(1, "repo")
    cli()


if __name__ == "__main__":
    configure_logging("INFO")
    route_cmd()
