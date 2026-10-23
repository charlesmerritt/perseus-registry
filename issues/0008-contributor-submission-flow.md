---
title: How does a non-Git contributor submit or update a record?
labels: [wayfinder:prototype]
parent: 1
blocked_by: [6]
assignee: chazm
status: closed
---

## Question

How does a contributor create or update a record without touching Git or YAML? Direction from the user: **GUI first**, with fillable fields for each record type driven by the official schema, plus the option to upload a YAML file that conforms to that schema. Prototype the form for a Research Project (inputs/outputs with Dataset pickers, Mentions, Integration Level, the unconfirmed marker) and decide where a submitted record goes:

- (a) the form saves directly to a backend store (needs a server and some auth);
- (b) the form validates client-side and opens a pull request or issue on the registry repo for a coordinator to review;
- (c) the form produces a validated YAML file the contributor sends to a coordinator.

Keep the "static wiki, no computation" preference in mind: the published site stays static either way. Choose the flow for the consortium exercise.
## Prototype

Built as a prototype on branch `prototype/wiki-and-submission` (kept as the primary source, ending at `99564aa`), then promoted (user decision, 2026-10-23) to the canonical app in `site/`; see `site/README.md`. The prototype offered three form layouts (`?variant=A|B|C`) and three destinations; the Resolution below records the choice.

## Resolution

Decided by the user, 2026-10-23, after reviewing the prototype:

- **Destination: (b) propose on GitHub.** The form validates in the browser, then opens a GitHub issue (from the `submission` template) with the record file in its body. A coordinator reviews the issue and adds the `approved` label. An Action (`.github/workflows/submission.yml`) writes the file, re-validates it with `scripts/check.sh`, and opens a pull request that closes the issue. Contributors need a free GitHub account, but no Git or YAML. The published site stays static. (a) a backend store and (c) download-and-email were dropped.
- **Form layout: B, step wizard.** One step per section, ending in Review & submit. The long form, the live-YAML split view and the layout switcher were dropped.
- **Where prose lives: one `<id>.md` per Research Project**, with the record as YAML frontmatter and the prose sections as the Markdown body. This amends 0007's sidecar choice (user confirmed the override). The 14 seeded Research Projects were migrated. `scripts/record_file.py` is the one reader, used by the validator (and so by the Action, through `scripts/check.sh`) and the site build. Other record types stay `.yaml` unless they gain prose.
- Untrusted issue bodies are parsed by `scripts/submission.py`, which writes only `records/<type>/<id>.md|yaml` paths. The issue body reaches the Action as data, never interpolated into a shell command.
- The form assigns a new record the next `RP-nn` from the published registry, so two pending submissions can get the same ID. The Action refuses a `New` submission whose file already exists, and the coordinator renumbers it. Two open PRs for one ID conflict at merge.
- A record too long for a prefilled issue link (about 8,000 characters) is copied to the clipboard for the contributor to paste. New records can also be proposed as a pull request directly.

Before the first real submission, the repo needs a GitHub remote (`GH` in `site/assets/form.js` is a placeholder), the `submission` and `approved` labels, and permission for Actions to create pull requests. See `site/README.md`.
