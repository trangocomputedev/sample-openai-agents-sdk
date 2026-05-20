"""
Tests for guardrail logic using mocked OpenAI responses.
The guardrails call gpt-4o-mini for classification — we mock that call
so tests run without API keys.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _mock_input_parse_response(is_coding: bool, reason: str = "test"):
    """Build a mock return value for the input guardrail's parse call."""
    parsed = MagicMock()
    parsed.is_coding_related = is_coding
    parsed.reason = reason
    choice = MagicMock()
    choice.message.parsed = parsed
    response = MagicMock()
    response.choices = [choice]
    return response


# Keep the old name as an alias so existing call sites don't break.
_mock_parse_response = _mock_input_parse_response


def _mock_output_parse_response(contains_useful: bool, reason: str = "test"):
    """Build a mock return value for the output guardrail's parse call."""
    parsed = MagicMock()
    parsed.contains_useful_content = contains_useful
    parsed.reason = reason
    choice = MagicMock()
    choice.message.parsed = parsed
    response = MagicMock()
    response.choices = [choice]
    return response


# ---------------------------------------------------------------------------
# Input guardrail — coding_topic_guardrail
# ---------------------------------------------------------------------------

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


@pytest.mark.asyncio
async def test_coding_guardrail_records_rejection_reason():
    """Blocked queries should carry the rejection reason in output_info for logging."""
    from src.guardrails import coding_topic_guardrail

    ctx, agent = MagicMock(), MagicMock()
    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_parse_response(is_coding=False, reason="unrelated topic")
        )
        result = await coding_topic_guardrail(ctx, agent, "Tell me a joke")

    assert result.tripwire_triggered is True
    assert result.output_info.reason == "unrelated topic"


@pytest.mark.asyncio
async def test_coding_guardrail_non_string_input_coerced():
    """Non-string inputs (e.g. a list of message dicts) must be coerced to str without raising."""
    from src.guardrails import coding_topic_guardrail

    ctx, agent = MagicMock(), MagicMock()
    non_string_input = [{"role": "user", "content": "How do I sort a list?"}]
    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_parse_response(is_coding=True)
        )
        result = await coding_topic_guardrail(ctx, agent, non_string_input)

    assert result.tripwire_triggered is False


# ---------------------------------------------------------------------------
# Output guardrail — useful_output_guardrail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_useful_output_guardrail_passes_good_content():
    """A response containing code and explanation must not trigger the output guardrail."""
    from src.guardrails import useful_output_guardrail

    ctx, agent = MagicMock(), MagicMock()
    output = MagicMock()
    output.final_output = "Here is the fix:\n```python\nx = 1\n```\nThis works because..."

    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_output_parse_response(contains_useful=True)
        )
        result = await useful_output_guardrail(ctx, agent, output)

    assert result.tripwire_triggered is False


@pytest.mark.asyncio
async def test_useful_output_guardrail_blocks_vague_refusal():
    """A vague 'I cannot help' response with no content must trigger the output guardrail."""
    from src.guardrails import useful_output_guardrail

    ctx, agent = MagicMock(), MagicMock()
    output = MagicMock()
    output.final_output = "I'm sorry, I cannot help with that."

    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_output_parse_response(contains_useful=False, reason="vague refusal")
        )
        result = await useful_output_guardrail(ctx, agent, output)

    assert result.tripwire_triggered is True


@pytest.mark.asyncio
async def test_useful_output_guardrail_output_info_populated():
    """output_info must carry the guardrail's classification so callers can log it."""
    from src.guardrails import useful_output_guardrail

    ctx, agent = MagicMock(), MagicMock()
    output = MagicMock()
    output.final_output = "Here is a detailed explanation with code..."

    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_output_parse_response(contains_useful=True, reason="contains code")
        )
        result = await useful_output_guardrail(ctx, agent, output)

    assert result.output_info.contains_useful_content is True
    assert result.output_info.reason == "contains code"


@pytest.mark.asyncio
async def test_useful_output_guardrail_falls_back_to_str():
    """When output lacks a final_output attribute, str() must be used as a fallback."""
    from src.guardrails import useful_output_guardrail

    ctx, agent = MagicMock(), MagicMock()
    # Plain string with no .final_output attribute
    output = "def add(a, b): return a + b"

    with patch("src.guardrails._client") as mock_client:
        mock_client.beta.chat.completions.parse = AsyncMock(
            return_value=_mock_output_parse_response(contains_useful=True)
        )
        result = await useful_output_guardrail(ctx, agent, output)

    assert result.tripwire_triggered is False
