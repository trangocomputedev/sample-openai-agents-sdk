"""
Coding assistant entry point — demonstrates three Runner modes.

Usage:
    python main.py                              # async run (default question)
    python main.py "explain Python decorators"  # async run with custom input
    python main.py --sync   "debug this code"   # synchronous run
    python main.py --stream "review my code"    # streamed run with event printing
"""
import asyncio
import sys
from dotenv import load_dotenv
load_dotenv()

from agents import Runner, trace
from agents.exceptions import InputGuardrailTripwireTriggered
from src.agents import triage_agent


async def run_async(question: str) -> None:
    """Standard async run — returns the final response."""
    print(f"Question: {question}\n{'─' * 60}")
    try:
        with trace("coding-assistant"):
            result = await Runner.run(triage_agent, question)
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("Sorry — I can only help with software development and programming questions.")


def run_sync(question: str) -> None:
    """Synchronous convenience wrapper — useful in scripts and notebooks."""
    print(f"Question: {question}\n{'─' * 60}")
    try:
        result = Runner.run_sync(triage_agent, question)
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("Sorry — I can only help with software development and programming questions.")


async def run_streamed(question: str) -> None:
    """Streamed run — prints events as they arrive."""
    print(f"Question: {question}\n{'─' * 60}")
    try:
        result = Runner.run_streamed(triage_agent, question)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, "delta"):
                print(event.data.delta, end="", flush=True)
        print()
    except InputGuardrailTripwireTriggered:
        print("Sorry — I can only help with programming questions.")


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "async"
    if args and args[0] in ("--sync", "--stream"):
        mode = args.pop(0).lstrip("-")

    question = " ".join(args) if args else "Explain how Python's @property decorator works, with an example."

    if mode == "sync":
        run_sync(question)
    elif mode == "stream":
        asyncio.run(run_streamed(question))
    else:
        asyncio.run(run_async(question))
