# Local issue tracker

One markdown file per issue: `NNNN-slug.md`. The number is the issue id.

Frontmatter fields:

- `title`: the issue's name; refer to issues by it
- `labels`: e.g. `[wayfinder:map]`, `[wayfinder:research]`
- `parent`: id of the parent map (child tickets only)
- `blocked_by`: list of issue ids; a ticket is unblocked when all are closed
- `assignee`: who claimed it; empty means unclaimed
- `status`: `open` or `closed`

## Wayfinding operations

- **Map**: the issue labelled `wayfinder:map`.
- **Claim**: set `assignee` before any work.
- **Resolve**: append a `## Resolution` section, set `status: closed`, add a line to the map's Decisions so far.
- **Frontier**: `status: open`, empty `assignee`, every `blocked_by` id closed.
