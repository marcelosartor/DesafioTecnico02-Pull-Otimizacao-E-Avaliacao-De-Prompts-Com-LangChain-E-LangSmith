"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt leonanluppi/bug_to_user_story_v1
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    prompt_ref = "leonanluppi/bug_to_user_story_v1"
    print(f"Fazendo pull: {prompt_ref} ...")

    prompt: ChatPromptTemplate = hub.pull(prompt_ref)

    system_text = ""
    user_text = ""

    for msg in prompt.messages:
        role = msg.__class__.__name__.lower()
        template = msg.prompt.template if hasattr(msg, "prompt") else str(msg)

        if "system" in role:
            system_text = template
        elif "human" in role or "user" in role:
            user_text = template

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_text,
            "user_prompt": user_text,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    output_path = "prompts/bug_to_user_story_v1.yml"
    if save_yaml(data, output_path):
        print(f"✓ Prompt salvo em {output_path}")
    else:
        print("❌ Falha ao salvar o prompt")
        sys.exit(1)


def main():
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        pull_prompts_from_langsmith()
        return 0
    except Exception as e:
        print(f"❌ Erro ao fazer pull: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
