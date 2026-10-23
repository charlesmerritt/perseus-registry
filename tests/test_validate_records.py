"""validate_records.py, run end to end on a records directory."""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from validate_records import main  # noqa: E402

SCHEMA = str(REPO / "schema/generated/fdis_registry.schema.json")
EXAMPLE = (REPO / "examples/research-project/RP-06.yaml").read_text()


def records(tmp_path, name, text):
    d = tmp_path / "research-project"
    d.mkdir()
    (d / name).write_text(text)
    return str(tmp_path)


def test_markdown_record_with_frontmatter_is_validated(tmp_path, capsys):
    root = records(tmp_path, "RP-06.md", f"---\n{EXAMPLE}---\n\n## Overview\n\nProse.\n")
    assert main(SCHEMA, root) == 0
    assert "ok   " in capsys.readouterr().out


def test_markdown_record_failing_the_schema_is_reported(tmp_path, capsys):
    root = records(tmp_path, "RP-06.md", "---\nid: RP-06\n---\n\nProse.\n")
    assert main(SCHEMA, root) == 1
    assert "FAIL" in capsys.readouterr().out


def test_markdown_record_id_must_match_file_name(tmp_path, capsys):
    root = records(tmp_path, "RP-07.md", f"---\n{EXAMPLE}---\n")
    assert main(SCHEMA, root) == 1
    assert "does not match file name" in capsys.readouterr().out


def test_markdown_without_frontmatter_is_reported_not_crashed(tmp_path, capsys):
    root = records(tmp_path, "RP-06.md", "## Overview\n\nNo record here.\n")
    assert main(SCHEMA, root) == 1
    assert "frontmatter" in capsys.readouterr().out
