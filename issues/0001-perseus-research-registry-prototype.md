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
- **GUI first** (user direction, while working on the relationship ticket): contributors create and edit records through fillable forms in the app, or upload a YAML file that conforms to the official schema. YAML is the storage and interchange format underneath, never something contributors are required to write. Contributors may not use Git.
- D2S STAC (`stac.d2s.org/api/v1/`) is read-only and authoritative for spatial dataset metadata.
- Skills to consult: `grilling` and `domain-modeling` for grilling tickets; `prototype` for prototype tickets.

## Decisions so far

- Destination is a working prototype, not just a spec; YAML in Git; local markdown tracker; D2S STAC is read-only; FDIS Core is referenced only by version string (decided while charting).
- [What does the D2S STAC catalog actually contain and expose?](0002-d2s-stac-catalog-survey.md): public, CORS-open, fast enough to fetch at build time; IDs are UUIDs or slugs; TreeMap, biomass, and LiDAR exist; metadata is thin; keep a cached snapshot.
- [Which existing metadata standards should the registry borrow its vocabulary from?](0003-relationship-vocabulary-prior-art.md): schema.org types + DataCite 4.6 relations (7 borrowed, inverses generated); Project dependsOn/uses, Integration Level, Tasks, and unregistered targets are Perseus-specific.
- [Which tracker columns become registry fields, which become wiki prose, and which stay in the meeting tracker?](0004-tracker-vs-registry-boundary.md): registry stands alone and the tracker is only a seed; durable columns become fields or prose and meeting logistics aren't imported; PI Ambassador is dropped (moves to the Objective/Task level); unconfirmed facts get an explicit marker.
- [How are relationships between records represented, and which record owns each link?](0005-relationship-model.md): links embedded on one owning record, inverses generated; inputs/outputs on the Research Project (optional `via` Software); dependencies generated from matching datasets plus declared ones; Datasets may point at STAC or an external source; Mentions for unregistered things; Integration Level is a per-Objective map.
- [What are the fields, identifiers, and controlled vocabularies for each record type?](0006-record-schemas-and-ids.md): project IDs `O2-06` style (never change; **amended**: neutral `RP-06`, tracker ID kept as `tracker_id`), slugs for other types; LinkML source with committed JSON Schema + JSON-LD; status vs phase; people inline with ORCID; `unconfirmed` marker allows placeholders.
- [Write the FDIS Registry Profile v0.1 schema in LinkML](0009-write-registry-profile-schema.md): done; `schema/` + `examples/` + `scripts/check.sh` pass. Uniform link objects (any target may be a Mention); some rules left to the form/build; JSON-LD base URL is a placeholder.
- [Seed the Objective 2 records from the tracker](0010-seed-objective-2-records.md): done; 27 records in `records/` (14 projects, 3 institutions, 8 datasets, 2 software), all validated; prose in sibling `.md`; most affiliations and lead institutions are unconfirmed guesses awaiting review.
- [What should the static wiki look like, and what generates it?](0007-wiki-stack-and-page-layout.md): a small Python generator, not MkDocs; directory is a sortable table plus a by-Objective outline page; Research Project pages are a wiki article with an infobox; prose in a sidecar `<id>.md` (**amended** by 0008: one `<id>.md` with YAML frontmatter).
- [How does a non-Git contributor submit or update a record?](0008-contributor-submission-flow.md): a step-wizard form validates in the browser and opens a GitHub issue; a coordinator labels it `approved` and an Action re-validates it and opens a PR. Contributors need a GitHub account, not Git. A Research Project is one `<id>.md` with YAML frontmatter. The repo remote and labels are still to set up.
- Canonical terms: **Research Project** (not "project"/"workstream"), **Software** with `kind: model | tool | library` (see `CONTEXT.md`).

## Not yet specified

- **Build-out**: the site generator, form and submission flow are built (0007, 0008), and CI validates every push. Still open: creating the GitHub remote and publishing the built site (see Hosting and handoff).
- **Public vs internal information**: the tracker has internal notes ("Discussion needed", status confirmations). Do some fields stay off a public site, or is the whole wiki consortium-internal?
- **Objective and Task structure**: the fixed Objectives (1 Measurement, 2 Modeling, 3 Management, 4 Mindset) and their numbered Tasks come from consortium documentation not yet in the repo. They likely become higher-order records or pages with their own PI leads (where PI Ambassadors land). Only Obj 2 has a project list; do Objectives 1, 3, 4 get placeholder pages in the prototype? User will supply the documentation later.
- **Versioning**: Software versions, model runs, dataset releases. How much does a prototype need?
- **Hosting and handoff**: where the demo site lives (GitHub Pages?) and who maintains it afterward.

## Out of scope

- Dynamic or computational features: live queries, graph analytics, a search backend (user direction while charting).
- Writing to D2S STAC or publishing model outputs automatically (stage 2 of the original proposal).
- Authentication and permissions beyond what the chosen submission flow strictly needs.
- Drafting FDIS Core or the FDIS Publication Profile.
