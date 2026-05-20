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
