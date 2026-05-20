"""
Tests for agent configuration — verifies that each agent has the correct name,
tools, handoffs, and guardrail wiring without making any LLM calls.

These tests are intentionally structural: they catch accidental misconfigurations
(wrong tools on the wrong agent, missing guardrails, broken handoff list) that
would only surface at runtime otherwise.
"""
import pytest


class TestTriageAgent:
    def test_name(self):
        from src.agents import triage_agent
        assert triage_agent.name == "TriageAgent"

    def test_has_three_handoffs(self):
        """Triage must route to exactly three specialists: explainer, debugger, reviewer."""
        from src.agents import triage_agent
        assert len(triage_agent.handoffs) == 3

    def test_has_input_guardrail(self):
        """Input guardrail must be registered to block off-topic questions."""
        from src.agents import triage_agent
        assert len(triage_agent.input_guardrails) == 1

    def test_has_output_guardrail(self):
        """Output guardrail must be registered to flag vague responses."""
        from src.agents import triage_agent
        assert len(triage_agent.output_guardrails) == 1

    def test_no_direct_tools(self):
        """Triage only routes — it must not have its own tools."""
        from src.agents import triage_agent
        assert not triage_agent.tools  # falsy: None or []

    def test_input_guardrail_is_on_topic(self):
        """The registered input guardrail must be the coding-topic check."""
        from src.agents import triage_agent
        from src.guardrails import on_topic_guardrail
        assert triage_agent.input_guardrails[0] is on_topic_guardrail

    def test_output_guardrail_is_quality_check(self):
        """The registered output guardrail must be the quality/usefulness check."""
        from src.agents import triage_agent
        from src.guardrails import quality_output_guardrail
        assert triage_agent.output_guardrails[0] is quality_output_guardrail


class TestDebuggerAgent:
    def test_name(self):
        from src.agents import debugger_agent
        assert debugger_agent.name == "DebuggerAgent"

    def test_has_linter_tool(self):
        from src.agents import debugger_agent
        from src.tools import run_linter
        assert run_linter in debugger_agent.tools

    def test_has_docs_tool(self):
        from src.agents import debugger_agent
        from src.tools import lookup_docs
        assert lookup_docs in debugger_agent.tools

    def test_has_web_search_tool(self):
        from src.agents import debugger_agent
        from src.tools import web_search
        assert web_search in debugger_agent.tools

    def test_does_not_have_save_response(self):
        """Debugger produces inline fixes, not saved files — save_response is not needed."""
        from src.agents import debugger_agent
        from src.tools import save_response
        assert save_response not in debugger_agent.tools


class TestExplainerAgent:
    def test_name(self):
        from src.agents import explainer_agent
        assert explainer_agent.name == "ExplainerAgent"

    def test_has_docs_tool(self):
        from src.agents import explainer_agent
        from src.tools import lookup_docs
        assert lookup_docs in explainer_agent.tools

    def test_has_web_search_tool(self):
        from src.agents import explainer_agent
        from src.tools import web_search
        assert web_search in explainer_agent.tools

    def test_has_save_response_tool(self):
        """Explainer persists polished explanations for reuse — save_response is required."""
        from src.agents import explainer_agent
        from src.tools import save_response
        assert save_response in explainer_agent.tools

    def test_does_not_have_linter(self):
        """Explaining concepts does not require mechanical linting."""
        from src.agents import explainer_agent
        from src.tools import run_linter
        assert run_linter not in explainer_agent.tools


class TestReviewerAgent:
    def test_name(self):
        from src.agents import reviewer_agent
        assert reviewer_agent.name == "ReviewerAgent"

    def test_has_linter_tool(self):
        from src.agents import reviewer_agent
        from src.tools import run_linter
        assert run_linter in reviewer_agent.tools

    def test_has_docs_tool(self):
        from src.agents import reviewer_agent
        from src.tools import lookup_docs
        assert lookup_docs in reviewer_agent.tools

    def test_has_save_response_tool(self):
        """Reviewer saves the final review for the user to reference later."""
        from src.agents import reviewer_agent
        from src.tools import save_response
        assert save_response in reviewer_agent.tools

    def test_does_not_have_web_search(self):
        """Reviewer works from the submitted code; web search is not in its tool list."""
        from src.agents import reviewer_agent
        from src.tools import web_search
        assert web_search not in reviewer_agent.tools


def test_all_agents_exported():
    """All four agents must be importable from the src.agents package."""
    from src.agents import triage_agent, explainer_agent, debugger_agent, reviewer_agent
    for agent in (triage_agent, explainer_agent, debugger_agent, reviewer_agent):
        assert agent is not None


def test_all_tools_exported():
    """All four tools must be importable from the src.tools package."""
    from src.tools import run_linter, lookup_docs, save_response, web_search
    for tool in (run_linter, lookup_docs, save_response, web_search):
        assert tool is not None
