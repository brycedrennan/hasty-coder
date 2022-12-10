from pathlib import Path

import click

from hasty_coder.main import write_code


@click.command()
@click.argument("description")
def hasty_code(description):
    click.echo(f"Description: {description}")
    write_code(description, Path("."), show_work=True)


if __name__ == "__main__":
    hasty_code()
