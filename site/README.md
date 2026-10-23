# Site

The Perseus Research Registry's static wiki and submission form, generated from `../records/`.

## Run

```sh
uv run site/build.py --serve      # build, then serve http://localhost:8000/
uv run site/build.py              # build into site/_site/
uv run site/build.py --offline    # skip the STAC fetch, use stac-snapshot.json
```

## What it builds

| Page | Contents |
|---|---|
| `index.html` | Research Project directory: a filterable, sortable table |
| `objectives.html` | The same Research Projects as an outline by Objective, then Task |
| `p-<id>.html` | Research Project pages: a wiki article (prose from the sidecar `<id>.md`) with an infobox of structured facts |
| `d-`, `s-`, `i-`, `pub-<id>.html` | Dataset, Software, Institution and Publication pages, with generated backlinks |
| `people.html` | Contacts directory. Every name on the site links here; people are matched by ORCID, otherwise by name. |
| `mentions.html` | Things referenced by name but not yet registered |
| `submit.html` (`?edit=<id>` to edit) | Schema-driven form: fill in fields or upload YAML, validate against the FDIS Registry Profile, then submit |

## Pending decisions

The form layout is not chosen yet (issue 0008). Until it is, `submit.html` carries three layouts, switched with `?variant=A|B|C`, the floating bar, or the ← → keys: A long form + section nav · B step wizard · C form + live editable YAML.

The form's Submit panel shows the three candidate destinations: (a) save to a store, (b) propose on GitHub, (c) download and send to a coordinator. Only (c) actually works. The GitHub repo URL and coordinator email are placeholders. When a layout and a destination are chosen, drop the others and `assets/switcher.js`.

## How it works

- `build.py` (Python, PyYAML and Markdown) loads every record (`<type>/<id>.yaml`, plus prose from a sidecar `<id>.md`), fetches Dataset titles from D2S STAC at build time (falling back to `stac-snapshot.json`), and generates the inverse links (used by, produced by, provides to, cited by), the People index and the Mentions list.
- `assets/form.js` renders fields from `schema/generated/fdis_registry.schema.json` (`$defs/ResearchProject`) and validates with Ajv. The only hand-written parts are UI hints: section grouping, which registry list feeds each picker, and labels. New Research Projects get the next neutral `RP-nn` ID, and retired numbers are never reused.
- Phase is colour-coded on a light-to-dark scale, from concept to operational.
