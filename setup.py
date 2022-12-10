from setuptools import setup

setup(
    name="hasty-coder",
    version="0.0.1",
    description="A command line tool that uses AI to write entire software projects from scratch (but the code is usually buggy and doesn't work)",
    author="Bryce Drennan",
    packages=["hasty_coder"],
    entry_points={
        "console_scripts": [
            "hasty-code = hasty_coder.cli:hasty_code",
            "hc = hasty_coder.cli:hasty_code",
        ]
    },
    install_requires=[
        "click",
        "openai",
        "black",
        "isort",
    ],
)
