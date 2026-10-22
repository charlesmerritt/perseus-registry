---
title: What are the fields, identifiers, and controlled vocabularies for each record type?
labels: [wayfinder:grilling]
parent: 1
blocked_by: [2, 4, 5]
assignee: chazm
status: closed
---

## Question

Pin down the draft FDIS Registry Profile v0.1: required and optional fields for Research Project, Software, Dataset, Institution, and Publication; the ID scheme (keep tracker IDs like O2-06, use slugs like perseus:landis-ii-south, or both); controlled vocabularies (lifecycle status, mapped from the tracker's Current Phase values; publication status; roles; Integration Level); how a Dataset references a STAC Collection or Item; and the schema language (JSON Schema over YAML?).

## Resolution

The draft **FDIS Registry Profile v0.1**.

### Identifiers

- **Research Projects** use tracker-style IDs `O{objective}-{nn}` (e.g. `O2-06`), numbered in sequence within each Objective and assigned by the form when a record is created. **An ID never changes**, and numbers are never reused (O2-09, O2-13, O2-14 stay retired). If a project moves Objective it keeps its ID; `primary_task` says where it belongs now. The prefix records where the project started.
- **Software, Datasets, Institutions, Publications** use short readable slugs (`landis-ii`, `treemap`, `uga`, `daigneault-2026-scenarios`). Every reference names its type (`dataset: treemap`, `via: landis-ii`), so slugs never collide across types. Institutions also carry their ROR ID.
- In JSON-LD exports, IDs expand under a Perseus base URL.

### Schema language

**LinkML is the single source.** The JSON Schema (for forms and validation) and the JSON-LD context (mapping to schema.org/DataCite, per the prior-art ticket) are generated from it and **committed alongside it**. A check fails when the generated files are out of date.

### Vocabularies

- Research Project `status` (required): `proposed | active | paused | completed | superseded | archived`.
- Research Project `phase` (optional): `concept | development | validation | integration | operational`. Tracker mapping: Concept/Development → concept; Development → development; Testing/Validation → validation; Integration/Implementation → integration; Operational/Ongoing → operational (O2-16's double phase is resolved to one when seeding).
- Software `kind`: `model | tool | library`; `development_status`: repostatus.org values (via CodeMeta); `fdis_adapter`: `none | planned | in_progress | done`.
- Dataset `access`: `public | consortium | restricted`; `availability`: `planned | in_progress | published | withdrawn` (`planned` lets a project list outputs that don't exist yet).
- Publication `type`: `article | report | thesis | presentation | release | other`.
- Integration Level (from the relationship ticket): `n/a | informational | collaborative | integrated | discuss`.

### Fields (required in **bold**)

- **Research Project**: **id**, **title**, **summary**, **status**, **primary_task**, **leads** (≥1), **lead_institution**. Optional: `tracker_id`, `phase`, `supporting_tasks`, `collaborators`, `institutions[{id, role}]`, `inputs`, `outputs`, `depends_on`, `part_of`, `related_to`, `superseded_by`, `objective_integration`, `repositories`, `funding`, `links`. Prose sections: Overview, Goals and milestones, Needs from other Objectives, Integration notes, Methods.
- **Software**: **id**, **title**, **summary**, **kind**, **maintainers**, and a **repository or landing URL**. Optional: `version`, `license`, `languages`, `documentation`, `development_status`, `fdis_adapter`.
- **Dataset**: **id**, **source** (`stac: {collection, item?}` or `url` / `doi`), **access**, **availability**. Optional: `title` and `summary` (required only for external sources; STAC datasets fetch theirs at build time), `variables` (FDIS variable names, when those exist), `fdis_conformance`. "Produced by" and "used by" are generated, not stored.
- **Institution**: **id**, **name**. Optional: `short_name`, `ror`, `url`.
- **Publication**: **id**, **title**, **type**, **year**, and a **DOI or URL**. Optional: `authors`, `about` (links to projects, software, datasets; stored here, inverse generated).

### People

No Person record type. People are **inline entries** `{name, orcid?, institution, role?, unconfirmed?}`. ORCID is optional but encouraged; the form should offer **ORCID lookup** to fill in a person's details. Cross-record "everything X is on" uses ORCID when present, otherwise name matching. Revisit a Person type if the exercise shows name matching breaking down.

### Placeholder information

`unconfirmed: true` (with optional `note`) is allowed on any link, person entry, or Task alignment; records are confirmed by default. Together with Mentions, this deliberately lets contributors enter placeholder information and refine it later.
