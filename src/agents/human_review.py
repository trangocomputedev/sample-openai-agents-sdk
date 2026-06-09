"""
Human review agent — escalation gate for edge cases requiring a human decision.

Receives handoffs from ReviewerAgent when the code raises security concerns,
involves destructive operations, or requires a judgment call beyond automated review.
Pauses the pipeline and surfaces the review to a human operator.
"""
from agents import Agent

human_review_agent = Agent(
    name="HumanReviewAgent",
    model="gpt-4o-mini",
    instructions=(
        "You are a placeholder representing a human reviewer. "
        "Summarize the context passed to you and explain clearly what decision "
        "the human operator needs to make. Do not attempt to resolve the issue — "
        "present the facts and await a human response."
    ),
    tools=[],
)
