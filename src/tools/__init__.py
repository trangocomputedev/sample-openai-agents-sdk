"""
Public tool interface for the coding assistant agents.

All tools are decorated with @function_tool, which registers them with the
OpenAI Agents SDK so agents can invoke them as structured function calls.
Import from this package rather than from individual modules to keep
coupling to the internal layout to a minimum.
"""
from .code_tools import run_linter, lookup_docs, save_response
from .web_search import web_search

__all__ = ["run_linter", "lookup_docs", "save_response", "web_search"]
