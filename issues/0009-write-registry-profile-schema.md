---
title: Write the FDIS Registry Profile v0.1 schema in LinkML
labels: [wayfinder:task]
parent: 1
blocked_by: []
assignee:
status: open
---

## Question

Build task (the map's execution override). Encode the decisions in the record-schemas ticket as a LinkML schema: five record types, inline person and link structures, Mentions, the `unconfirmed` marker, all vocabularies, and the schema.org/DataCite mappings from the prior-art ticket. Generate and commit the JSON Schema and JSON-LD context next to it, add a check that fails when they are out of date, and include one valid example record per type (e.g. O2-06, `landis-ii`, `treemap`, `uga`, a publication). Done when the examples validate against the generated JSON Schema.
