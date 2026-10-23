"""Turn a 'submission' issue body into Registry Record files.

The submission form (site/assets/form.js) writes each file as its path in
backticks on its own line, then the file's text in a fenced code block.

Usage: submission.py [--new] BODY_FILE
    Write each file under the current directory. With --new (a "New ..."
    submission), refuse to overwrite an existing record: another submission
    may already have taken the ID the form assigned.
"""

import re
import sys
from pathlib import Path

FILE = re.compile(r"^`([^`\n]+)`\n+(`{3,})[^\n]*\n(.*?)^\2$", re.M | re.S)
# Issue bodies are untrusted: only ever write records/<type>/<id>.md|yaml.
RECORD_PATH = re.compile(
    r"records/(research-project|software|dataset|institution|publication)/[A-Za-z0-9][A-Za-z0-9_-]*\.(md|yaml)"
)


def files_from_issue(body: str) -> list[tuple[str, str]]:
    """Return [(path, text)] for each file in the issue body."""
    body = body.replace("\r\n", "\n")  # GitHub stores issue bodies with CRLF
    files = [(m[1], m[3]) for m in FILE.finditer(body)]
    if not files:
        raise ValueError("no record file found in the issue body")
    for path, _ in files:
        if not RECORD_PATH.fullmatch(path):
            raise ValueError(f"{path!r} is not a record file path (records/<type>/<id>.md or .yaml)")
    return files


if __name__ == "__main__":
    args = sys.argv[1:]
    new = args[:1] == ["--new"]
    if len(args) != 1 + new:
        print(__doc__)
        sys.exit(2)
    try:
        files = files_from_issue(Path(args[-1]).read_text())
    except ValueError as ex:
        print(ex)
        sys.exit(1)
    taken = [path for path, _ in files if new and Path(path).exists()]
    if taken:
        print(f"{', '.join(taken)} already exists: give the new record the next free ID")
        sys.exit(1)
    for path, text in files:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
        print(path)
