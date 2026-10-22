---
title: Which existing metadata standards should the registry borrow its vocabulary from?
labels: [wayfinder:research]
parent: 1
blocked_by: []
assignee: claude (research subagent)
status: closed
---

## Question

Survey CodeMeta, DataCite relation types, schema.org (ResearchProject, SoftwareSourceCode, Dataset), RO-Crate, Backstage's entity model, and the STAC scientific/citation extensions. For each: which entity types and relationship terms (e.g. isDerivedFrom, uses, produces, isSupplementTo, dependsOn) map onto Research Project, Software, Dataset, Institution, Publication, and the tracker's Depends On / Provides To and Integration Level columns. Recommend the smallest borrowed vocabulary that keeps records interoperable and portable; note anything that must be Perseus-specific.

## Context

Findings: branch `research/relationship-vocabulary-prior-art`, file `research/relationship-vocabulary-prior-art.md`.

## Resolution

Borrow **types and JSON-LD shape from schema.org** and **relation semantics from DataCite 4.6**; a schema.org export is then also valid CodeMeta / RO-Crate.

- Types: Research Project → `ResearchProject` / DataCite `Project`; Software (all kinds) → `SoftwareSourceCode` / `Software` (DataCite `Model` means a conceptual model, not code); Dataset → `Dataset`; Institution → `Organization` with ROR ID; Publication → `ScholarlyArticle` with DOI.
- Seven borrowed relations, each stored on one record with its inverse generated (Backstage pattern): `partOf`, Software `producer` → Project, `requires`, Dataset `compiledBy` Software, `derivedFrom`, Publication `about`, `obsoletes`.
- Institutions as `lead` / `collaborators` role fields; STAC pointer as a field exporting to DataCite `HasMetadata`; Software lifecycle from CodeMeta `developmentStatus`.
- Perseus-specific (no standard term fits): Project `dependsOn` Project (the tracker's Depends On / Provides To are one edge seen from both ends; store once with optional `via` Dataset/Software); Project `uses` Software; Integration Level per Objective; primary vs supporting Task; references to unregistered things ("FIA", "Obj 3 survey results"); project lifecycle values; the `perseus:` ID base address.
