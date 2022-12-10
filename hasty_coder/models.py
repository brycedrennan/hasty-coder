from dataclasses import asdict, dataclass
from typing import List


@dataclass
class SoftwareStack:
    primary_programming_language: str
    secondary_programming_languages: List[str]
    primary_framework: str
    secondary_frameworks: List[str]


@dataclass
class SoftwareProjectDescription:
    short_description: str
    software_name: str = None
    software_stack: SoftwareStack = None
    primary_programming_language: str = None
    secondary_programming_languages: str = None
    start_cmd: str = None
    components: dict = None
    requirements: List[str] = None
    project_files: dict = None

    def as_markdown(self):
        section_texts = []
        if self.software_name:
            section_texts.append(f"# {self.software_name}")

        for key, value in asdict(self).items():
            if key == "software_name":
                continue
            if value:
                formatted_key = key.upper().replace("_", " ")
                section_text = f"## {formatted_key}\n{value}"
                if isinstance(value, dict):
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
        return doctext
