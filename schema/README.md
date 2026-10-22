# FDIS Registry Profile v0.1 schema

`fdis_registry.yaml` is the **single source** for the Registry Profile, written in [LinkML](https://linkml.io). It defines the five record classes (`ResearchProject`, `Software`, `Dataset`, `Institution`, `Publication`), the inline structures they use (person entries, links, Mentions, Dataset sources, Task alignments, `objective_integration`), every controlled vocabulary, and the mappings to schema.org and DataCite 4.6.

Prose sections (for example a Research Project's Overview or Methods) are not schema fields. They live in a record's Markdown body.

## Files

| Path | What it is |
|---|---|
| `fdis_registry.yaml` | The LinkML schema. Edit this one. |
| `generated/fdis_registry.schema.json` | JSON Schema (draft 2019-09) from `gen-json-schema`. Used by forms and validation. Do not edit. |
| `generated/fdis_registry.context.jsonld` | JSON-LD context from `gen-jsonld-context`. Record IDs expand under `https://w3id.org/perseus/registry/`. Do not edit. |
| `../examples/<type>/<id>.yaml` | One valid example record per type. |
| `../scripts/check.sh` | Regenerates the files above, fails if they are stale, and validates the examples. |
| `../scripts/validate_records.py` | Validates record files against one class of the JSON Schema. |

## Regenerate

```sh
scripts/check.sh --write
```

Needs only [uv](https://docs.astral.sh/uv/). The LinkML version is pinned in `scripts/check.sh`. Commit the regenerated files together with the schema change.

## Validate

```sh
scripts/check.sh
```

This fails if `generated/` differs from what the schema produces, then validates every file under `examples/`.

A record file holds one record, and its type comes from its directory: `research-project/`, `software/`, `dataset/`, `institution/` or `publication/`. The validator checks each file against that class's definition (`$defs/<Class>`) in the single generated JSON Schema. It also checks that the record's `id` matches the file name. To validate other records:

```sh
uv run --no-project --with jsonschema --with pyyaml \
  python scripts/validate_records.py schema/generated/fdis_registry.schema.json path/to/records
```

## What the JSON Schema does not enforce

- A Dataset with an external (`url` or `doi`) source must have `title` and `summary`. LinkML 1.12 cannot express this condition in JSON Schema, so the form and site build must check it.
- References between records (e.g. that `dataset: treemap` names a registered Dataset) are not checked here. The site build checks them.
- The `objective_integration` map should omit the project's own Objective. This is not checked.
