"""
Tests for @function_tool decorated tools — no LLM calls.

The OpenAI Agents SDK wraps each tool in a FunctionTool object whose underlying
function is invoked via the async `on_invoke_tool(ctx, json_str)` interface.
`_call` is a small helper defined here to keep individual tests readable.
"""
import json
import pytest
from unittest.mock import MagicMock


async def _call(tool, **kwargs) -> str:
    """Invoke a FunctionTool by serialising kwargs to JSON, as the SDK does at runtime."""
    ctx = MagicMock()
    return await tool.on_invoke_tool(ctx, json.dumps(kwargs))


# ---------------------------------------------------------------------------
# run_linter
# ---------------------------------------------------------------------------

async def test_run_linter_clean_code():
    from src.tools.code_tools import run_linter
    result = await _call(run_linter, code="x = 1\ny = x + 2\n", language="python")
    assert "No issues" in result


async def test_run_linter_detects_long_line():
    from src.tools.code_tools import run_linter
    long_line = "x = " + "a" * 120
    result = await _call(run_linter, code=long_line, language="python")
    assert "E501" in result


async def test_run_linter_detects_print():
    from src.tools.code_tools import run_linter
    result = await _call(run_linter, code='print("hello")', language="python")
    assert "print" in result.lower()


async def test_run_linter_detects_multiple_issues():
    """A snippet with both a long line and a print call should report two distinct issues."""
    from src.tools.code_tools import run_linter
    code = 'print("debug")\n' + "x = " + "a" * 120
    result = await _call(run_linter, code=code, language="python")
    assert "E501" in result
    assert "print" in result.lower()


async def test_run_linter_no_print_warning_for_non_python():
    """Print warnings are Python-specific; other languages must not trigger them."""
    from src.tools.code_tools import run_linter
    result = await _call(run_linter, code='print("hello")', language="javascript")
    assert "W print" not in result


async def test_run_linter_default_language_flags_print():
    """Omitting language defaults to python, so print statements must be flagged."""
    from src.tools.code_tools import run_linter
    result = await _call(run_linter, code='print("hello")')
    assert "print" in result.lower()


# ---------------------------------------------------------------------------
# lookup_docs
# ---------------------------------------------------------------------------

async def test_lookup_docs_known_topic():
    from src.tools.code_tools import lookup_docs
    result = await _call(lookup_docs, topic="list")
    assert "append" in result.lower()


async def test_lookup_docs_unknown_topic():
    from src.tools.code_tools import lookup_docs
    result = await _call(lookup_docs, topic="xyz_nonexistent")
    assert "No reference entry" in result


async def test_lookup_docs_case_insensitive():
    from src.tools.code_tools import lookup_docs
    result_upper = await _call(lookup_docs, topic="DICT")
    result_lower = await _call(lookup_docs, topic="dict")
    assert result_upper == result_lower


async def test_lookup_docs_all_known_topics():
    """Every key in _DOCS must return a non-empty, meaningful description."""
    from src.tools.code_tools import lookup_docs, _DOCS
    for topic in _DOCS:
        result = await _call(lookup_docs, topic=topic)
        assert result, f"Empty result for topic '{topic}'"
        assert "No reference entry" not in result


# ---------------------------------------------------------------------------
# save_response
# ---------------------------------------------------------------------------

async def test_save_response_creates_file(tmp_path, monkeypatch):
    import src.tools.code_tools as ct
    monkeypatch.setattr(ct, "_OUTPUT_DIR", tmp_path)
    result = await _call(ct.save_response, filename="test_out", content="# Hello")
    assert (tmp_path / "test_out.md").exists()
    assert "test_out" in result


async def test_save_response_already_has_md_extension(tmp_path, monkeypatch):
    """Filenames already ending in .md must not get a second .md appended."""
    import src.tools.code_tools as ct
    monkeypatch.setattr(ct, "_OUTPUT_DIR", tmp_path)
    await _call(ct.save_response, filename="already.md", content="content")
    assert (tmp_path / "already.md").exists()
    assert not (tmp_path / "already.md.md").exists()


async def test_save_response_content_written(tmp_path, monkeypatch):
    """The exact content passed to save_response must appear verbatim in the output file."""
    import src.tools.code_tools as ct
    monkeypatch.setattr(ct, "_OUTPUT_DIR", tmp_path)
    await _call(ct.save_response, filename="verify", content="# My Content\n\nHello, world!")
    text = (tmp_path / "verify.md").read_text(encoding="utf-8")
    assert "# My Content" in text
    assert "Hello, world!" in text


# ---------------------------------------------------------------------------
# web_search
# ---------------------------------------------------------------------------

async def test_web_search_returns_string():
    from src.tools.web_search import web_search
    result = await _call(web_search, query="Python asyncio")
    assert isinstance(result, str)
    assert "Python asyncio" in result


async def test_web_search_echoes_query():
    """The stub must include the query in the output so the agent can correlate results."""
    from src.tools.web_search import web_search
    result = await _call(web_search, query="Python generators")
    assert "Python generators" in result


async def test_web_search_returns_three_sources():
    """The stub returns exactly three numbered sources for the agent to cite."""
    from src.tools.web_search import web_search
    result = await _call(web_search, query="anything")
    assert "1." in result
    assert "2." in result
    assert "3." in result


# ---------------------------------------------------------------------------
# SDK contract — all tools must expose a non-empty name
# ---------------------------------------------------------------------------

def test_function_tools_have_names():
    from src.tools.code_tools import run_linter, lookup_docs, save_response
    from src.tools.web_search import web_search
    for tool in (run_linter, lookup_docs, save_response, web_search):
        assert hasattr(tool, "name")
        assert len(tool.name) > 0
