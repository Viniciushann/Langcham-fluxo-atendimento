"""
Testes para fragmentação e envio de respostas.

Testa:
- quebrar_texto_inteligente
- limpar_mensagem
- fragmentar_resposta
- enviar_respostas (mockado)
"""

import pytest
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from nodes.response import quebrar_texto_inteligente, limpar_mensagem, fragmentar_resposta


# ==============================================
# TESTES DE quebrar_texto_inteligente
# ==============================================

@pytest.mark.unit
def test_quebrar_texto_curto():
    """Testa que texto curto não é fragmentado."""
    texto = "Olá! Tudo bem?"
    fragmentos = quebrar_texto_inteligente(texto, max_chars=100)

    assert len(fragmentos) == 1
    assert fragmentos[0] == texto


@pytest.mark.unit
def test_quebrar_texto_por_paragrafos():
    """Testa quebra por parágrafos."""
    texto = "Parágrafo 1 aqui.\n\nParágrafo 2 aqui."
    fragmentos = quebrar_texto_inteligente(texto, max_chars=20)

    assert len(fragmentos) >= 2
    assert "Parágrafo 1" in fragmentos[0]


@pytest.mark.unit
def test_quebrar_texto_por_frases():
    """Testa quebra respeitando frases."""
    texto = "Frase 1 aqui. Frase 2 aqui. Frase 3 aqui."
    fragmentos = quebrar_texto_inteligente(texto, max_chars=20)

    # Deve quebrar em frases completas
    assert len(fragmentos) > 1
    for frag in fragmentos:
        # Cada fragmento deve ter pontuação de fim
        assert frag.strip()[-1] in ['.', '!', '?'] or len(frag) <= 20


@pytest.mark.unit
def test_quebrar_texto_vazio():
    """Testa que texto vazio retorna lista vazia."""
    assert quebrar_texto_inteligente("") == []
    assert quebrar_texto_inteligente("   ") == []


# ==============================================
# TESTES DE limpar_mensagem
# ==============================================

@pytest.mark.unit
def test_limpar_aspas():
    """Testa escape de aspas duplas."""
    texto = 'Teste com "aspas"'
    limpo = limpar_mensagem(texto)

    assert '\\"' in limpo


@pytest.mark.unit
def test_limpar_quebras_linha():
    """Testa escape de quebras de linha."""
    texto = 'Linha 1\nLinha 2'
    limpo = limpar_mensagem(texto)

    assert '\\n' in limpo
    assert '\n' not in limpo


@pytest.mark.unit
def test_limpar_markdown():
    """Testa escape de caracteres markdown."""
    texto = 'Texto com *asteriscos* e _underscores_'
    limpo = limpar_mensagem(texto)

    assert '\\*' in limpo
    assert '\\_' in limpo


@pytest.mark.unit
def test_limpar_hashtags():
    """Testa remoção de hashtags."""
    texto = 'Texto com #hashtag'
    limpo = limpar_mensagem(texto)

    assert '#' not in limpo


@pytest.mark.unit
def test_limpar_vazio():
    """Testa limpeza de texto vazio."""
    assert limpar_mensagem("") == ""
    assert limpar_mensagem(None) == ""


# ==============================================
# TESTES DE fragmentar_resposta
# ==============================================

@pytest.mark.unit
def test_fragmentar_resposta_sucesso():
    """Testa fragmentação bem-sucedida."""
    state = {
        "resposta_agente": "Resposta longa do agente aqui. " * 20,
        "next_action": ""
    }

    result = fragmentar_resposta(state)

    assert "respostas_fragmentadas" in result
    assert len(result["respostas_fragmentadas"]) > 1
    assert result["next_action"] != ""


@pytest.mark.unit
def test_fragmentar_resposta_curta():
    """Testa fragmentação de resposta curta."""
    state = {
        "resposta_agente": "Resposta curta",
        "next_action": ""
    }

    result = fragmentar_resposta(state)

    assert len(result["respostas_fragmentadas"]) == 1
    assert result["respostas_fragmentadas"][0] == "Resposta curta"


@pytest.mark.unit
def test_fragmentar_resposta_vazia():
    """Testa fragmentação de resposta vazia."""
    state = {
        "resposta_agente": "",
        "next_action": ""
    }

    result = fragmentar_resposta(state)

    # Deve ter erro
    assert "erro" in result or result.get("next_action") == "erro"
