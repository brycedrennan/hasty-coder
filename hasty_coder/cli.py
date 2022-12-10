import sys
from pathlib import Path

import click

from hasty_coder.log_utils import configure_logging
from hasty_coder.main import write_code
from hasty_coder.tasklib.generate_software_project_description import (
    flesh_out_project_description,
)


@click.group()
def cli():
    pass


@cli.command("repo")
@click.argument("description")
def make_repo(description):
    click.echo(f"Description: {description}")
    write_code(description, Path("."), show_work=True)


@cli.command("repo-plan")
@click.argument("description")
def make_repo_plan(description):
    click.echo(f"Description: {description}")
    project_description = flesh_out_project_description(description)
    print(project_description.as_markdown())


def route_cmd():
    configure_logging()
    if len(sys.argv) == 2:
        sys.argv.insert(1, "repo")
    cli()


if __name__ == "__main__":
    configure_logging()
    route_cmd()
