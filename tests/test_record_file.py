"""read_record: one reader for every Registry Record file."""

import sys

import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from record_file import read_record  # noqa: E402


def test_markdown_file_gives_frontmatter_record_and_prose_body(tmp_path):
    f = tmp_path / "RP-06.md"
    f.write_text("---\nid: RP-06\ntitle: LANDIS-II\n---\n\n## Overview\n\nAdapts LANDIS-II.\n")
    record, body = read_record(f)
    assert record == {"id": "RP-06", "title": "LANDIS-II"}
    assert body == "## Overview\n\nAdapts LANDIS-II.\n"


def test_yaml_file_has_no_prose(tmp_path):
    f = tmp_path / "treemap.yaml"
    f.write_text("id: treemap\ntitle: TreeMap 2022\n")
    assert read_record(f) == ({"id": "treemap", "title": "TreeMap 2022"}, "")


def test_markdown_file_without_frontmatter_is_rejected(tmp_path):
    f = tmp_path / "RP-06.md"
    f.write_text("## Overview\n\nProse only, no record.\n")
    with pytest.raises(ValueError, match="frontmatter"):
        read_record(f)


def test_only_whole_dash_lines_delimit_frontmatter(tmp_path):
    f = tmp_path / "RP-06.md"
    f.write_text("---\nid: RP-06\ntitle: Before---\nstatus: active\n---\n\nAbove a rule.\n\n---\n\nBelow it.\n")
    record, body = read_record(f)
    assert record == {"id": "RP-06", "title": "Before---", "status": "active"}
    assert body == "Above a rule.\n\n---\n\nBelow it.\n"
