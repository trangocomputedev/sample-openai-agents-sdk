"""Tests for @function_tool decorated tools — no LLM calls."""
import pytest
from pathlib import Path


def test_run_linter_clean_code():
    from src.tools.code_tools import run_linter
    result = run_linter.fn(code="x = 1\ny = x + 2\n", language="python")
    assert "No issues" in result


def test_run_linter_detects_long_line():
    from src.tools.code_tools import run_linter
    long_line = "x = " + "a" * 120
    result = run_linter.fn(code=long_line, language="python")
    assert "E501" in result


def test_run_linter_detects_print():
    from src.tools.code_tools import run_linter
    result = run_linter.fn(code='print("hello")', language="python")
    assert "print" in result.lower()


def test_lookup_docs_known_topic():
    from src.tools.code_tools import lookup_docs
    result = lookup_docs.fn(topic="list")
    assert "append" in result.lower()


def test_lookup_docs_unknown_topic():
    from src.tools.code_tools import lookup_docs
    result = lookup_docs.fn(topic="xyz_nonexistent")
    assert "No reference entry" in result


def test_lookup_docs_case_insensitive():
    from src.tools.code_tools import lookup_docs
    assert lookup_docs.fn(topic="DICT") == lookup_docs.fn(topic="dict")


def test_save_response_creates_file(tmp_path, monkeypatch):
    import src.tools.code_tools as ct
    monkeypatch.setattr(ct, "_OUTPUT_DIR", tmp_path)
    result = ct.save_response.fn(filename="test_out", content="# Hello")
    assert (tmp_path / "test_out.md").exists()
    assert "test_out" in result


def test_web_search_returns_string():
    from src.tools.web_search import web_search
    result = web_search.fn(query="Python asyncio")
    assert isinstance(result, str)
    assert "Python asyncio" in result


def test_function_tools_have_names():
    from src.tools.code_tools import run_linter, lookup_docs, save_response
    from src.tools.web_search import web_search
    for tool in (run_linter, lookup_docs, save_response, web_search):
        assert hasattr(tool, "name")
        assert len(tool.name) > 0
