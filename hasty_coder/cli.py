import sys
from pathlib import Path

import click

from hasty_coder.log_utils import configure_logging
from hasty_coder.main import write_code
from hasty_coder.tasklib.generate_software_project_plan import generate_project_plan


@click.group()
def cli():
    pass


@cli.command("project")
@click.argument("description")
def make_project(description):
    write_code(Path("."), description, show_work=True)


@cli.command("project-plan")
@click.argument("description", required=False)
def make_project_plan(description):
    project_description = generate_project_plan(description)
    filename = f"{project_description.slug}-plan.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(project_description.as_markdown())
    print(f"\n\nProject plan written to {filename}")


def route_cmd():
    configure_logging()
    if len(sys.argv) == 2:
        subcommands = set(cli.commands.keys())
        if sys.argv[1] in subcommands:
            cli()
            return

        if sys.argv[1].lower().startswith("yolo"):
            print("YOLO! 😎🤘🏼👊")
            sys.argv[1] = "project"
            sys.argv.append("")
        else:
            sys.argv.insert(1, "project")
    cli()


if __name__ == "__main__":
    configure_logging("DEBUG")
    route_cmd()
