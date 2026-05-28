# Sample OpenAI Agents SDK

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A multi-agent coding assistant built with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). A triage agent routes questions to specialist agents, protected by an input guardrail that blocks non-programming queries. Demonstrates handoffs, `@function_tool`, guardrails, tracing, and all three `Runner` modes.

## Architecture

```
User ──▶ [TriageAgent]  (InputGuardrail: block non-coding questions)
              │          (OutputGuardrail: ensure useful content)
              │
              ├──handoff_to_explainer──▶ [ExplainerAgent]
              │                          tools: lookup_docs, web_search, save_response
              │
              ├──handoff_to_debugger───▶ [DebuggerAgent]
              │                          tools: run_linter, lookup_docs, web_search
              │
              └──handoff_to_reviewer───▶ [ReviewerAgent]
                                         tools: run_linter, lookup_docs, save_response
```

## Features Demonstrated

| Agents SDK Feature | Location |
|---|---|
| `Agent(name, model, instructions, tools, handoffs)` | `src/agents/` |
| `@function_tool` decorated tools | `src/tools/` |
| `handoff(agent, tool_name_override=...)` | `src/agents/triage.py` |
| `InputGuardrail(guardrail_function=...)` | `src/guardrails.py` + `src/agents/triage.py` |
| `OutputGuardrail(guardrail_function=...)` | `src/guardrails.py` + `src/agents/triage.py` |
| `GuardrailFunctionOutput(output_info, tripwire_triggered)` | `src/guardrails.py` |
| `Runner.run(agent, input)` — async | `main.py` |
| `Runner.run_sync(agent, input)` — synchronous | `main.py` |
| `Runner.run_streamed(agent, input)` — streaming events | `main.py` |
| `with trace("name"):` — tracing | `main.py` |
| `InputGuardrailTripwireTriggered` exception handling | `main.py` |

## Quickstart

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Set OPENAI_API_KEY

# 3. Run (async, default question)
python main.py

# Custom question
python main.py "Explain how Python generators work"

# Debug a bug
python main.py "Why does this raise AttributeError: my_list.append is None"

# Code review
python main.py "Review this code: def add(a,b): return a+b"

# Synchronous mode
python main.py --sync "What is a decorator?"

# Streamed output
python main.py --stream "Explain async/await"
```

## Guardrail Behaviour

The `InputGuardrail` runs **in parallel** with the triage agent's first LLM call. If `tripwire_triggered=True`, the run aborts immediately before producing any response:

```python
try:
    result = await Runner.run(triage_agent, "What's a good pasta recipe?")
except InputGuardrailTripwireTriggered:
    print("Off-topic query blocked")
```

The `OutputGuardrail` validates the final response before it reaches the user, ensuring the agent didn't return a vague non-answer.

## Tracing

Wrapping a run in `with trace("name"):` records the full agent execution tree (tool calls, handoffs, guardrail results) in the [OpenAI traces dashboard](https://platform.openai.com/traces):

```python
with trace("coding-assistant"):
    result = await Runner.run(triage_agent, question)
```

## Tests

```bash
pytest tests/ -v
```

Tool tests call `.fn` directly on `@function_tool` objects — no LLM calls needed. Guardrail tests mock the OpenAI client to verify classification logic in isolation.

## Project Structure

```
src/
├── agents/
│   ├── triage.py      # Entry point with guardrails + handoffs — the file the visualizer parses
│   ├── explainer.py   # Concept explanation specialist
│   ├── debugger.py    # Bug diagnosis specialist
│   └── reviewer.py    # Code review specialist
├── guardrails.py      # InputGuardrail + OutputGuardrail functions
└── tools/
    ├── code_tools.py  # run_linter, lookup_docs, save_response (@function_tool)
    └── web_search.py  # web_search (@function_tool)
tests/
main.py                # Three Runner modes: async, sync, streamed
```

---

Built by [Trango Compute](https://trango-compute.com)
