# PROTOTYPE: static wiki + submission form (issues 0007, 0008)

Throwaway. It lives on the `prototype/wiki-and-submission` branch only; main keeps the decisions, not this code.

**Plan:** three structurally different layouts each for the directory and the Research Project page, plus three layouts for a schema-driven submission form with three submission destinations (a/b/c). Every page switches with `?variant=A|B|C`, the floating bar, or the ← → keys.

## Run

```sh
uv run site-prototype/build.py --serve      # http://localhost:8000/
uv run site-prototype/build.py --offline    # skip STAC fetch, use stac-snapshot.json
```

## What to look at

| Page | Variants | Question |
|---|---|---|
| `index.html` | A sortable table · B outline by Objective → Task · C connection matrix (Tasks + Integration Level) | 0007 directory |
| `p-O2-06.html` (also `p-O2-15.html`) | A wiki article + infobox · B dashboard + data-flow strip · C long-read + "needs confirming" checklist | 0007 page layout |
| `d-treemap.html`, `s-landis-ii.html`, `mentions.html` | one layout | generated backlinks, live STAC titles, Mentions |
| `submit.html` (`?edit=O2-06` to edit) | A long form + section nav · B step wizard · C form + live editable YAML | 0008 form; destinations (a)/(b)/(c) in the Submit panel |

## What it is made of

- `build.py`: the "small static-site generator" option, about 550 lines of Python with PyYAML and Markdown. It reads `../examples/` plus `records/`, which overrides by id. It fetches STAC titles at build time, falls back to `stac-snapshot.json`, and generates backlinks (used by, produced by, provides to, cited by) and the Mentions list.
- `records/`: rough prototype records. Most Research Projects were machine-drafted from the tracker, so leads are marked unconfirmed. **This is not the seeding task (0010).**
- Prose storage under test: `O2-06.yaml` + `O2-06.md` (two files) and `O2-15.md` (one file, frontmatter). The generator and form handle both.
- `assets/form.js`: renders fields from `schema/generated/fdis_registry.schema.json` (`$defs/ResearchProject`) and validates with Ajv. The only hand-written parts are UI hints: section grouping, which registry list feeds each picker, and labels.
- The GitHub repo URL and coordinator email in the form are placeholders.
