"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    return validate_prompt_structure(prompt_data)


def push_prompt_to_langsmith(prompt_id: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).
    Usa client.push_prompt() — não precisa de username, a API key identifica a conta.

    Args:
        prompt_id: Identificador do prompt (ex: "bug_to_user_story_v2")
        prompt_data: Dados do prompt (inner dict do YAML)

    Returns:
        True se sucesso, False caso contrário
    """
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return False

    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    chat_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    description = prompt_data.get("description", "")

    print(f"Fazendo push: {prompt_id} ...")
    try:
        client = Client()
        client.push_prompt(
            prompt_identifier=prompt_id,
            object=chat_template,
            description=description,
            is_public=True,
        )
        print(f"✓ Push realizado com sucesso: {prompt_id}")
        return True
    except TypeError:
        # Versões mais antigas não aceitam is_public
        client = Client()
        client.push_prompt(prompt_identifier=prompt_id, object=chat_template, description=description)
        print(f"✓ Push realizado (marque como público no dashboard): {prompt_id}")
        return True
    except Exception as e:
        if "Nothing to commit" in str(e) or "409" in str(e):
            print(f"✓ Prompt já está atualizado no LangSmith (sem alterações): {prompt_id}")
            return True
        print(f"❌ Erro ao fazer push: {e}")
        return False


def main():
    print_section_header("PUSH DE PROMPTS OTIMIZADOS")

    # USERNAME_LANGSMITH_HUB não é necessário para o push (a API key identifica a conta),
    # mas ainda é obrigatório para o evaluate.py fazer hub.pull("{username}/prompt")
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    yaml_path = "prompts/bug_to_user_story_v2.yml"

    data = load_yaml(yaml_path)
    if not data:
        print(f"❌ Não foi possível carregar {yaml_path}")
        return 1

    prompt_key = list(data.keys())[0]
    prompt_data = data[prompt_key]

    success = push_prompt_to_langsmith("bug_to_user_story_v2", prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
