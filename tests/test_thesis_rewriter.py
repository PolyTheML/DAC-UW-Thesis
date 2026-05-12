from unittest.mock import MagicMock, patch
import anthropic as anthropic_lib
from scripts.thesis_scorer import Violation


@patch("scripts.thesis_rewriter.anthropic.Anthropic")
def test_rewrite_calls_api_and_returns_string(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="# Fixed [CITATION: needed]")]
    )
    from scripts.thesis_rewriter import rewrite_chapter
    violations = [Violation("1.1", "citation_placeholder", "Missing citation", "warning")]
    result = rewrite_chapter("# Original", violations)
    assert result == "# Fixed [CITATION: needed]"
    assert mock_client.messages.create.called


def test_rewrite_returns_original_when_no_violations():
    from scripts.thesis_rewriter import rewrite_chapter
    content = "# Chapter\n\nSome text."
    result = rewrite_chapter(content, violations=[])
    assert result == content


@patch("scripts.thesis_rewriter.anthropic.Anthropic")
def test_rewrite_includes_violations_in_user_message(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="fixed")]
    )
    from scripts.thesis_rewriter import rewrite_chapter
    violations = [Violation("2.1", "heading_hierarchy", "### before ##", "error")]
    rewrite_chapter("content", violations)
    user_msg = mock_client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "heading_hierarchy" in user_msg
    assert "2.1" in user_msg
    assert "### before ##" in user_msg


@patch("scripts.thesis_rewriter.anthropic.Anthropic")
def test_rewrite_uses_configured_model(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="fixed")]
    )
    from scripts.thesis_rewriter import rewrite_chapter
    violations = [Violation("1.1", "citation_placeholder", "Missing", "warning")]
    rewrite_chapter("content", violations, model="claude-haiku-4-5-20251001")
    assert mock_client.messages.create.call_args.kwargs["model"] == "claude-haiku-4-5-20251001"


@patch("scripts.thesis_rewriter.time.sleep")
@patch("scripts.thesis_rewriter.anthropic.Anthropic")
def test_rewrite_falls_back_to_original_after_two_failures(mock_class, mock_sleep, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.side_effect = anthropic_lib.APIError(
        "error", request=MagicMock(), body={}
    )
    from scripts.thesis_rewriter import rewrite_chapter
    violations = [Violation("1.1", "citation_placeholder", "Missing", "warning")]
    result = rewrite_chapter("# Original content", violations)
    assert result == "# Original content"
