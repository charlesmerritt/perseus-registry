# Registry Records

The registry's records, seeded once from `sources/objective2-tracker.csv` (see `issues/0010-seed-objective-2-records.md`). The tracker is not consulted again; these files are now the source.

- `<type>/<id>.yaml` is one record. The directory gives its type and the file name its `id`, as in `examples/`.
- `research-project/<id>.md` holds the record's prose sections (Overview, Needs from other Objectives, Integration notes), which are not schema fields.

Seeding conventions:

- A fact the tracker hedges ("to confirm", "?", "potentially") carries `unconfirmed: true`, usually with a `note`.
- A person whose affiliation the tracker does not state is marked `unconfirmed` with the note "Affiliation not stated in the tracker". Where there was no basis for a guess, the institution is the Mention `Not stated`.
- Anything without a registered record (most model outputs, Objective 3 survey data, FVS, Woodstock) is a Mention, ready to be promoted.
- Tracker columns not imported, per the tracker-boundary ticket: PI Ambassador, Current Update, Next Milestone, Discussion/Decision Needed, Presentation Status and Month. Hedges in Discussion/Decision Needed were still used to set `unconfirmed` markers.

`scripts/check.sh` validates every record here.
