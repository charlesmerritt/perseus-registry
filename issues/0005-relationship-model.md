---
title: How are relationships between records represented, and which record owns each link?
labels: [wayfinder:grilling]
parent: 1
blocked_by: [3, 4]
assignee: chazm
status: closed
---

## Question

Decide whether links are embedded in records (a Research Project lists its Software and Datasets; Software lists what it consumes and produces) or held as separate relationship records; which side is authoritative for each link type, with the inverse generated statically; the relation vocabulary (from the prior-art ticket); how Integration Level per Objective is modelled; and how a link to a not-yet-registered thing (e.g. 'Objective 3 survey results', 'FIA') is represented. Test against tracker rows such as O2-04 → O2-01/O2-05 and O2-16 → many.

## Resolution

Links are **embedded in records**, each stored on exactly one owning record; every inverse ("used by", "provides to", "produced by") is generated statically at build time (Backstage pattern, per the prior-art ticket).

- **Inputs and outputs live on the Research Project.** Each entry names a Dataset and may name the Software that consumes or produces it (`via`). Software records describe general capabilities in prose and do not list concrete inputs and outputs; "Software used by Project X" is generated.
  ```yaml
  inputs:
    - dataset: perseus:treemap
  outputs:
    - dataset: perseus:landis-south-projections
      via: perseus:landis-ii
  ```
- **Project-to-project dependencies come from both sources.** They are generated where one project's output Dataset is another's input, and can also be declared explicitly on the downstream project (`depends_on`, with a short note) for looser links. "Provides to" is always generated. A declared link can be dropped once a matching Dataset makes it redundant.
- **A Dataset points at one authoritative source**: a D2S STAC Collection or Item (preferred for spatial data the consortium produces) *or* an external landing page or DOI (e.g. FIA DataMart). Supersedes the glossary's earlier "exactly one STAC reference".
- **Mentions** of not-yet-registered things are allowed anywhere a link can go: `{name: "Obj 3 landowner typologies", unconfirmed: true}`. The site lists all unregistered mentions so they can be promoted to records.
- **Project-to-project relation set**: `depends_on`, `part_of` (sub-project), `superseded_by` (retired records stay, so IDs never break; e.g. O2-17 into O2-16), and a weak `related_to` with a note.
- **Integration Level** is a map on the Research Project keyed by Objective, each with `level` and an optional `note`. The project's own Objective (from its primary Task) is omitted; `discuss` acts as the unconfirmed marker.
  ```yaml
  objective_integration:
    1: { level: integrated, note: "wall-to-wall forest data" }
    3: { level: collaborative }
  ```
