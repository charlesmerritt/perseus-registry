---
title: Seed the Objective 2 records from the tracker
labels: [wayfinder:task]
parent: 1
blocked_by: [9]
assignee: claude
status: closed
---

## Question

Build task. Convert each row of `sources/objective2-tracker.csv` into a Research Project record using the column mapping from the tracker-boundary ticket, and create the Software, Dataset, and Institution records those rows reference (real D2S STAC IDs from the STAC survey ticket, e.g. TreeMap `f8934dd1-…`). Anything the tracker hedges ("to confirm", "not defined") becomes `unconfirmed: true` or a Mention, not a guess. Every record must validate. List the judgment calls made (e.g. O2-16's double phase, people vs institutions in the Collaborators column) for the user to review.

## Resolution

Done. `records/` holds 27 records, all validated by `scripts/check.sh`, which now checks `records/` as well as `examples/`. Every ID reference resolves to a record. See `records/README.md` for the seeding conventions.

- **14 Research Projects**: O2-01 to O2-08, O2-10 to O2-12, and O2-15 to O2-17. The prose columns are in a sibling `<id>.md`.
- **3 Institutions**: `uga`, `umaine`, `purdue`. ROR IDs were checked against the ROR API; Purdue uses the West Lafayette campus ID `02dqehb95`.
- **8 Datasets**: `fia` (external, FIA DataMart), plus seven STAC Datasets checked live: `treemap`, `maine-biomass-2023`, `howland-biomass`, `bigmap`, `indiana-lidar-point-cloud`, `indiana-lidar-ndhm`, `3dep`.
- **2 Software**: `landis-ii` (from the examples) and `d2s` (Data to Science, gdslab).

Judgment calls (for user review):

1. **Prose storage**: each project's prose sections are in a sibling `records/research-project/<id>.md` with `## Overview`, `## Needs from other Objectives`, `## Integration notes`. The schema left the format of the "Markdown body" open, so this choice feeds the wiki-stack ticket. Next Milestone was not imported (per the boundary ticket), so no "Goals and milestones" section was written. That loses durable aims such as O2-03's "paper goal end of fall 2026".
2. **Affiliations**: the tracker rarely states one. An affiliation counts as stated only when the row says so: O2-01 and O2-05/07 for Maine, O2-03 and O2-08 for UGA, O2-12 for Purdue, and Bahaa Alaila and Shishir Lohar at UGA. Every other person has a best-guess institution and `unconfirmed: true`. Evan Salcido, Mahesh Tiwari and Victor Chen had no basis for a guess, so their institution is the Mention `Not stated`. "K. Legaard" (O2-16) is entered with only the initial the tracker gives.
3. **Collaborators column, people vs institutions**: named people became `collaborators`. Team phrases ("UGA and Purdue modeling collaborators", "Purdue and Maine forest-health teams") became `institutions` entries. Groups that are not institutions ("visualization collaborators", "Objective 1 data-coverage team", "destination platform owners") went into the prose. "UGA interns" in O2-15's Leads became a note on the UGA institution entry.
4. **Lead institution**: the tracker never names one. It was inferred from the leads, and marked unconfirmed wherever the leads span institutions or their affiliations are guessed (O2-04, O2-06, O2-10, O2-11, O2-15, O2-16, O2-17).
5. **Phase and status**: O2-16's double phase resolved to `operational` (the STAC is active). O2-12 is `paused` (paused for fall). Everything else is `active`, including O2-02 (concept but actively worked on, with "confirm if this should be included") and O2-11 ("status unknown").
6. **O2-17 primary Task** is `1.3`, unconfirmed, and keeps its O2 ID. Its own Objective therefore becomes 1, so `objective_integration` lists Objective 2 (integrated) and drops Objective 1. The proposed merge into O2-16 is a `related_to` with unconfirmed, not `superseded_by`, because the tracker phrases it as a question.
7. **Dependencies**: each Provides To edge was turned into a `depends_on` on the downstream project, then combined with the declared Depends On (e.g. O2-07 depends on O2-01, O2-04, O2-05; O2-15 on ten projects). One-sided "potentially" edges are unconfirmed (O2-15 to O2-02, O2-08 to O2-11). O2-04's "O2-05–O2-08 and O2-10–O2-12" was expanded, skipping the retired O2-09. The CSV has mojibake for the dashes there.
8. **STAC mapping for O2-16**: the tracker's generic "LiDAR" and "biomass" were mapped to the STAC survey's collections. Each of these inputs is unconfirmed with a note. The D2S STAC catalog is linked as O2-16's STAC repository (also unconfirmed).
9. **Hedges in Discussion/Decision Needed** (a column that is not imported) were still used to set `unconfirmed` markers: O2-10 and O2-11 primary Tasks, O2-04's lead, O2-07's dashboard relation to O2-15, O2-01 to O2-02.
10. **Software as Mentions**: the Harvest Choice Model, MIFSM, the UGA Timber Supply Model, FVS and Woodstock have no URL or repository, which a Software record requires. They are Mentions on `via`. O2-07 lists `fia` four times, once per model, so that every model shows up as software used.
11. **Not registered**: "2-13A" (O2-16's Current Update) and PSAE/Areal. PSAE/Areal is a `related_to` Mention on O2-16. Publications ("manuscript submitted", "publication accepted") have no DOI or URL in the tracker, so no Publication records were created.
12. **Examples unchanged**: `examples/` is left as is. `records/research-project/O2-06.yaml` revises the example: Purdue and Maine are now registered Institutions, and affiliations follow rule 2.
