"""``dkit components`` - look up Discord Component types."""

from __future__ import annotations

import argparse
from typing import Any

from dkit.core import data
from dkit.core.errors import UsageError
from dkit.core.output import Printer
from dkit.core.parse import looks_like_int, normalise_name, parse_int
from dkit.core.registry import Command
from dkit.core.suggest import suggestion_hint

DESCRIPTION = """\
Look up Discord component types by type number or name, or list every known
component type.
"""

HINT_ALL = "run 'dkit components' to list every known component type"


def component_types() -> list[dict[str, str]]:
    """Return component types from ``dkit/data/component_types.json``."""
    components = data.load("component_types")

    return [
        {
            "type": component_type["type"],
            "name": component_type["name"],
            "description": component_type["description"],
            "style": component_type.get("style", ""),
            "usage": component_type.get("Usage", component_type.get("usage", "")),
        }
        for component_type in components["types"]
    ]


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Register the arguments of ``dkit components``."""
    parser.add_argument(
        "value",
        metavar="TYPE",
        nargs="?",
        help="a component type number (e.g. 2) or name (e.g. Button)",
    )


def run(args: argparse.Namespace, out: Printer) -> dict[str, Any]:
    """Execute ``dkit components``."""
    entries = component_types()

    if args.value is None:
        _render_all(out, entries)
        return {
            "mode": "all",
            "count": len(entries),
            "component_types": [dict(entry) for entry in entries],
            "source": data.provenance("component_types"),
        }

    raw = args.value.strip()
    if looks_like_int(raw):
        int_val = parse_int(raw, what="component type")
        str_val = str(int_val)
        for entry in entries:
            if entry["type"] == str_val:
                _render_one(out, entry)
                return {
                    "mode": "lookup",
                    **entry,
                    "source": data.provenance("component_types"),
                }
        raise UsageError(
            f"unknown component type number: {raw!r}",
            hint=HINT_ALL,
        )

    norm = normalise_name(raw)
    for entry in entries:
        if normalise_name(entry["name"]) == norm:
            _render_one(out, entry)
            return {
                "mode": "lookup",
                **entry,
                "source": data.provenance("component_types"),
            }

    known_names = [entry["name"] for entry in entries]
    hint = suggestion_hint(norm, [normalise_name(n) for n in known_names]) or HINT_ALL
    raise UsageError(f"unknown component type: {raw!r}", hint=hint)


def _render_one(out: Printer, entry: dict[str, str]) -> None:
    """Render a single component type."""
    out.heading("Component type")
    out.field("Type", out.style(entry["type"], "green", "bold"))
    out.field("Name", entry["name"])
    out.field("Description", entry["description"])
    if entry.get("style"):
        out.field("Style", entry["style"])
    if entry.get("usage"):
        out.field("Usage", entry["usage"])


def _render_all(out: Printer, entries: list[dict[str, str]]) -> None:
    """Render every component type in tabular form."""
    out.heading(f"Component types ({len(entries)})")
    type_width = max((len(entry["type"]) for entry in entries), default=0)
    name_width = max((len(entry["name"]) for entry in entries), default=0)
    for entry in entries:
        type_str = entry["type"].rjust(type_width)
        name = entry["name"]
        padding = " " * (name_width - len(name))
        styled_name = out.style(name, "green")
        out.line(f"  {type_str}  {styled_name}{padding}  {entry['description']}")


COMMAND = Command(
    name="components",
    help="look up Discord component types",
    description=DESCRIPTION,
    add_arguments=add_arguments,
    run=run,
    epilog=("examples:\n  dkit components\n  dkit components 1\n  dkit components 'Action Row'\n"),
)
