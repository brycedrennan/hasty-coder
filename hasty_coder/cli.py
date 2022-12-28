import os.path
import sys
from pathlib import Path

import click

from hasty_coder.log_utils import configure_logging
from hasty_coder.main import write_file, write_project
from hasty_coder.tasklib.add_comments import add_comments_to_all_code_in_path
from hasty_coder.tasklib.generate_software_project_plan import generate_project_plan


@click.group()
def cli():
    """
    Quickly write probably wrong code! 💥.

    Shortcuts:

    `hc filename.txt "optional description"  (writes a whole file)

    `hc dirname/` "optional description"     (writes a whole project)

    """


@cli.command("comments")
@click.argument("path", type=click.Path(exists=True))
def add_docstrings(path):
    """Add docstrings to all python files in PATH."""
    path = os.path.abspath(path)
    if click.confirm(
        f"This is gonna edit all the python files in `{path}` Are you sure?"
    ):
        add_comments_to_all_code_in_path(path)


@cli.command("project")
@click.argument("description")
@click.argument("path", type=click.Path(exists=True), default=".")
def make_project(description, path):
    """Create a project with the given description."""
    write_project(Path(path), description, show_work=True)


@cli.command("project-plan")
@click.argument("description", required=False)
def make_project_plan(description):
    """Generate and write a project plan to a markdown file."""
    project_description = generate_project_plan(description)
    filename = f"{project_description.slug}-plan.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(project_description.as_markdown())


@cli.command("lint")
@click.argument("path", type=click.Path(exists=True), default=".")
def lint(path):
    """AI linting of a file or path."""


@cli.command("file")
@click.argument("path", type=click.Path(exists=False), required=True)
@click.argument("description", required=False)
def mkfile(path, description):
    """Write a single file."""
    write_file(Path(path).absolute(), description=description)


@cli.command("test")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.argument("description", required=False)
def test(path):
    """Write tests."""


def route_cmd():
    """Route command line arguments to appropriate subcommand."""
    configure_logging()
    if len(sys.argv) == 2:
        subcommands = set(cli.commands.keys())
        if sys.argv[1] in subcommands:
            cli()
            return

        if sys.argv[1].lower().startswith("yolo"):
            sys.argv[1] = "project"
            sys.argv.append("")
        elif "." in sys.argv[1]:
            sys.argv.insert(1, "file")

    cli()


if __name__ == "__main__":
    configure_logging("DEBUG")
    route_cmd()
