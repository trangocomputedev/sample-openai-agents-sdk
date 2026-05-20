"""
Public interface for all specialist agents in the coding assistant.

triage_agent is the entry point — it inspects the user's request and routes
to the correct specialist via handoff.  Downstream agents are not meant to
be called directly from main.py.
"""
from .triage import triage_agent
from .explainer import explainer_agent
from .debugger import debugger_agent
from .reviewer import reviewer_agent

__all__ = ["triage_agent", "explainer_agent", "debugger_agent", "reviewer_agent"]
