# /// script
# dependencies = ["pyyaml==6.0.2", "markdown==3.7"]
# ///
"""Static wiki generator for the Perseus Research Registry.

Builds the site from records/: directory, by-Objective outline, record pages,
People, Mentions, and a schema-driven submission form (submit.html).

    uv run site/build.py           build into site/_site/
    uv run site/build.py --serve   build, then serve on :8000
    uv run site/build.py --offline use the STAC snapshot, no fetch
"""
import html, json, re, shutil, sys, urllib.request
from pathlib import Path

import markdown

HERE = Path(__file__).parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "scripts"))
from record_file import read_record  # noqa: E402
OUT = HERE / "_site"
SNAPSHOT = HERE / "stac-snapshot.json"
STAC = "https://stac.d2s.org/api/v1/collections/"
TYPES = {"research-project": "p", "software": "s", "dataset": "d", "institution": "i", "publication": "pub"}
OBJECTIVES = {"1": "Measurement", "2": "Modeling", "3": "Management", "4": "Mindset"}
TASKS = {"2.1": "Landowner Optimization", "2.2": "Broad Simulation", "2.3": "Value Chain", "2.4": "Data Visualization"}
RETIRED = ["RP-09", "RP-13", "RP-14"]
PHASES = ["concept", "development", "validation", "integration", "operational"]
PROSE = ["Overview", "Goals and milestones", "Needs from other Objectives", "Integration notes", "Methods"]
e = html.escape


# ---------------------------------------------------------------- loading

def load_records():
    """A record is X.yaml, or X.md with YAML frontmatter and its prose as the body (issue 0008)."""
    recs = {t: {} for t in TYPES}
    for t in TYPES:
        for f in sorted((REPO / "records" / t).glob("*.yaml")) + sorted((REPO / "records" / t).glob("*.md")):
            rec, rec["_body"] = read_record(f)
            rec["_file"] = str(f.relative_to(REPO))
            recs[t][rec["id"]] = rec
    return recs


def stac_meta(recs, offline):
    snap = json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else {}
    for d in recs["dataset"].values():
        col = d["source"].get("stac", {}).get("collection") if isinstance(d["source"], dict) else None
        if not col:
            continue
        if not offline:
            try:
                with urllib.request.urlopen(STAC + col, timeout=10) as r:
                    c = json.load(r)
                snap[col] = {"title": c.get("title"), "description": c.get("description"),
                             "license": c.get("license"), "doi": c.get("sci:doi")}
            except Exception as ex:  # degrade to snapshot
                print(f"STAC fetch failed for {col}: {ex}; using snapshot")
        d["_stac"] = snap.get(col, {"title": f"(missing STAC collection {col})"})
    SNAPSHOT.write_text(json.dumps(snap, indent=2))


# ---------------------------------------------------------------- derived (backlinks)

def target(v):
    return v if isinstance(v, str) else None


def derive(recs):
    P, D, S = recs["research-project"], recs["dataset"], recs["software"]
    for r in [*P.values(), *D.values(), *S.values(), *recs["institution"].values()]:
        r.update(_produced_by=[], _used_by=[], _provides_to=[], _depended_by=[], _projects=[], _cited_by=[])
    mentions = []
    for p in P.values():
        for key, back in (("inputs", "_used_by"), ("outputs", "_produced_by")):
            for link in p.get(key) or []:
                ds = target(link["dataset"])
                if ds in D:
                    D[ds][back].append(p["id"])
                via = target(link.get("via"))
                if via in S and p["id"] not in S[via]["_used_by"]:
                    S[via]["_used_by"].append(p["id"])
        for link in p.get("depends_on") or []:
            if target(link["project"]) in P:
                P[link["project"]]["_depended_by"].append(p["id"])
        insts = [p["lead_institution"]] + (p.get("institutions") or [])
        for x in insts + (p.get("leads") or []) + (p.get("collaborators") or []):
            i = target(x["institution"])
            if i in recs["institution"] and p["id"] not in recs["institution"][i]["_projects"]:
                recs["institution"][i]["_projects"].append(p["id"])
        walk_mentions(p, p["id"], mentions)
    # generated project-to-project: my output is your input
    for p in P.values():
        outs = {target(l["dataset"]) for l in p.get("outputs") or []} - {None}
        for q in P.values():
            ins = {target(l["dataset"]) for l in q.get("inputs") or []}
            for ds in outs & ins:
                p["_provides_to"].append((q["id"], ds))
    for pub in recs["publication"].values():
        for a in pub.get("about") or []:
            for t, k in (("dataset", "dataset"), ("software", "software"), ("research-project", "project")):
                if target(a.get(k)) in recs[t]:
                    recs[t][a[k]]["_cited_by"].append(pub["id"])
    return mentions


# People are inline, not records: index them by ORCID, else by name (record-schemas ticket).
PEOPLE = {}


def person_key(x):
    return x.get("orcid") or re.sub(r"[^a-z0-9]+", "-", x["name"].lower()).strip("-")


def index_people(recs):
    roles = [("research-project", "leads", "Lead"), ("research-project", "collaborators", "Collaborator"),
             ("software", "maintainers", "Maintainer"), ("publication", "authors", "Author")]
    for t, field, role in roles:
        for r in recs[t].values():
            for x in r.get(field) or []:
                p = PEOPLE.setdefault(person_key(x), {"name": x["name"], "orcid": x.get("orcid"), "institutions": [], "on": []})
                if x["institution"] not in p["institutions"]:
                    p["institutions"].append(x["institution"])
                p["on"].append((t, r["id"], x.get("role") or role, x))


def walk_mentions(node, owner, out, key=None):
    if isinstance(node, dict):
        if set(node) <= {"name", "unconfirmed", "note"} and "name" in node and key not in (None, "leads", "collaborators", "maintainers", "authors"):
            out.append((owner, key, node["name"]))
        for k, v in node.items():
            if not k.startswith("_"):
                walk_mentions(v, owner, out, k if not isinstance(v, list) else k)
    elif isinstance(node, list):
        for v in node:
            walk_mentions(v, owner, out, key)


# ---------------------------------------------------------------- render helpers

def title_of(recs, t, i):
    r = recs[t].get(i)
    if not r:
        return i
    return r.get("title") or r.get("name") or r.get("_stac", {}).get("title") or i


def unc(inner, obj):
    if isinstance(obj, dict) and obj.get("unconfirmed"):
        note = obj.get("note") or "Stated but not verified by the people involved."
        return f'<span class="unc" title="Unconfirmed: {e(note)}">{inner}<sup>?</sup></span>'
    return inner


def ref(recs, t, v):
    """A link target: a registered ID or a Mention."""
    if isinstance(v, dict):
        return unc(f'<span class="mention" title="Mention: not yet registered">{e(v["name"])}</span>', v)
    if v in recs[t]:
        return f'<a href="{TYPES[t]}-{e(v)}.html">{e(title_of(recs, t, v))}</a>'
    return f'<span class="broken" title="No such record">{e(v)}</span>'


def pid(recs, i):
    return f'<a href="p-{e(i)}.html"><b>{e(i)}</b> {e(title_of(recs, "research-project", i))}</a>'


def person_link(x):
    return unc(f'<a class="person" href="people.html#{e(person_key(x))}">{e(x["name"])}</a>', x)


def person(recs, x):
    s = f'<a class="person" href="people.html#{e(person_key(x))}">{e(x["name"])}</a>'
    if x.get("orcid"):
        s += f' <a class="orcid" href="https://orcid.org/{e(x["orcid"])}">iD</a>'
    s += f' <span class="muted">· {ref(recs, "institution", x["institution"])}</span>'
    if x.get("role"):
        s += f' <span class="muted">· {e(x["role"])}</span>'
    return unc(s, x)


def task(t):
    name = TASKS.get(t["task"], "Task name not yet documented")
    return unc(f'<span class="task">{e(t["task"])}</span> {e(name)}', t)


def objective_of(p):
    return p["primary_task"]["task"].split(".")[0]


def chip(text, cls=""):
    return f'<span class="chip {cls}">{e(text)}</span>'


def phase_chip(p):
    ph = p.get("phase")
    if not ph:
        return ""
    return f'<span class="phase ph-{ph}" title="Phase {PHASES.index(ph) + 1} of {len(PHASES)}">{e(ph)}</span>'


def phase_legend():
    return '<span class="muted">Phase:</span> ' + " ".join(f'<span class="phase ph-{x}">{x}</span>' for x in PHASES)


def level_chip(entry):
    lv = entry["level"]
    return f'<span class="lv lv-{lv.replace("/", "")}" title="{e(entry.get("note") or "")}">{e(lv)}</span>'


def note(x):
    return f' <span class="note">{e(x["note"])}</span>' if isinstance(x, dict) and x.get("note") and not x.get("unconfirmed") else ""


def ds_line(recs, link):
    s = ref(recs, "dataset", link["dataset"])
    d = recs["dataset"].get(target(link["dataset"]))
    if d:
        src = "D2S STAC" if "stac" in d["source"] else "external"
        s += f' <span class="src">{src} · {e(d["availability"])}</span>'
    if link.get("via"):
        s += f' <span class="muted">via</span> {ref(recs, "software", link["via"])}'
    return unc(s, link) + note(link)


def prose_sections(body):
    """Split '## Heading' Markdown into {heading: html}."""
    parts = re.split(r"^## +(.+)$", body, flags=re.M)
    out = {}
    for h, txt in zip(parts[1::2], parts[2::2]):
        out[h.strip()] = markdown.markdown(txt)
    return out


def count_unconfirmed(node):
    if isinstance(node, dict):
        return int(bool(node.get("unconfirmed"))) + sum(count_unconfirmed(v) for k, v in node.items() if not k.startswith("_"))
    if isinstance(node, list):
        return sum(count_unconfirmed(v) for v in node)
    return 0


# ---------------------------------------------------------------- page shell

def page(title, body, active="", head=""):
    nav = "".join(f'<a href="{h}" class="{"on" if h == active else ""}">{l}</a>' for h, l in
                  (("index.html", "Directory"), ("objectives.html", "By Objective"), ("people.html", "People"),
                   ("mentions.html", "Mentions"), ("submit.html", "Submit or update a record")))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · Perseus Research Registry</title>
<link rel="stylesheet" href="style.css">{head}</head>
<body>
<div class="draft-banner">DRAFT · records are seeded, many facts unconfirmed</div>
<header class="site"><a class="brand" href="index.html">Perseus Research Registry</a><nav>{nav}</nav></header>
<main>{body}</main>
<script src="site.js"></script></body></html>"""


# ---------------------------------------------------------------- project page

def project_blocks(recs, p):
    b = {}
    o = objective_of(p)
    b["objective"] = f'Objective {o} · {OBJECTIVES[o]}'
    b["task"] = task(p["primary_task"])
    b["supporting"] = ", ".join(task(t) for t in p.get("supporting_tasks") or []) or '<span class="muted">none</span>'
    b["status"] = chip(p["status"], "st-" + p["status"]) + phase_chip(p)
    b["lead_inst"] = unc(ref(recs, "institution", p["lead_institution"]["institution"]), p["lead_institution"]) + note(p["lead_institution"])
    b["institutions"] = "".join(f'<li>{unc(ref(recs, "institution", x["institution"]), x)} <span class="muted">{e(x.get("role") or "")}</span>{note(x)}</li>' for x in p.get("institutions") or [])
    b["leads"] = "".join(f"<li>{person(recs, x)}</li>" for x in p["leads"])
    b["collab"] = "".join(f"<li>{person(recs, x)}</li>" for x in p.get("collaborators") or [])
    b["inputs"] = "".join(f"<li>{ds_line(recs, l)}</li>" for l in p.get("inputs") or []) or '<li class="muted">none listed</li>'
    b["outputs"] = "".join(f"<li>{ds_line(recs, l)}</li>" for l in p.get("outputs") or []) or '<li class="muted">none listed</li>'
    sw = []
    for l in (p.get("inputs") or []) + (p.get("outputs") or []):
        if l.get("via") and l["via"] not in sw:
            sw.append(l["via"])
    b["software"] = "".join(f'<li>{ref(recs, "software", s)} <span class="muted">{e(recs["software"].get(target(s), {}).get("kind", ""))}</span></li>' for s in sw) or '<li class="muted">none</li>'
    b["upstream"] = "".join(f'<li>{unc(ref(recs, "research-project", l["project"]) if isinstance(l["project"], dict) else pid(recs, l["project"]), l)}{note(l)} <span class="gen">declared</span></li>' for l in p.get("depends_on") or [])
    b["downstream"] = "".join(f'<li>{pid(recs, q)} <span class="gen">generated: uses {e(title_of(recs, "dataset", ds))}</span></li>' for q, ds in p["_provides_to"])
    b["downstream"] += "".join(f'<li>{pid(recs, q)} <span class="gen">generated: declares depends on</span></li>' for q in p["_depended_by"] if q not in [x for x, _ in p["_provides_to"]])
    b["related"] = "".join(f'<li>{ref(recs, "research-project", l["project"]) if isinstance(l["project"], dict) else pid(recs, l["project"])}{note(l)}</li>' for l in p.get("related_to") or [])
    oi = p.get("objective_integration") or {}
    b["integration"] = "".join(
        f'<tr><th>{k} {OBJECTIVES[k]}</th><td>{level_chip(oi[k]) if k in oi else ("<i class=muted>own Objective</i>" if k == o else "<i class=muted>not stated</i>")}</td><td class="note">{e((oi.get(k) or {}).get("note") or "")}</td></tr>'
        for k in OBJECTIVES)
    b["prose"] = prose_sections(p["_body"])
    b["file"] = f'<p class="filenote">Source: <code>{e(p["_file"])}</code>{"" if p["_body"] else " (no prose yet)"}</p>'
    return b


def project_page(recs, p):
    """Wiki article with an infobox."""
    b = project_blocks(recs, p)
    prose = "".join(f"<h2>{e(h)}</h2>{t}" for h, t in b["prose"].items()) or '<p class="muted">No prose sections yet. <a href="submit.html">Add some</a>.</p>'
    return f"""<div class="wiki"><article class="wiki-article">
<p class="crumbs">{b["objective"]} › {b["task"]}</p>
<h1>{e(p["title"])} <span class="pid">{e(p["id"])}</span></h1>
<p class="lede">{e(p["summary"])}</p>{prose}
<h2>Datasets</h2><table class="ds-table"><tr><th>Inputs</th><th>Outputs</th></tr>
<tr><td><ul>{b["inputs"]}</ul></td><td><ul>{b["outputs"]}</ul></td></tr></table>
<h2>What links here</h2><ul>{b["downstream"] or '<li class="muted">nothing yet</li>'}</ul>{b["file"]}
</article>
<aside class="infobox"><div class="ib-title">{e(p["id"])}</div>
<table>
<tr><th>Status</th><td>{b["status"]}</td></tr>
<tr><th>Objective</th><td>{b["objective"]}</td></tr>
<tr><th>Primary Task</th><td>{b["task"]}</td></tr>
<tr><th>Supports</th><td>{b["supporting"]}</td></tr>
<tr><th>Leads</th><td><ul>{b["leads"]}</ul></td></tr>
<tr><th>Lead institution</th><td>{b["lead_inst"]}</td></tr>
<tr><th>Institutions</th><td><ul>{b["institutions"]}</ul></td></tr>
<tr><th>Collaborators</th><td><ul>{b["collab"]}</ul></td></tr>
<tr><th>Software</th><td><ul>{b["software"]}</ul></td></tr>
<tr><th>Depends on</th><td><ul>{b["upstream"]}</ul></td></tr>
<tr><th>Related</th><td><ul>{b["related"]}</ul></td></tr>
</table>
<div class="ib-title small">Integration with other Objectives</div><table class="int">{b["integration"]}</table>
<a class="btn" href="submit.html?edit={e(p["id"])}">Edit this record</a>
</aside></div>"""


# ---------------------------------------------------------------- directory

def directory_page(recs, P):
    """Sortable, filterable table."""
    rows = "".join(f"""<tr><td><a href="p-{e(p["id"])}.html">{e(p["id"])}</a></td><td><a href="p-{e(p["id"])}.html">{e(p["title"])}</a></td>
<td>{task(p["primary_task"])}</td><td>{chip(p["status"], "st-" + p["status"])}</td><td data-sort="{PHASES.index(p["phase"]) if p.get("phase") else 9}">{phase_chip(p)}</td>
<td>{", ".join(person_link(x) for x in p["leads"][:3])}{" +" + str(len(p["leads"]) - 3) if len(p["leads"]) > 3 else ""}</td>
<td>{ref(recs, "institution", p["lead_institution"]["institution"])}</td><td class="num">{count_unconfirmed(p) or ""}</td></tr>""" for p in P)
    return f"""<h1>Research Projects</h1><p class="muted">{len(P)} registered · click a header to sort · retired IDs: {", ".join(RETIRED)}</p><p>{phase_legend()}</p>
<input class="filter" placeholder="Filter by anything: name, Task, institution…" oninput="filterRows(this)">
<table class="dir sortable"><thead><tr><th>ID</th><th>Title</th><th>Primary Task</th><th>Status</th><th>Phase</th><th>Leads</th><th>Lead institution</th><th title="unconfirmed facts">?</th></tr></thead>
<tbody>{rows}</tbody></table>"""


def objectives_page(recs, P):
    """Outline grouped by Objective then Task."""
    out = [f"<h1>Perseus research, by Objective</h1><p>{phase_legend()}</p>"]
    for o, oname in OBJECTIVES.items():
        ps = [p for p in P if objective_of(p) == o]
        out.append(f'<section class="obj"><h2>Objective {o}: {oname} <span class="muted">({len(ps)})</span></h2>')
        if not ps:
            out.append('<p class="muted">No Research Projects registered yet. Objective documentation pending.</p>')
        tasks = sorted({p["primary_task"]["task"] for p in ps})
        for t in tasks:
            out.append(f'<h3>Task {t} {e(TASKS.get(t, ""))}</h3><ul class="outline">')
            for p in ps:
                if p["primary_task"]["task"] == t:
                    flag = ' <span class="unc-flag" title="Task alignment unconfirmed">task unconfirmed</span>' if p["primary_task"].get("unconfirmed") else ""
                    out.append(f'<li><a href="p-{e(p["id"])}.html"><b>{e(p["id"])}</b> {e(p["title"])}</a>{flag} {chip(p["status"], "st-" + p["status"])}{phase_chip(p)}'
                               f'<p>{e(p["summary"])}</p><p class="muted">{", ".join(person_link(x) for x in p["leads"])}</p></li>')
            out.append("</ul>")
        out.append("</section>")
    return "".join(out)


# ---------------------------------------------------------------- other record pages

def simple(title, sub, body_html, rid, kind):
    return f'<div class="simple"><p class="crumbs">{e(kind)}</p><h1>{title} <span class="pid">{e(rid)}</span></h1>{sub}{body_html}</div>'


def dataset_page(recs, d):
    st = d.get("_stac")
    if st:
        src = f'<p><span class="src">D2S STAC</span> Collection <code>{e(d["source"]["stac"]["collection"])}</code> · title and description fetched from STAC at build time</p><p>{e(st.get("description") or "")}</p>'
        if st.get("doi"):
            src += f'<p>DOI {e(st["doi"])} (from <code>sci:doi</code>)</p>'
    else:
        s = d["source"]
        link = s.get("url") or "https://doi.org/" + s["doi"]
        src = f'<p><span class="src">external</span> <a href="{e(link)}">{e(link)}</a></p><p>{e(d.get("summary") or "")}</p>'
    lst = lambda ids: "".join(f"<li>{pid(recs, i)}</li>" for i in ids) or '<li class="muted">none</li>'
    body = f"""{src}<p>{chip(d["access"])} {chip(d["availability"])}</p>
<div class="two"><div><h2>Produced by <span class="gen">generated</span></h2><ul>{lst(d["_produced_by"])}</ul></div>
<div><h2>Used by <span class="gen">generated</span></h2><ul>{lst(d["_used_by"])}</ul></div></div>
<h2>Cited by <span class="gen">generated</span></h2><ul>{"".join(f'<li>{ref(recs, "publication", x)}</li>' for x in d["_cited_by"]) or '<li class="muted">none</li>'}</ul>"""
    return simple(e(title_of(recs, "dataset", d["id"])), "", body, d["id"], "Dataset")


def software_page(recs, s):
    body = f"""<p class="lede">{e(s["summary"])}</p><p>{chip(s["kind"])} {chip(s.get("development_status") or "")} FDIS adapter: {e(s.get("fdis_adapter") or "?")}</p>
<h2>Maintainers</h2><ul>{"".join(f"<li>{person(recs, x)}</li>" for x in s["maintainers"])}</ul>
<h2>Used by Research Projects <span class="gen">generated</span></h2><ul>{"".join(f"<li>{pid(recs, i)}</li>" for i in s["_used_by"])}</ul>
<p><a href="{e(s.get("repository") or "")}">Repository</a> · <a href="{e(s.get("url") or "")}">Website</a></p>"""
    return simple(e(s["title"]), "", body, s["id"], "Software · " + s["kind"])


def institution_page(recs, i):
    body = f"""<p><a href="{e(i.get("url") or "")}">{e(i.get("url") or "")}</a> {f'· ROR <a href="{e(i["ror"])}">{e(i["ror"])}</a>' if i.get("ror") else ""}</p>
<h2>Research Projects <span class="gen">generated</span></h2><ul>{"".join(f"<li>{pid(recs, x)}</li>" for x in i["_projects"])}</ul>"""
    return simple(e(i["name"]), "", body, i["id"], "Institution")


def publication_page(recs, p):
    about = "".join(f'<li>{ref(recs, t, a[k])}</li>' for a in p.get("about") or [] for t, k in (("dataset", "dataset"), ("software", "software"), ("research-project", "project")) if k in a)
    body = f"""<p>{e(p["type"])} · {p["year"]} · {f'<a href="https://doi.org/{e(p["doi"])}">doi:{e(p["doi"])}</a>' if p.get("doi") else ""}</p>
<h2>Authors</h2><ul>{"".join(f"<li>{person(recs, x)}</li>" for x in p.get("authors") or [])}</ul><h2>About</h2><ul>{about}</ul>"""
    return simple(e(p["title"]), "", body, p["id"], "Publication")


def people_page(recs):
    """Contacts directory: everyone named on any record, with what they are on."""
    rows = []
    for key, p in sorted(PEOPLE.items(), key=lambda kv: kv[1]["name"].split()[-1].lower()):
        insts = ", ".join(unc(ref(recs, "institution", i), i) for i in p["institutions"])
        on = "".join(
            f'<li>{pid(recs, rid) if t == "research-project" else ref(recs, t, rid)} '
            f'<span class="role">{e(role)}</span>{" <span class=unc-flag>unconfirmed</span>" if x.get("unconfirmed") else ""}</li>'
            for t, rid, role, x in p["on"])
        orcid = f' <a class="orcid" href="https://orcid.org/{e(p["orcid"])}">iD</a>' if p["orcid"] else ' <span class="muted" title="Matched by name; add an ORCID to make this reliable">no ORCID</span>'
        rows.append(f'<tr id="{e(key)}" class="person-row"><td><b>{e(p["name"])}</b>{orcid}</td><td>{insts}</td><td><ul>{on}</ul></td></tr>')
    body = f"""<div class="simple wide"><h1>People</h1>
<p class="muted">{len(PEOPLE)} people named on records. People are not records: they are matched across records by ORCID when present, otherwise by name.
Use the filter to find someone; click any name on the site to land here.</p>
<input class="filter" placeholder="Filter by name, institution, project…" oninput="filterRows(this)">
<table class="dir people"><thead><tr><th>Name</th><th>Institution(s)</th><th>Research Projects and roles</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>"""
    return body


def mentions_page(recs, mentions):
    rows = "".join(f'<tr><td>{e(n)}</td><td>{e(k or "")}</td><td>{pid(recs, o)}</td></tr>' for o, k, n in sorted(mentions, key=lambda m: m[2]))
    return f"""<div class="simple"><h1>Mentions</h1><p class="muted">Things referenced by name but not yet registered.
Each is a candidate for a new record.</p><table class="dir"><tr><th>Mentioned as</th><th>Field</th><th>On</th></tr>{rows}</table></div>"""


# ---------------------------------------------------------------- submit page

def submit_page(recs):
    reg = {
        "projects": {k: {"title": v["title"], "record": clean(v), "body": v["_body"]} for k, v in recs["research-project"].items()},
        "datasets": {k: title_of(recs, "dataset", k) for k in recs["dataset"]},
        "software": {k: v["title"] for k, v in recs["software"].items()},
        "institutions": {k: v["name"] for k, v in recs["institution"].items()},
        "retired": RETIRED, "tasks": TASKS, "objectives": OBJECTIVES, "prose": PROSE,
    }
    head = f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.1/js-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/ajv/8.17.1/ajv2019.bundle.min.js"></script>
<script>window.REGISTRY = {json.dumps(reg)};
window.SCHEMA = {(REPO / "schema/generated/fdis_registry.schema.json").read_text()};</script>
<script src="form.js" defer></script>"""
    return page("Submit or update a record", '<div class="submit-root"></div>', "submit.html", head)


def clean(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


# ---------------------------------------------------------------- main

def main():
    offline = "--offline" in sys.argv
    recs = load_records()
    stac_meta(recs, offline)
    mentions = derive(recs)
    index_people(recs)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for f in ("style.css", "site.js", "form.js"):
        shutil.copy(HERE / "assets" / f, OUT / f)
    shutil.copy(REPO / "schema/generated/fdis_registry.schema.json", OUT / "fdis_registry.schema.json")
    P = sorted(recs["research-project"].values(), key=lambda p: p["id"])
    w = lambda name, html_: (OUT / name).write_text(html_)
    w("index.html", page("Directory", directory_page(recs, P), "index.html"))
    w("objectives.html", page("By Objective", objectives_page(recs, P), "objectives.html"))
    for p in P:
        w(f"p-{p['id']}.html", page(p["title"], project_page(recs, p)))
    for d in recs["dataset"].values():
        w(f"d-{d['id']}.html", page(title_of(recs, "dataset", d["id"]), dataset_page(recs, d)))
    for s in recs["software"].values():
        w(f"s-{s['id']}.html", page(s["title"], software_page(recs, s)))
    for i in recs["institution"].values():
        w(f"i-{i['id']}.html", page(i["name"], institution_page(recs, i)))
    for x in recs["publication"].values():
        w(f"pub-{x['id']}.html", page(x["title"], publication_page(recs, x)))
    w("mentions.html", page("Mentions", mentions_page(recs, mentions), "mentions.html"))
    w("people.html", page("People", people_page(recs), "people.html"))
    w("submit.html", submit_page(recs))
    print(f"built {len(list(OUT.glob('*.html')))} pages into {OUT.relative_to(REPO)}/")
    if "--serve" in sys.argv:
        import functools, http.server
        print("serving http://localhost:8000/  (Ctrl-C to stop)")
        http.server.ThreadingHTTPServer(("", 8000), functools.partial(http.server.SimpleHTTPRequestHandler, directory=OUT)).serve_forever()


if __name__ == "__main__":
    main()
