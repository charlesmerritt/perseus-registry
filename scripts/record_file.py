"""Read one Registry Record file.

A record is either <id>.yaml (fields only) or <id>.md: YAML frontmatter
between `---` lines, then the record's prose as a Markdown body.
"""

import re
from pathlib import Path

import yaml

FRONTMATTER = re.compile(r"---\n(.*?)^---\n(.*)", re.M | re.S)


def read_record(path: Path) -> tuple[object, str]:
    """Return (record, prose body). The body is "" for a .yaml file."""
    text = Path(path).read_text()
    if Path(path).suffix != ".md":
        return yaml.safe_load(text), ""
    m = FRONTMATTER.match(text)
    if not m:
        raise ValueError(f"{path}: a record .md file must start with YAML frontmatter between --- lines")
    return yaml.safe_load(m[1]), m[2].lstrip("\n")
