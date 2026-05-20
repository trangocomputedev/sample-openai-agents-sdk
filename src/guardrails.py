"""
Input and output guardrails for the coding assistant.

InputGuardrail runs in parallel with the agent's first LLM call. If the
tripwire triggers, the run is aborted before the agent produces a response.
"""
from __future__ import annotations

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrail,
    OutputGuardrail,
    RunContextWrapper,
)
from openai import AsyncOpenAI
from pydantic import BaseModel

_client = AsyncOpenAI()


# ---------------------------------------------------------------------------
# Input guardrail — block non-coding questions
# ---------------------------------------------------------------------------

class _TopicCheck(BaseModel):
    is_coding_related: bool
    reason: str


async def coding_topic_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str,
) -> GuardrailFunctionOutput:
    """Reject queries unrelated to software development or programming."""
    result = await _client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Determine whether the user's message is related to software development, "
                    "programming, debugging, code review, or technical documentation. "
                    "Reply with is_coding_related=true or false and a one-sentence reason."
                ),
            },
            {"role": "user", "content": input if isinstance(input, str) else str(input)},
        ],
        response_format=_TopicCheck,
    )
    check = result.choices[0].message.parsed
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_coding_related,
    )


on_topic_guardrail = InputGuardrail(guardrail_function=coding_topic_guardrail)


# ---------------------------------------------------------------------------
# Output guardrail — ensure responses contain actual code or explanation
# ---------------------------------------------------------------------------

class _OutputCheck(BaseModel):
    contains_useful_content: bool
    reason: str


async def useful_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output,
) -> GuardrailFunctionOutput:
    """Flag responses that are vague refusals with no actionable content."""
    content = output.final_output if hasattr(output, "final_output") else str(output)
    result = await _client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Check whether this assistant response provides useful technical content "
                    "(code, explanation, steps, or references). "
                    "A vague 'I cannot help' with no content is NOT useful."
                ),
            },
            {"role": "user", "content": content},
        ],
        response_format=_OutputCheck,
    )
    check = result.choices[0].message.parsed
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.contains_useful_content,
    )


quality_output_guardrail = OutputGuardrail(guardrail_function=useful_output_guardrail)
