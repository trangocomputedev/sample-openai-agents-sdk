"""
Reviewer agent — specialist for code review and quality feedback.

Receives handoffs from TriageAgent when the user requests a code review.
Combines mechanical linting (run_linter) with higher-level review criteria:
readability, idiomatic style, performance, security, and test coverage gaps.

Response format: Summary / Issues (with severity) / Suggestions / Verdict.
The final review is saved with save_response for the user to reference later.
"""
from agents import Agent
from src.tools import run_linter, lookup_docs, save_response

reviewer_agent = Agent(
    name="ReviewerAgent",
    model="gpt-4o",
    instructions=(
        "You are a senior engineer performing code review. "
        "Use run_linter to check for mechanical issues, then review for: "
        "readability, idiomatic style, performance, security, and test coverage gaps. "
        "Structure your review as: 'Summary', 'Issues' (with severity), 'Suggestions', 'Verdict'. "
        "Save the final review with save_response."
    ),
    tools=[run_linter, lookup_docs, save_response],
)
