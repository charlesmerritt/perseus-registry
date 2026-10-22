"""Validate Registry Record YAML files against the generated JSON Schema.

The record class comes from the file's parent directory name
(research-project/O2-06.yaml -> ResearchProject). Each file is validated
against that class's definition in schema/generated/fdis_registry.schema.json,
and its `id` must match the file name.

Usage: validate_records.py SCHEMA_JSON DIR [DIR ...]
"""

import json
import sys
from pathlib import Path

import jsonschema
import yaml

CLASS_BY_DIR = {
    "research-project": "ResearchProject",
    "software": "Software",
    "dataset": "Dataset",
    "institution": "Institution",
    "publication": "Publication",
}


def main(schema_path: str, *dirs: str) -> int:
    schema = json.loads(Path(schema_path).read_text())
    failures = 0
    files = sorted(f for d in dirs for f in Path(d).rglob("*.y*ml"))
    if not files:
        print(f"no YAML files found in {', '.join(dirs)}")
        return 1
    for path in files:
        cls = CLASS_BY_DIR.get(path.parent.name)
        if cls is None:
            print(f"FAIL {path}: directory must be one of {sorted(CLASS_BY_DIR)}")
            failures += 1
            continue
        # Validate the JSON form of the record (YAML int keys become strings,
        # dates become ISO strings), which is what forms and JSON-LD see.
        record = json.loads(json.dumps(yaml.safe_load(path.read_text()), default=str))
        validator = jsonschema.Draft201909Validator(
            {"$ref": f"#/$defs/{cls}", "$defs": schema["$defs"]}
        )
        errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        if isinstance(record, dict) and record.get("id") != path.stem:
            errors.append(f"id {record.get('id')!r} does not match file name {path.stem!r}")
        if errors:
            failures += 1
            print(f"FAIL {path} ({cls})")
            for e in errors:
                if isinstance(e, str):
                    print(f"  - {e}")
                else:
                    loc = "/".join(str(p) for p in e.absolute_path) or "(record)"
                    print(f"  - {loc}: {e.message}")
        else:
            print(f"ok   {path} ({cls})")
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
