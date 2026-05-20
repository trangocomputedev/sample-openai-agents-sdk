"""
Tests for guardrail logic using mocked OpenAI responses.
The guardrails call gpt-4o-mini for classification — we mock that call
so tests run without API keys.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _mock_parse_response(is_coding: bool, reason: str = "test"):
    """Build a mock return value for beta.chat.completions.parse."""
    parsed = MagicMock()
    parsed.is_coding_related = is_coding
    parsed.reason = reason
    choice = MagicMock()
    choice.message.parsed = parsed
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.mark.asyncio
async def test_coding_guardrail_passes_coding_question():
    from src.guardrails import coding_topic_guardrail

    ctx, agent = MagicMock(), MagicMock()
    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_parse_response(is_coding=True)
        )
        result = await coding_topic_guardrail(ctx, agent, "How do I use async/await in Python?")

    assert result.tripwire_triggered is False


@pytest.mark.asyncio
async def test_coding_guardrail_blocks_off_topic():
    from src.guardrails import coding_topic_guardrail

    ctx, agent = MagicMock(), MagicMock()
    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_parse_response(is_coding=False, reason="recipe question")
        )
        result = await coding_topic_guardrail(ctx, agent, "What's a good pasta recipe?")

    assert result.tripwire_triggered is True


@pytest.mark.asyncio
async def test_coding_guardrail_output_info_populated():
    from src.guardrails import coding_topic_guardrail

    ctx, agent = MagicMock(), MagicMock()
    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_parse_response(is_coding=True, reason="clearly a coding question")
        )
        result = await coding_topic_guardrail(ctx, agent, "Explain decorators")

    assert result.output_info.is_coding_related is True
    assert result.output_info.reason == "clearly a coding question"
