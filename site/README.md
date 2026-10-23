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
| `p-<id>.html` | Research Project pages: a wiki article (the prose body of `<id>.md`) with an infobox of structured facts |
| `d-`, `s-`, `i-`, `pub-<id>.html` | Dataset, Software, Institution and Publication pages, with generated backlinks |
| `people.html` | Contacts directory. Every name on the site links here; people are matched by ORCID, otherwise by name. |
| `mentions.html` | Things referenced by name but not yet registered |
| `submit.html` (`?edit=<id>` to edit) | Schema-driven step wizard: fill in fields or upload a record file, validate against the FDIS Registry Profile, then submit as a GitHub issue |

## Submission flow (issue 0008)

1. The contributor fills in the wizard (or uploads a record file) on the static site. It validates in the browser.
2. **Submit** opens a new GitHub issue from the `submission` template, with `records/research-project/<id>.md` filled into the body. A record too long for a prefilled link (about 8,000 characters) is copied to the clipboard for the contributor to paste instead. New records can also be opened directly as a pull request.
3. A coordinator reviews the issue and adds the `approved` label. `.github/workflows/submission.yml` writes the file with `scripts/submission.py` (which only accepts `records/<type>/<id>.md|yaml` paths), runs `scripts/check.sh`, and opens a pull request that closes the issue. A `New` submission whose ID another record has taken meanwhile is refused for the coordinator to renumber. If any step fails, it comments on the issue.
4. Merging the pull request publishes the change. `.github/workflows/check.yml` validates every push and pull request.

Contributors need a free GitHub account, but no Git or YAML. Before the first real submission:

- Set `GH` in `assets/form.js` to the registry repository's URL. It is a placeholder because the repo has no remote yet.
- Create the `submission` and `approved` labels.
- Under Settings → Actions → General, allow GitHub Actions to create pull requests.

## How it works

- `build.py` (Python, PyYAML and Markdown) loads every record (`<type>/<id>.yaml`, or `<type>/<id>.md` with the record as YAML frontmatter and its prose as the body), fetches Dataset titles from D2S STAC at build time (falling back to `stac-snapshot.json`), and generates the inverse links (used by, produced by, provides to, cited by), the People index and the Mentions list.
- `assets/form.js` renders fields from `schema/generated/fdis_registry.schema.json` (`$defs/ResearchProject`) and validates with Ajv. The only hand-written parts are UI hints: section grouping, which registry list feeds each picker, and labels. New Research Projects get the next neutral `RP-nn` ID, and retired numbers are never reused.
- Phase is colour-coded on a light-to-dark scale, from concept to operational.
