---
title: How does a non-Git contributor submit or update a record?
labels: [wayfinder:prototype]
parent: 1
blocked_by: [6]
assignee: chazm
status: open
---

## Question

How does a contributor create or update a record without touching Git or YAML? Direction from the user: **GUI first**, with fillable fields for each record type driven by the official schema, plus the option to upload a YAML file that conforms to that schema. Prototype the form for a Research Project (inputs/outputs with Dataset pickers, Mentions, Integration Level, the unconfirmed marker) and decide where a submitted record goes:

- (a) the form saves directly to a backend store (needs a server and some auth);
- (b) the form validates client-side and opens a pull request or issue on the registry repo for a coordinator to review;
- (c) the form produces a validated YAML file the contributor sends to a coordinator.

Keep the "static wiki, no computation" preference in mind: the published site stays static either way. Choose the flow for the consortium exercise.
## Prototype

Throwaway prototype (shared by 0007 and 0008) on branch `prototype/wiki-and-submission`, in `site-prototype/`; see its README. Run `uv run site-prototype/build.py --serve` and flip layouts with `?variant=A|B|C`. Verdict pending user review.
