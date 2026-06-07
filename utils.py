from enum import Enum


class PromptType(Enum):
    USER = "user"
    SYSTEM = "system"


def prompt_content(name: str, prompt_type: PromptType = PromptType.SYSTEM):

    prompt_content = ""
    with open(f"orchestration/agents/prompts/{prompt_type.value}/{name}.md") as f:
        prompt_content = f.read()

    return prompt_content
