---
title: What should the static wiki look like, and what generates it?
labels: [wayfinder:prototype]
parent: 1
blocked_by: [6]
assignee: chazm
status: open
---

## Question

Build a rough clickable prototype of the directory and a Research Project page (e.g. O2-06 LANDIS-II) from a few hand-written records: structured panels (Objective/Task, leads, institutions, Software, input/output Datasets with live STAC titles, statically generated 'used by' backlinks) beside free-form wiki sections. Use it to choose between MkDocs Material with a generator plugin and a small static-site generator, and to fix where the prose lives (Markdown body in the same file as the YAML frontmatter, or a separate file).

Constraint added after the relationship ticket: the stack must also host **schema-driven entry forms** (GUI-first submission; see the contributor-flow ticket), so weigh generators by how easily a form page can be embedded alongside the static wiki.

## Prototype

Throwaway prototype (shared by 0007 and 0008) on branch `prototype/wiki-and-submission`, in `site-prototype/`; see its README. Run `uv run site-prototype/build.py --serve` and flip layouts with `?variant=A|B|C`. Verdict pending user review.
