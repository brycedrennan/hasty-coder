from dataclasses import dataclass, fields
from typing import List


@dataclass
class SoftwareStack:
    primary_programming_language: str = None
    secondary_programming_languages: List[str] = None
    primary_framework: str = None
    secondary_frameworks: List[str] = None
    testing_tooling: List[str] = None

    def as_markdown(self):
        md = f"""
- Programming Languages: **{self.primary_programming_language}**. {", ".join(self.secondary_programming_languages)}
- Frameworks: **{self.primary_framework}**. {", ".join(self.secondary_frameworks)}
- Testing Tooling: {", ".join(self.testing_tooling)}
        """
        return md.strip()


@dataclass
class SoftwareProjectDescription:
    software_name: str = None
    short_description: str = None
    long_description: str = None
    tagline: str = None
    emoji_tagline: str = None
    installation_instructions: str = None
    quick_start: str = None
    features: dict = None
    todo: List[str] = None
    software_stack: SoftwareStack = None
    project_files: dict = None

    def as_markdown(self, excluded_sections=None):

        header = ""
        if self.software_name:
            header += f"# {self.software_name}"
        if self.emoji_tagline:
            header += f" {self.emoji_tagline}"
        if header:
            header += "\n\n"
        if self.tagline:
            header += f"**{self.tagline}**\n\n"
        if self.short_description:
            header += f"{self.short_description}\n\n"
        if self.long_description:
            header += f"{self.long_description}\n\n"

        section_texts = []
        skip_keys = [
            "software_name",
            "short_description",
            "long_description",
            "tagline",
            "emoji_tagline",
        ]
        if excluded_sections:
            skip_keys.extend(excluded_sections)

        for field in fields(self):
            key = field.name
            value = getattr(self, key)
            if key in skip_keys:
                continue
            if value:
                formatted_key = key.replace("_", " ").title()
                section_text = f"## {formatted_key}\n{value}"
                if hasattr(value, "as_markdown"):
                    section_text = f"## {formatted_key}\n{value.as_markdown()}"
                elif isinstance(value, dict):
                    subsection_texts = []
                    for subkey, subvalue in value.items():
                        subsection_text = f" - {subkey} - {subvalue}"
                        subsection_texts.append(subsection_text)
                    subsection_text = "\n".join(subsection_texts)
                    section_text = f"## {formatted_key}\n{subsection_text}"
                elif isinstance(value, list):
                    subsection_texts = []
                    for item in value:
                        subsection_text = f" - {item}"
                        subsection_texts.append(subsection_text)
                    subsection_text = "\n".join(subsection_texts)
                    section_text = f"## {formatted_key}\n{subsection_text}"
                section_texts.append(section_text)

        doctext = "\n\n".join(section_texts)
        return header + doctext
