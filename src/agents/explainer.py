"""
Explainer agent — specialist for teaching programming concepts and how-tos.

Receives handoffs from TriageAgent for concept explanations or how-to questions.
Uses lookup_docs for quick Python references, web_search for deeper topics,
and save_response to persist polished explanations for later reuse.

All responses are Markdown-formatted and include at least one working code example.
"""
from agents import Agent
from src.tools import lookup_docs, web_search, save_response

explainer_agent = Agent(
    name="ExplainerAgent",
    model="gpt-4o",
    instructions=(
        "You are a patient, expert programming teacher. "
        "Explain concepts clearly with concrete examples and code snippets. "
        "Use lookup_docs for quick Python references and web_search for deeper topics. "
        "Save polished explanations with save_response. "
        "Always include a working code example. Respond in Markdown."
    ),
    tools=[lookup_docs, web_search, save_response],
)
