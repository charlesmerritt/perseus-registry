"""files_from_issue: a 'submission' issue body, as the form writes it, into record files."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from submission import files_from_issue  # noqa: E402

RECORD = "---\nid: RP-18\ntitle: Fire regimes\n---\n\n## Overview\n\nNew work.\n"


def issue(path, text, fence="```"):
    return f"`{path}`\n\n{fence}markdown\n{text}{fence}\n"


def test_issue_with_one_record_gives_that_file():
    body = issue("records/research-project/RP-18.md", RECORD)
    assert files_from_issue(body) == [("records/research-project/RP-18.md", RECORD)]


def test_windows_line_endings_from_github_become_unix():
    body = issue("records/research-project/RP-18.md", RECORD).replace("\n", "\r\n")
    assert files_from_issue(body) == [("records/research-project/RP-18.md", RECORD)]


def test_prose_containing_a_code_fence_survives_a_longer_outer_fence():
    text = RECORD + "\n## Methods\n\n```r\nfit <- lm(y ~ x)\n```\n"
    body = issue("records/research-project/RP-18.md", text, fence="````")
    assert files_from_issue(body) == [("records/research-project/RP-18.md", text)]


@pytest.mark.parametrize("path", [
    ".github/workflows/ci.yml",
    "records/research-project/../../scripts/check.sh",
    "records/research-project/RP-18.sh",
    "records/widgets/RP-18.md",
    "/records/research-project/RP-18.md",
    "records/research-project/sub/RP-18.md",
])
def test_paths_outside_a_record_type_directory_are_rejected(path):
    with pytest.raises(ValueError, match="not a record file"):
        files_from_issue(issue(path, RECORD))


def test_issue_without_any_file_is_rejected():
    with pytest.raises(ValueError, match="no record file"):
        files_from_issue("Please add my project, details below.")
