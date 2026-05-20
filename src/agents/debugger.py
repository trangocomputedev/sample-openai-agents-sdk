"""
Debugger agent — specialist for bug analysis, error diagnosis, and code fixes.

Receives handoffs from TriageAgent when the user reports a bug, error, or
unexpected behaviour. Combines mechanical linting (run_linter) with API
verification (lookup_docs, web_search) before producing a structured fix.

Response format: Root Cause / Fix / Explanation.
"""
from agents import Agent
from src.tools import run_linter, lookup_docs, web_search

debugger_agent = Agent(
    name="DebuggerAgent",
    model="gpt-4o",
    instructions=(
        "You are an expert debugger. Analyse code for bugs, logic errors, and edge cases. "
        "Use run_linter to catch style issues and lookup_docs or web_search to verify correct API usage. "
        "Always explain WHY the bug occurs and provide a corrected version of the code. "
        "Format your response with sections: 'Root Cause', 'Fix', 'Explanation'."
    ),
    tools=[run_linter, lookup_docs, web_search],
)
