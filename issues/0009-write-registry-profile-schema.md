---
title: Write the FDIS Registry Profile v0.1 schema in LinkML
labels: [wayfinder:task]
parent: 1
blocked_by: []
assignee: claude (background agent)
status: closed
---

## Question

Build task (the map's execution override). Encode the decisions in the record-schemas ticket as a LinkML schema: five record types, inline person and link structures, Mentions, the `unconfirmed` marker, all vocabularies, and the schema.org/DataCite mappings from the prior-art ticket. Generate and commit the JSON Schema and JSON-LD context next to it, add a check that fails when they are out of date, and include one valid example record per type (e.g. O2-06, `landis-ii`, `treemap`, `uga`, a publication). Done when the examples validate against the generated JSON Schema.

## Resolution

Done, merged to main from `task/registry-profile-schema`. `scripts/check.sh` passes: generated files are up to date and all five examples validate (`scripts/check.sh --write` regenerates). See `schema/README.md`.

- `schema/fdis_registry.yaml` (LinkML source); `schema/generated/fdis_registry.schema.json` and `fdis_registry.context.jsonld` (generated, committed). LinkML pinned to 1.12.1, run via `uvx`.
- `examples/<type>/<id>.yaml`: the directory gives the record type, each file is validated against `$defs/<Class>`, and `id` must match the filename.

Implementation decisions (for user review):

1. **Uniform link shape**: every link is an object with a typed key (`{dataset: treemap, via?, unconfirmed?, note?}`), including `lead_institution`, `primary_task`, `part_of`, `superseded_by`, so any of them can be unconfirmed. Any target can be an ID or a Mention. `institutions` entries use `institution:` rather than the spec's `id:`.
2. Dataset `source` is exactly one of `stac {collection, item?}`, `url`, `doi`.
3. Not enforceable in the JSON Schema (left to the form/build): title and summary required for external Datasets; cross-record reference integrity; omitting the project's own Objective from `objective_integration`.
4. Person and institution `role` are free text (no vocabulary yet). Task pattern `^[1-4]\.\d+$`.
5. `objective_integration` keys are strings "1"–"4". JSON-LD base `https://w3id.org/perseus/registry/` is a **placeholder**. DataCite mappings recorded as exact/close/related mappings.
6. Example content: UGA ROR `00te3t702` verified against the ROR API; LANDIS-II URLs unverified.
