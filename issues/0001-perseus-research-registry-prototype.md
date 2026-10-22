---
title: Perseus research registry prototype
labels: [wayfinder:map]
status: open
---

## Destination

A demonstrable prototype of the Perseus research registry: a **static wiki** generated from portable, schema-validated YAML records (the draft **FDIS Registry Profile v0.1**), seeded with the real Objective 2 projects from the tracker, with D2S STAC datasets linked rather than copied. It should be good enough to show the consortium how it would work, and to run the exercise where each institution submits one project, one Software record, and one Dataset.

## Notes

- Domain: multi-institutional forest research (Perseus: Objectives 1 Measurement, 2 Modeling, 3 Management, 4 Mindset). Glossary in `CONTEXT.md`; use its terms.
- Source data: `sources/objective2-tracker.csv` (Obj 2 tracker, ~14 Research Projects with O2-xx IDs).
- **Execution override**: this map carries through to *building* the prototype. Once the decisions are clear, build tickets graduate from the fog.
- Standing preferences: a wiki plus data standards for cross-project and cross-institution collaboration and ease of use downstream, *not* a dynamic or computational app. Anything derived (backlinks, "used by" lists) is generated statically at build time. Portability matters most: the records must stay usable without the site.
- Contributors may not use Git: provide copyable templates; a coordinator merges.
- D2S STAC (`stac.d2s.org/api/v1/`) is read-only and authoritative for spatial dataset metadata.
- Skills to consult: `grilling` and `domain-modeling` for grilling tickets; `prototype` for prototype tickets.

## Decisions so far

- Destination is a working prototype, not just a spec; YAML in Git; local markdown tracker; D2S STAC is read-only; FDIS Core is referenced only by version string (decided while charting).
- Canonical terms: **Research Project** (not "project"/"workstream"), **Software** with `kind: model | tool | library` (see `CONTEXT.md`).

## Not yet specified

- **Build-out**: the generator, seeding records from the tracker, and CI validation. Graduates once the schema and site stack are decided.
- **Public vs internal information**: the tracker has internal notes ("Discussion needed", status confirmations). Do some fields stay off a public site, or is the whole wiki consortium-internal?
- **Objectives 1, 3, 4**: only Obj 2 has a tracker. Do the others have equivalent lists, and should the prototype include placeholder pages for them?
- **People**: are researchers records of their own (with ORCID), or names on Research Projects? Hangs on the relationship model.
- **Versioning**: Software versions, model runs, dataset releases. How much does a prototype need?
- **Hosting and handoff**: where the demo site lives (GitHub Pages?) and who maintains it afterward.

## Out of scope

- Dynamic or computational features: live queries, graph analytics, a search backend (user direction while charting).
- Writing to D2S STAC or publishing model outputs automatically (stage 2 of the original proposal).
- A browser editor backed by a database; authentication and permissions.
- Drafting FDIS Core or the FDIS Publication Profile.
