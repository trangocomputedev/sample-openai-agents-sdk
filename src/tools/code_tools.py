from pathlib import Path
from agents import function_tool

_OUTPUT_DIR = Path("outputs")

_DOCS = {
    "list": "list — ordered, mutable sequence. Methods: append, extend, insert, remove, pop, sort.",
    "dict": "dict — key-value mapping. Methods: get, keys, values, items, update, pop.",
    "async": "async/await — Python coroutine syntax. Use asyncio.run() to execute from sync code.",
    "decorator": "@decorator syntax wraps a function, returning a new callable with added behavior.",
    "generator": "Generator functions use 'yield' to produce values lazily without storing all in memory.",
    "dataclass": "@dataclass auto-generates __init__, __repr__, __eq__ from annotated class fields.",
    "pathlib": "pathlib.Path — object-oriented filesystem paths. Prefer over os.path for new code.",
    "typing": "typing module — provides type hint constructs: List, Dict, Optional, Union, Literal, etc.",
}


@function_tool
def run_linter(code: str, language: str = "python") -> str:
    """Run a static linter on a code snippet and return any style or error findings.

    Args:
        code: The source code to analyse.
        language: Programming language. Defaults to 'python'.
    """
    # Stub — replace with subprocess call to flake8/eslint in production
    issues = []
    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        if len(line) > 120:
            issues.append(f"Line {i}: E501 line too long ({len(line)} > 120 chars)")
        if "print(" in line and language == "python":
            issues.append(f"Line {i}: W print statement found — consider using logging")
    if not issues:
        return "No issues found."
    return "\n".join(issues)


@function_tool
def lookup_docs(topic: str) -> str:
    """Look up a concise reference for a Python built-in, keyword, or standard library concept.

    Args:
        topic: The concept to look up, e.g. 'list', 'async', 'dataclass'.
    """
    key = topic.lower().strip()
    return _DOCS.get(key, f"No reference entry for '{topic}'. Try a more specific term.")


@function_tool
def save_response(filename: str, content: str) -> str:
    """Save a code snippet or explanation to the outputs directory.

    Args:
        filename: Output filename (without extension — .md is appended).
        content: Markdown-formatted content to save.
    """
    _OUTPUT_DIR.mkdir(exist_ok=True)
    if not filename.endswith(".md"):
        filename += ".md"
    path = _OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return f"Saved to {path}"
