#!/usr/bin/env bash
# Regenerate the JSON Schema and JSON-LD context from the LinkML schema, fail
# if they differ from the committed copies, then validate every example record.
#
#   scripts/check.sh            check (CI)
#   scripts/check.sh --write    regenerate and overwrite schema/generated/
set -euo pipefail

LINKML="linkml==1.12.1"
cd "$(dirname "$0")/.."

SRC=schema/fdis_registry.yaml
OUT=schema/generated
JSON=fdis_registry.schema.json
CTX=fdis_registry.context.jsonld

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

uvx --quiet --from "$LINKML" gen-json-schema "$SRC" > "$tmp/$JSON"
# Record IDs expand under this base IRI in JSON-LD.
uvx --quiet --from "$LINKML" gen-jsonld-context --base https://w3id.org/perseus/registry/ "$SRC" > "$tmp/$CTX"

if [[ "${1:-}" == "--write" ]]; then
  mkdir -p "$OUT"
  cp "$tmp/$JSON" "$tmp/$CTX" "$OUT/"
  echo "wrote $OUT/$JSON and $OUT/$CTX"
else
  stale=0
  for f in "$JSON" "$CTX"; do
    if ! diff -u "$OUT/$f" "$tmp/$f"; then
      echo "STALE: $OUT/$f is out of date; run scripts/check.sh --write" >&2
      stale=1
    fi
  done
  [[ $stale -eq 0 ]] || exit 1
  echo "generated files are up to date"
fi

uv run --quiet --no-project --with jsonschema==4.23.0 --with pyyaml==6.0.2 \
  python scripts/validate_records.py "$OUT/$JSON" examples
