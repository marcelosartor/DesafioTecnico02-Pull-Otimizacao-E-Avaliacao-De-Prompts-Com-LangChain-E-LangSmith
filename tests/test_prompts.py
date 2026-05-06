"""
Testes automatizados para validação do prompt otimizado v2.
"""
import re
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


@pytest.fixture(scope="module")
def prompt_data():
    """Carrega e retorna o inner dict do prompt v2."""
    with open(PROMPT_V2_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    key = list(raw.keys())[0]
    return raw[key]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' ausente no YAML"
        assert prompt_data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system = prompt_data.get("system_prompt", "")
        persona_pattern = re.compile(
            r"(você é|you are|product manager|especialista|sênior|sr\.|especializado)",
            re.IGNORECASE,
        )
        assert persona_pattern.search(system), (
            "O system_prompt não contém definição de persona. "
            "Inclua algo como 'Você é um Product Manager...'."
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system = prompt_data.get("system_prompt", "")
        format_pattern = re.compile(
            r"(markdown|user story|como.*eu quero|como.*quero|critérios de aceitação|gherkin|given|when|then)",
            re.IGNORECASE,
        )
        assert format_pattern.search(system), (
            "O system_prompt não menciona formato de saída esperado (Markdown, User Story, Gherkin)."
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system = prompt_data.get("system_prompt", "")
        # Few-shot: deve ter pelo menos 2 ocorrências de "Bug report" ou "Exemplo"
        example_pattern = re.compile(r"(exemplo|bug report|user story gerada)", re.IGNORECASE)
        matches = example_pattern.findall(system)
        assert len(matches) >= 4, (
            f"Few-shot Learning requer pelo menos 2 exemplos completos (entrada+saída). "
            f"Encontrados {len(matches) // 2} blocos de exemplo."
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que não há nenhum [TODO] pendente no texto."""
        system = prompt_data.get("system_prompt", "")
        user = prompt_data.get("user_prompt", "")
        full_text = system + user
        assert "[TODO]" not in full_text and "[todo]" not in full_text.lower(), (
            "O prompt contém marcadores [TODO] não resolvidos."
        )

    def test_minimum_techniques(self, prompt_data):
        """Verifica se pelo menos 2 técnicas foram listadas nos metadados."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"São necessárias pelo menos 2 técnicas em 'techniques_applied'. "
            f"Encontradas: {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
