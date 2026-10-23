---
title: Seed the Objective 2 records from the tracker
labels: [wayfinder:task]
parent: 1
blocked_by: [9]
assignee: claude
status: open
---

## Question

Build task. Convert each row of `sources/objective2-tracker.csv` into a Research Project record using the column mapping from the tracker-boundary ticket, and create the Software, Dataset, and Institution records those rows reference (real D2S STAC IDs from the STAC survey ticket, e.g. TreeMap `f8934dd1-…`). Anything the tracker hedges ("to confirm", "not defined") becomes `unconfirmed: true` or a Mention, not a guess. Every record must validate. List the judgment calls made (e.g. O2-16's double phase, people vs institutions in the Collaborators column) for the user to review.
