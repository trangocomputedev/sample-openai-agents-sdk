"""
Triage agent — entry point with input guardrail and handoffs to specialists.

Architecture:
    User ──▶ [TriageAgent] (InputGuardrail: block non-coding)
                  │
                  ├──(explain)──▶ [ExplainerAgent]  tools: lookup_docs, web_search, save_response
                  ├──(debug)────▶ [DebuggerAgent]   tools: run_linter, lookup_docs, web_search
                  └──(review)───▶ [ReviewerAgent]   tools: run_linter, lookup_docs, save_response
"""
from agents import Agent, handoff
from src.agents.explainer import explainer_agent
from src.agents.debugger import debugger_agent
from src.agents.reviewer import reviewer_agent
from src.guardrails import on_topic_guardrail, quality_output_guardrail

triage_agent = Agent(
    name="TriageAgent",
    model="gpt-4o-mini",
    instructions=(
        "You are the entry point for a coding assistant. "
        "Classify the user's request and immediately hand off to the right specialist — "
        "do not attempt to answer the question yourself:\n\n"
        "  • Concept or how-to question → handoff to ExplainerAgent\n"
        "  • Bug, error, or unexpected behaviour → handoff to DebuggerAgent\n"
        "  • Code review or quality feedback → handoff to ReviewerAgent\n\n"
        "If the request is ambiguous, ask one clarifying question before routing."
    ),
    handoffs=[
        handoff(explainer_agent, tool_name_override="handoff_to_explainer"),
        handoff(debugger_agent,  tool_name_override="handoff_to_debugger"),
        handoff(reviewer_agent,  tool_name_override="handoff_to_reviewer"),
    ],
    input_guardrails=[on_topic_guardrail],
    output_guardrails=[quality_output_guardrail],
)
