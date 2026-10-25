"""Tests for ``dkit components``."""

from __future__ import annotations

import pytest

from dkit.commands.components import component_types


def test_component_types_loads() -> None:
    types = component_types()
    assert len(types) >= 20
    assert any(t["name"] == "Button" and t["type"] == "2" for t in types)


def test_component_types_have_required_keys() -> None:
    for entry in component_types():
        assert "type" in entry
        assert "name" in entry
        assert "description" in entry
        assert "style" in entry
        assert "usage" in entry


def test_cli_components_list_all(cli) -> None:
    result = cli("components")
    assert result.exit_code == 0
    assert "Action Row" in result.stdout
    assert "Button" in result.stdout
    assert "String Select" in result.stdout


def test_cli_components_json_all(cli) -> None:
    payload = cli("--json", "components").json
    assert payload["mode"] == "all"
    assert payload["count"] == 20
    assert len(payload["component_types"]) == 20
    assert payload["source"]["source"].startswith("https://github.com/discord/discord-api-docs")
    assert any(c["name"] == "Button" and c["type"] == "2" for c in payload["component_types"])


def test_cli_lookup_by_integer(cli) -> None:
    result = cli("components", "2")
    assert result.exit_code == 0
    assert "Button" in result.stdout
    assert "2" in result.stdout
    assert "Button object" in result.stdout


def test_cli_lookup_by_integer_action_row(cli) -> None:
    result = cli("components", "1")
    assert result.exit_code == 0
    assert "Action Row" in result.stdout


def test_cli_lookup_by_name(cli) -> None:
    result = cli("components", "Button")
    assert result.exit_code == 0
    assert "Button" in result.stdout
    assert "2" in result.stdout


def test_cli_lookup_normalises_name(cli) -> None:
    result = cli("components", "action-row")
    assert result.exit_code == 0
    assert "Action Row" in result.stdout
    assert "1" in result.stdout


def test_cli_lookup_normalises_name_with_spaces(cli) -> None:
    result = cli("components", "string select")
    assert result.exit_code == 0
    assert "String Select" in result.stdout
    assert "3" in result.stdout


def test_cli_json_lookup(cli) -> None:
    payload = cli("--json", "components", "2").json
    assert payload["mode"] == "lookup"
    assert payload["name"] == "Button"
    assert payload["type"] == "2"
    assert payload["description"] == "Button object"
    assert payload["source"]["last_verified"]


def test_cli_json_lookup_includes_style_and_usage(cli) -> None:
    payload = cli("--json", "components", "2").json
    assert payload["style"] == "Interactive"
    assert payload["usage"] == "Message"


def test_cli_unknown_integer_exits_with_code_2(cli) -> None:
    result = cli("components", "99")
    assert result.exit_code == 2
    assert "unknown component type number: '99'" in result.stderr
    assert "run 'dkit components' to list every known component type" in result.stderr


def test_cli_unknown_name_with_suggestion(cli) -> None:
    result = cli("components", "Butto")
    assert result.exit_code == 2
    assert "unknown component type: 'Butto'" in result.stderr
    assert "did you mean" in result.stderr.lower()


def test_cli_unknown_name_no_suggestion(cli) -> None:
    result = cli("components", "xyzzy")
    assert result.exit_code == 2
    assert "unknown component type: 'xyzzy'" in result.stderr


@pytest.mark.parametrize(
    "argv",
    [("components", "-1"), ("components", "99999999999999999999")],
)
def test_cli_invalid_input_exits_with_code_2(cli, argv: tuple[str, ...]) -> None:
    result = cli(*argv)
    assert result.exit_code == 2
    assert result.stderr.startswith("error:")


def test_cli_strips_whitespace_on_input(cli) -> None:
    res_int = cli("components", "  2  ")
    assert res_int.exit_code == 0
    assert "Button" in res_int.stdout

    res_name = cli("components", "  Button  ")
    assert res_name.exit_code == 0
    assert "2" in res_name.stdout


def test_cli_render_one_shows_style_and_usage(cli) -> None:
    result = cli("components", "3")
    assert result.exit_code == 0
    assert "Interactive" in result.stdout
    assert "Message, Modal" in result.stdout


def test_cli_render_one_shows_style_and_usage(cli) -> None:
    result = cli("components", "1")

    assert result.exit_code == 0
    assert "Layout" in result.stdout
    assert "Message" in result.stdout

def test_cli_search_finds_matches(cli) -> None:
    result = cli("components", "--search", "interactive")

    assert result.exit_code == 0
    assert "Action Row" in result.stdout

def test_cli_search_empty_string(cli) -> None:
    result = cli("components", "--search", "")

    assert result.exit_code == 2
    assert "no search text given" in result.stderr

def test_cli_rejects_component_and_search_together(cli) -> None:
    result = cli(
        "components",
        "Button",
        "--search",
        "Interactive",
    )

    assert result.exit_code == 2
    assert "cannot be combined with --search" in result.stderr
