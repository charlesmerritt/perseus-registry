---
title: What should the static wiki look like, and what generates it?
labels: [wayfinder:prototype]
parent: 1
blocked_by: [6]
assignee: chazm
status: closed
---

## Question

Build a rough clickable prototype of the directory and a Research Project page (e.g. O2-06 LANDIS-II) from a few hand-written records: structured panels (Objective/Task, leads, institutions, Software, input/output Datasets with live STAC titles, statically generated 'used by' backlinks) beside free-form wiki sections. Use it to choose between MkDocs Material with a generator plugin and a small static-site generator, and to fix where the prose lives (Markdown body in the same file as the YAML frontmatter, or a separate file).

Constraint added after the relationship ticket: the stack must also host **schema-driven entry forms** (GUI-first submission; see the contributor-flow ticket), so weigh generators by how easily a form page can be embedded alongside the static wiki.

## Prototype

Built as a prototype on branch `prototype/wiki-and-submission` (kept as the primary source, ending at `99564aa`), then promoted (user decision, 2026-10-23) to the canonical app in `site/`; see `site/README.md`. The prototype carried three layouts per page; the Resolution below records which were kept.

## Resolution

Decided by the user, 2026-10-23, after reviewing the prototype:

- **Generator**: a small Python generator (`site/build.py`), not MkDocs Material. It is plain Python string templates over `records/`, and the schema-driven form is one more generated page with its own script, so embedding forms costs nothing extra.
- **Directory**: the sortable, filterable table is the index (`index.html`). The outline by Objective, then Task, is kept as a second view (`objectives.html`), linked from the nav. The connection matrix is dropped.
- **Research Project page**: wiki article plus infobox. Prose sections run down the page, structured facts sit in the infobox, then the Datasets table and the generated "What links here". The dashboard and long-read layouts are dropped.
- **Where prose lives** (superseded, see below): a sidecar `<id>.md` next to `<id>.yaml`. The YAML stays plain for the schema validator and the form. Frontmatter-in-one-`.md` support is removed from the loader.

Implemented in `site/`. `submit.html` kept its layout variants until issue 0008 chose one.

**Amended by issue 0008** (user decision, 2026-10-23): prose now lives in one `<id>.md` with the record as YAML frontmatter, not in a sidecar. The submit page is a single step wizard.
