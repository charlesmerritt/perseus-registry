---
title: Which tracker columns become registry fields, which become wiki prose, and which stay in the meeting tracker?
labels: [wayfinder:grilling]
parent: 1
blocked_by: []
assignee: chazm
status: closed
---

## Question

The Obj 2 tracker (`sources/objective2-tracker.csv`) mixes durable facts (what the project is, leads, institutions, Task, dependencies, Integration Levels) with meeting logistics (PI Ambassador, Presentation Status/Month, dated 9/17 updates, Discussion/Decision Needed). Decide, column by column, whether each becomes a structured registry field, a narrative wiki section, or stays out of the registry. Also decide whether the registry replaces the tracker or sits beside it.

## Resolution

**The registry stands alone; the tracker is only a seed source.** The Obj 2 tracker is a coordination artifact outside this effort. Records are seeded from it once, its meeting-logistics columns are simply not imported, and nothing in the registry depends on the tracker continuing to exist.

Column mapping (from `sources/objective2-tracker.csv`):

| Becomes | Columns |
|---|---|
| Structured field | Project ID · Project/Workstream (title) · Primary Task · Secondary/Supporting Tasks · Current Phase (becomes lifecycle status) · Lead(s) · Collaborators/Institutions · Obj. 1/3/4 Integration · Depends On + Provides To (one link seen from both ends; representation decided in the relationship ticket) |
| Wiki prose section | What the Project Is (Overview) · Needs from Other Objectives · Integration/Dependency Notes |
| Not imported | PI Ambassador · Current Update · Next Milestone · Discussion/Decision Needed · Presentation Status · Presentation Month |
| Generated | Last Updated (from git history) |

Further decisions:

- **Summary**: every Research Project has a required one-to-two sentence `summary` for directory cards and exports. The tracker's "What the Project Is" text becomes the page's Overview section.
- **Goals and milestones**: an optional free-text section for durable aims (e.g. "paper on GA/IN expansion"). No dated, month-by-month updates.
- **PI Ambassador** is dropped from Research Projects. It is a PI-level role that belongs to a higher-order Objective/Task structure (Objectives and Tasks come from fixed consortium documentation and may carry their own leads), to be filled in later.
- **Uncertainty is explicit**: structured entries can carry a visible "unconfirmed" marker rather than being omitted or hidden in prose (cf. Integration Level `Discuss`). Applies to links, roles, and Task alignment.
