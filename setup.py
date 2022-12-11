from setuptools import setup

setup(
    name="hasty-coder",
    version="0.0.1",
    description="A command line tool that uses AI to write entire software projects from scratch. HastyCoder is your AI careless coding companion. ",
    author="Bryce Drennan",
    packages=["hasty_coder"],
    entry_points={
        "console_scripts": [
            "hasty-code = hasty_coder.cli:route_cmd",
            "hc = hasty_coder.cli:route_cmd",
        ]
    },
    install_requires=["black", "click", "isort", "langchain", "openai", "orjson"],
)
