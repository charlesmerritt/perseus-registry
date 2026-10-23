// PROTOTYPE (issue 0008): schema-driven Research Project form.
// Fields come from the generated JSON Schema ($defs/ResearchProject); the only
// hand-written parts are UI hints (section grouping, which registry list a
// picker draws from, labels). Three layouts share one record in memory.
// Nothing is persisted.
(function () {
  const SCHEMA = window.SCHEMA, REG = window.REGISTRY, defs = SCHEMA.$defs;
  const CLASS = "ResearchProject";
  const GH = "https://github.com/OWNER/perseus-registry"; // placeholder: repo has no remote yet
  const COORDINATOR = "registry-coordinator@example.org"; // placeholder

  // ---- UI hints (the non-schema part) ----
  const SECTIONS = [
    ["basics", "Basics", ["id", "title", "summary", "status", "phase", "primary_task", "supporting_tasks"]],
    ["people", "People and institutions", ["leads", "lead_institution", "collaborators", "institutions"]],
    ["data", "Datasets and Software", ["inputs", "outputs"]],
    ["relations", "Other Research Projects", ["depends_on", "part_of", "related_to", "superseded_by"]],
    ["integration", "Integration with other Objectives", ["objective_integration"]],
    ["other", "Links and other", []], // gets every schema property not listed above
    ["prose", "Wiki sections (Markdown)", []],
  ];
  const PICK = { dataset: "datasets", via: "software", institution: "institutions", project: "projects" };
  const LABELS = { primary_task: "Primary Task", supporting_tasks: "Supporting Tasks", lead_institution: "Lead institution",
    objective_integration: "Integration Level by Objective", via: "via Software", orcid: "ORCID", tracker_id: "Tracker ID",
    depends_on: "Depends on", part_of: "Part of", related_to: "Related to", superseded_by: "Superseded by" };
  const props = defs[CLASS].properties;
  const listed = SECTIONS.flatMap((s) => s[2]);
  SECTIONS.find((s) => s[0] === "other")[2] = Object.keys(props).filter((k) => !listed.includes(k));
  const ORDER = SECTIONS.flatMap((s) => s[2]);

  // ---- state ----
  const params = new URLSearchParams(location.search);
  const S = { rec: {}, prose: {}, editing: null, proseStyle: "sidecar", dest: params.get("dest") || "b", step: 0, errors: [] };
  const editId = params.get("edit");
  if (editId && REG.projects[editId]) loadExisting(editId);
  else newRecord();

  function newRecord() {
    S.editing = null;
    S.rec = { status: "proposed", primary_task: { task: "" }, leads: [{}], lead_institution: {} };
    S.prose = Object.fromEntries(REG.prose.map((h) => [h, ""]));
  }
  function loadExisting(id) {
    const p = REG.projects[id];
    S.editing = id;
    S.rec = structuredClone(p.record);
    S.prose = parseProse(p.body);
    S.proseStyle = p.file.endsWith(".md") ? "frontmatter" : "sidecar";
  }
  function parseProse(body) {
    const out = Object.fromEntries(REG.prose.map((h) => [h, ""]));
    const parts = (body || "").split(/^## +(.+)$/m);
    for (let i = 1; i < parts.length; i += 2) out[parts[i].trim()] = parts[i + 1].trim();
    return out;
  }

  // ---- ID assignment: O{objective}-{nn}, never reusing retired numbers ----
  function nextId() {
    const o = ((S.rec.primary_task || {}).task || "").split(".")[0];
    if (!/^[1-4]$/.test(o)) return "";
    const used = [...Object.keys(REG.projects), ...REG.retired].filter((x) => x.startsWith(`O${o}-`)).map((x) => +x.slice(3));
    return `O${o}-${String(Math.max(0, ...used) + 1).padStart(2, "0")}`;
  }
  const currentId = () => S.editing || nextId();

  // ---- path helpers ----
  const getAt = (path) => path.reduce((o, k) => (o == null ? undefined : o[k]), S.rec);
  function setAt(path, v) {
    let o = S.rec;
    path.slice(0, -1).forEach((k, i) => {
      if (o[k] == null || typeof o[k] !== "object") o[k] = typeof path[i + 1] === "number" ? [] : {};
      o = o[k];
    });
    o[path[path.length - 1]] = v;
  }

  // ---- schema helpers ----
  const refName = (s) => (s && s.$ref ? s.$ref.split("/").pop() : null);
  const deref = (s) => { while (s && s.$ref) s = defs[refName(s)]; return s; };
  function unwrap(s) { // strip nullability -> {s, optional}
    if (s.anyOf && s.anyOf.some((x) => x.type === "null")) {
      const rest = s.anyOf.filter((x) => x.type !== "null");
      return { s: rest.length === 1 ? { ...rest[0], description: s.description } : { anyOf: rest, description: s.description }, optional: true };
    }
    if (Array.isArray(s.type) && s.type.includes("null")) return { s: { ...s, type: s.type.find((t) => t !== "null") }, optional: true };
    return { s, optional: false };
  }
  const isPicker = (s) => s.anyOf && s.anyOf.some((x) => refName(x) === "Mention");
  const human = (k) => LABELS[k] || (String(k).charAt(0).toUpperCase() + String(k).slice(1)).replace(/_/g, " ");

  // ---- tiny DOM helper ----
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (v === true) el.setAttribute(k, "");
      else if (v !== false && v != null) el.setAttribute(k, v);
    }
    for (const c of kids.flat()) if (c != null) el.append(c.nodeType ? c : document.createTextNode(c));
    return el;
  }

  // ---- widgets ----
  function field(key, schema, path, required) {
    const { s, optional } = unwrap(schema);
    const row = h("div", { class: "f-row", "data-path": "/" + path.join("/") });
    const label = h("label", { class: "f-label" }, human(key), required && !optional ? h("span", { class: "f-req" }, " *") : null);
    const help = s.description || deref(s)?.description;
    const ctl = control(key, s, path);
    if (ctl.inlineLabel) return ctl.el;
    row.append(...[label, help && !ctl.noHelp ? h("p", { class: "f-help" }, help) : null, ctl.el, h("div", { class: "f-err" })].filter(Boolean));
    return row;
  }

  function control(key, s, path) {
    const name = refName(s);
    const d = deref(s);
    if (key === "id") {
      return { el: h("input", { type: "text", readonly: true, value: currentId() || "(assigned from the primary Task)", class: "f-id" }), noHelp: false };
    }
    if (isPicker(s)) return { el: picker(key, path) };
    if (d.enum) {
      const v = getAt(path) || "";
      const sel = h("select", { onchange: (ev) => { setAt(path, ev.target.value || undefined); changed(); } },
        h("option", { value: "" }, "—"), d.enum.map((x) => h("option", { value: x, selected: x === v }, x)));
      return { el: sel };
    }
    if (d.type === "boolean") {
      const lab = key === "unconfirmed" ? "Not confirmed yet" : human(key);
      const cb = h("input", { type: "checkbox", checked: !!getAt(path), onchange: (ev) => { setAt(path, ev.target.checked || undefined); changed(); } });
      return { el: h("label", { class: "f-unc", "data-path": "/" + path.join("/"), title: d.description || "" }, cb, lab), inlineLabel: true };
    }
    if (d.type === "array") return { el: list(key, d.items, path, d.minItems) };
    if (d.type === "object" || d.properties) return { el: object(key, d, path, name), noHelp: true };
    // strings
    const multiline = key === "summary";
    const attrs = { value: getAt(path) || "", oninput: (ev) => { setAt(path, ev.target.value || undefined); changed(key === "task"); } };
    if (key === "task") attrs.list = "f-tasks";
    if (d.pattern && key !== "orcid") attrs.placeholder = key === "task" ? "e.g. 2.2" : d.format === "uri" ? "https://…" : "";
    if (key === "orcid") attrs.placeholder = "0000-0000-0000-0000";
    const input = multiline ? h("textarea", { oninput: attrs.oninput, rows: 3 }, attrs.value) : h("input", { type: "text", ...attrs });
    if (key === "orcid") return { el: h("div", { class: "f-picker" }, input, h("button", { type: "button", class: "f-add", onclick: () => orcidLookup(path, input) }, "Look up")) };
    return { el: input };
  }

  function picker(key, path) {
    const pool = REG[PICK[key]] || {};
    const v = getAt(path);
    const isMention = v && typeof v === "object";
    const opts = Object.entries(pool).map(([id, t]) => [id, `${id} · ${typeof t === "string" ? t : t.title}`]);
    const box = h("div", { class: "f-picker" });
    const sel = h("select", { class: isMention ? "f-mode" : "",
      onchange: (ev) => {
        if (ev.target.value === "__mention") setAt(path, { name: "" });
        else setAt(path, ev.target.value || undefined);
        box.replaceWith(picker(key, path));
        changed();
      } },
      h("option", { value: "" }, "— choose —"),
      opts.map(([id, t]) => h("option", { value: id, selected: v === id }, t)),
      h("option", { value: "__mention", selected: isMention }, "Not registered yet (Mention)…"));
    box.append(sel);
    if (isMention) box.append(h("input", { type: "text", placeholder: `Name the unregistered ${key}`, value: v.name || "",
      oninput: (ev) => { v.name = ev.target.value; changed(); } }));
    return box;
  }

  function list(key, items, path, minItems) {
    const box = h("div", { class: "f-list" });
    const isObj = !!deref(items).properties;
    const draw = () => {
      const arr = getAt(path) || [];
      box.replaceChildren(
        ...arr.map((_, i) => h("div", { class: "f-item" },
          h("button", { type: "button", class: "f-del", title: "Remove", onclick: () => { arr.splice(i, 1); draw(); changed(); } }, "×"),
          isObj ? control(key, items, [...path, i]).el : field(`${human(key)} ${i + 1}`, items, [...path, i], false))),
        h("button", { type: "button", class: "f-add", onclick: () => { setAt(path, [...arr, isObj ? {} : ""]); draw(); changed(); } },
          "+ add " + human(key).toLowerCase().replace(/s$/, "")));
    };
    draw();
    return box;
  }

  function object(key, d, path, name) {
    const req = d.required || [];
    const entries = Object.entries(d.properties);
    const first = ["name", "task", "dataset", "project", "institution", "via", "level"];
    const pos = (k) => (first.includes(k) ? first.indexOf(k) : 99);
    const main = entries.filter(([k]) => k !== "unconfirmed" && k !== "note").sort((a, b) => pos(a[0]) - pos(b[0]));
    const box = h("div", { class: main.length > 1 ? "f-obj" : "" });
    const inline = h("div", { class: "f-inline" });
    for (const [k, ps] of main) {
      let label = k;
      if (key === "objective_integration") {
        const own = ((S.rec.primary_task || {}).task || "").split(".")[0] === k;
        label = `Objective ${k} ${REG.objectives[k]}${own ? " (this project's own: leave blank)" : ""}`;
        box.append(h("div", { class: "f-item" }, h("b", {}, label), control(k, unwrap(ps).s, [...path, k]).el));
        continue;
      }
      inline.append(field(label, ps, [...path, k], req.includes(k)));
    }
    if (inline.children.length) box.append(inline);
    if (d.properties.unconfirmed || d.properties.note) {
      box.append(h("div", { class: "f-inline" },
        d.properties.unconfirmed ? field("unconfirmed", d.properties.unconfirmed, [...path, "unconfirmed"]) : null,
        d.properties.note ? h("div", { class: "f-row" }, h("input", { type: "text", placeholder: "note (optional): why unconfirmed, what the link carries",
          value: getAt([...path, "note"]) || "", oninput: (ev) => { setAt([...path, "note"], ev.target.value || undefined); changed(); } })) : null));
    }
    return box;
  }

  async function orcidLookup(path, input) {
    const id = input.value.trim();
    try {
      const r = await fetch(`https://pub.orcid.org/v3.0/${id}/person`, { headers: { Accept: "application/json" } });
      const j = await r.json();
      const n = j.name;
      const full = [n?.["given-names"]?.value, n?.["family-name"]?.value].filter(Boolean).join(" ");
      if (!full) throw new Error("no public name");
      setAt([...path.slice(0, -1), "name"], full);
      setAt(path, id);
      render();
    } catch (ex) {
      alertInline(`ORCID lookup failed: ${ex.message}`);
    }
  }
  function alertInline(msg) { document.querySelectorAll(".f-status").forEach((el) => { el.textContent = msg; el.className = "f-status bad"; }); }

  function proseSection() {
    const box = h("div", {});
    box.append(h("p", { class: "f-help" }, "Free-form wiki text. Each box becomes a ## section of the record's Markdown body."),
      h("div", { class: "f-row" }, h("label", { class: "f-label" }, "Store prose as"),
        h("select", { onchange: (ev) => { S.proseStyle = ev.target.value; changed(); } },
          h("option", { value: "sidecar", selected: S.proseStyle === "sidecar" }, "Two files: ID.yaml + ID.md"),
          h("option", { value: "frontmatter", selected: S.proseStyle === "frontmatter" }, "One file: ID.md with YAML frontmatter"))));
    for (const hd of REG.prose) {
      box.append(h("div", { class: "f-row" }, h("label", { class: "f-label" }, hd),
        h("textarea", { rows: 4, oninput: (ev) => { S.prose[hd] = ev.target.value; changed(); } }, S.prose[hd] || "")));
    }
    return box;
  }

  function section(key) {
    const [, title, fields] = SECTIONS.find((s) => s[0] === key);
    const req = defs[CLASS].required;
    const body = key === "prose" ? proseSection() : h("div", {}, fields.map((f) => field(f, props[f], [f], req.includes(f))));
    return h("div", { class: "f-section", id: "sec-" + key }, h("h2", {}, title, " ", h("span", { class: "cnt f-cnt", "data-sec": key })), body);
  }

  // ---- output ----
  function clean(v) {
    if (Array.isArray(v)) { const a = v.map(clean).filter((x) => x !== undefined); return a.length ? a : undefined; }
    if (v && typeof v === "object") {
      const o = {};
      for (const [k, x] of Object.entries(v)) { const c = clean(x); if (c !== undefined && c !== false) o[k] = c; }
      return Object.keys(o).length ? o : undefined;
    }
    return v === "" || v == null ? undefined : v;
  }
  function output() {
    const rec = clean(S.rec) || {};
    const id = currentId();
    if (id) rec.id = id;
    const ordered = {};
    for (const k of ORDER) if (k in rec) ordered[k] = rec[k];
    const body = REG.prose.filter((hd) => (S.prose[hd] || "").trim()).map((hd) => `## ${hd}\n\n${S.prose[hd].trim()}\n`).join("\n");
    const yaml = jsyaml.dump(ordered, { lineWidth: 78, noRefs: true });
    const dir = "records/research-project/";
    const files = S.proseStyle === "frontmatter"
      ? [{ path: `${dir}${id || "NEW"}.md`, text: `---\n${yaml}---\n\n${body}` }]
      : [{ path: `${dir}${id || "NEW"}.yaml`, text: yaml }, ...(body ? [{ path: `${dir}${id || "NEW"}.md`, text: body }] : [])];
    return { rec: ordered, yaml, files };
  }

  // ---- validation (Ajv against the generated JSON Schema) ----
  const Ajv = window.ajv2019.default || window.ajv2019;
  const ajv = new Ajv({ allErrors: true, strict: false });
  ajv.addFormat("uri", true);
  ajv.addSchema(SCHEMA, "fdis");
  const validateRP = ajv.compile({ $ref: (SCHEMA.$id || "fdis") + "#/$defs/" + CLASS });
  function friendly(err) {
    switch (err.keyword) {
      case "required": return err.params.missingProperty === "id" && !err.instancePath ? "assigned once you choose a primary Task" : `${human(err.params.missingProperty)} is required`;
      case "pattern": return /orcid/.test(err.instancePath) ? "ORCID looks like 0000-0002-1825-0097" : /task/.test(err.instancePath) ? "Task looks like 2.2" : "unexpected format";
      case "enum": return "pick one of the options";
      case "minItems": return "add at least one";
      case "additionalProperties": return `unknown field "${err.params.additionalProperty}"`;
      case "anyOf": return "choose a registered record, or name a Mention";
      default: return err.message;
    }
  }
  function validate() {
    const { rec } = output();
    const ok = validateRP(rec);
    // one message per field, the most useful one (anyOf branches are noisy)
    const rank = { required: 0, anyOf: 1, enum: 2, pattern: 3, minItems: 4, additionalProperties: 5 };
    const best = {};
    for (const er of validateRP.errors || []) {
      const path = er.keyword === "required" ? `${er.instancePath}/${er.params.missingProperty}` : er.instancePath;
      const r = rank[er.keyword] ?? 9;
      if (!best[path] || r < best[path].r) best[path] = { path, msg: friendly(er), r };
    }
    // a failed anyOf also reports its branches at deeper paths; drop those
    const anyOfPaths = Object.values(best).filter((x) => x.r === 1).map((x) => x.path);
    S.errors = Object.values(best).filter((x) => !anyOfPaths.some((p) => x.path !== p && x.path.startsWith(p + "/")));
    // checks the JSON Schema cannot express, done here and again at site build
    for (const [i, l] of (rec.inputs || []).concat(rec.outputs || []).entries())
      if (typeof l.dataset === "object" && !l.dataset.name) S.errors.push({ path: `/inputs/${i}/dataset`, msg: "name the Mention" });
    return ok && !S.errors.length;
  }

  // ---- render layouts ----
  let root;
  function layoutRoot() {
    const sec = [...document.querySelectorAll("section.variant")].find((s) => !s.hidden);
    return sec && sec.querySelector(".submit-root");
  }
  function topBar() {
    const projects = Object.entries(REG.projects).map(([id, p]) => h("option", { value: id, selected: id === S.editing }, `${id} · ${p.title}`));
    const up = h("input", { type: "file", accept: ".yaml,.yml,.md", style: "display:none", onchange: (ev) => upload(ev.target.files[0]) });
    return h("div", { class: "f-top" },
      h("b", {}, S.editing ? `Editing ${S.editing}` : `New Research Project ${currentId() ? "→ " + currentId() : ""}`),
      h("button", { type: "button", class: "btn ghost", onclick: () => { newRecord(); render(); } }, "New"),
      h("select", { onchange: (ev) => { if (ev.target.value) { loadExisting(ev.target.value); render(); } } },
        h("option", { value: "" }, "Edit an existing record…"), projects),
      h("button", { type: "button", class: "btn ghost", onclick: () => up.click() }, "Upload a YAML file"), up,
      h("span", { class: "f-status" }));
  }
  async function upload(file) {
    if (!file) return;
    const text = await file.text();
    try {
      let rec, body = "";
      if (text.startsWith("---")) { const [, fm, b] = text.split(/^---\s*$/m); rec = jsyaml.load(fm); body = b; }
      else rec = jsyaml.load(text);
      S.rec = rec; S.prose = parseProse(body);
      S.editing = REG.projects[rec.id] ? rec.id : null;
      render();
    } catch (ex) { alertInline("Could not read that file: " + ex.message); }
  }

  function destPanel() {
    const box = h("div", { class: "dest" });
    const draw = () => {
      const ok = validate();
      const { files } = output();
      const tabs = [["a", "(a) Save to registry"], ["b", "(b) Propose on GitHub"], ["c", "(c) Download, send to coordinator"]];
      const out = h("div", { class: "dest-out" });
      if (!ok) out.append(h("p", { class: "f-err" }, `Fix ${S.errors.length} problem(s) first. You can still download a draft under (c).`));
      if (S.dest === "a") out.append(
        h("p", {}, "The form writes straight into a registry store; the static site rebuilds from it."),
        h("p", {}, h("button", { type: "button", class: "btn", disabled: !ok, onclick: (ev) => { ev.target.replaceWith(h("p", { class: "f-status ok" }, `(simulated) POST /api/records/${currentId()} → 201. Rebuild queued.`)); } }, "Sign in with institution account, then save")),
        h("ol", {}, h("li", {}, "Needs: a server (or serverless function) + a store that commits YAML back to Git."),
          h("li", {}, "Needs: accounts for every contributor across the consortium's institutions, and permissions."),
          h("li", {}, "Review happens after the fact, if at all.")));
      if (S.dest === "b") {
        const f = files[0];
        const prUrl = `${GH}/new/main?filename=${encodeURIComponent(f.path)}&value=${encodeURIComponent(f.text)}`;
        const issueBody = files.map((x) => `\`${x.path}\`\n\n\`\`\`${x.path.endsWith(".yaml") ? "yaml" : "markdown"}\n${x.text}\`\`\``).join("\n\n");
        const issueUrl = `${GH}/issues/new?labels=submission&title=${encodeURIComponent((S.editing ? "Update " : "New ") + (currentId() || "record"))}&body=${encodeURIComponent(issueBody)}`;
        out.append(
          h("p", {}, "The form validates here, then opens GitHub with the file filled in. A coordinator reviews and merges; the site rebuilds."),
          h("p", {}, h("a", { class: "btn", href: ok ? issueUrl : null, target: "_blank" }, "Open a submission issue"), " ",
            !S.editing && files.length === 1 ? h("a", { class: "btn ghost", href: ok ? prUrl : null, target: "_blank" }, "Open as a pull request") : h("span", { class: "muted" }, S.editing ? " (PR prefill only works for new files; edits go via the issue)" : " (two files: PR prefill takes one; use the issue)")),
          h("ol", {}, h("li", {}, "Needs: a free GitHub account per contributor (no Git, no YAML, but a login)."),
            h("li", {}, "An Action turns a 'submission' issue into a PR and re-validates it."),
            h("li", {}, `Issue URL is ${issueUrl.length.toLocaleString()} characters; GitHub rejects URLs over ~8,000, so long prose must be pasted instead.`)));
      }
      if (S.dest === "c") {
        const dl = () => files.forEach((x) => { const a = h("a", { href: URL.createObjectURL(new Blob([x.text], { type: "text/plain" })), download: x.path.split("/").pop() }); a.click(); });
        out.append(h("p", {}, "The form produces the file(s); the contributor emails them to a coordinator who commits them."),
          h("p", {}, h("button", { type: "button", class: "btn", onclick: dl }, `Download ${files.map((x) => x.path.split("/").pop()).join(" + ")}`), " ",
            h("a", { class: "btn ghost", href: `mailto:${COORDINATOR}?subject=${encodeURIComponent("Registry record " + (currentId() || ""))}&body=${encodeURIComponent("Attached: " + files.map((x) => x.path).join(", "))}` }, "Email the coordinator")),
          h("ol", {}, h("li", {}, "Needs nothing but a browser and email."), h("li", {}, "Coordinator does all the Git work; easy to lose track of attachments and versions.")));
      }
      box.replaceChildren(h("h2", {}, "Submit"), h("div", { class: "dest-tabs" }, tabs.map(([k, t]) =>
        h("button", { type: "button", class: S.dest === k ? "on" : "", onclick: () => { S.dest = k; draw(); } }, t))), out);
    };
    box.redraw = draw;
    draw();
    return box;
  }

  function layoutA() {
    const nav = h("nav", {}, SECTIONS.map(([k, t]) => h("a", { href: "#sec-" + k }, t, " ", h("span", { class: "cnt f-cnt", "data-sec": k }))),
      h("a", { href: "#dest" }, "Submit"));
    const main = h("div", {}, SECTIONS.map(([k]) => section(k)),
      h("details", {}, h("summary", {}, "Preview the YAML"), h("pre", { class: "f-yaml" })), h("div", { id: "dest" }, destPanel()));
    return h("div", { class: "fA" }, nav, main);
  }
  function layoutB() {
    const steps = [...SECTIONS.map(([k, t]) => [k, t]), ["review", "Review & submit"]];
    const cur = steps[S.step];
    const bar = h("div", { class: "steps" }, steps.map(([k, t], i) =>
      h("button", { type: "button", class: (i === S.step ? "on " : i < S.step ? "done " : "") + "f-stepbtn", "data-sec": k, onclick: () => { S.step = i; render(); } }, `${i + 1}. ${t}`)));
    const body = cur[0] === "review"
      ? h("div", {}, h("h2", {}, "Review"), h("pre", { class: "f-yaml" }), destPanel())
      : section(cur[0]);
    const nav = h("div", { class: "navbtns" },
      h("button", { type: "button", class: "btn ghost", disabled: S.step === 0, onclick: () => { S.step--; render(); } }, "← Back"),
      S.step < steps.length - 1 ? h("button", { type: "button", class: "btn", onclick: () => { S.step++; render(); } }, "Next →") : h("span"));
    return h("div", { class: "fB" }, bar, body, nav);
  }
  function layoutC() {
    const left = h("div", {}, SECTIONS.map(([k, t], i) => {
      const s = section(k); s.querySelector("h2").remove();
      return h("details", { open: i === 0 }, h("summary", {}, t, " ", h("span", { class: "cnt f-cnt", "data-sec": k })), s);
    }));
    let timer;
    const ta = h("textarea", { class: "yaml-edit", spellcheck: "false", oninput: (ev) => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        try { S.rec = jsyaml.load(ev.target.value) || {}; delete S.rec.id; render(true); }
        catch (ex) { root.querySelector(".errs").textContent = "YAML: " + ex.message; }
      }, 400);
    } });
    const right = h("div", { class: "right" }, h("h3", {}, "Record YAML (editable: paste or type, the form follows)"), ta, h("div", { class: "errs" }), destPanel());
    return h("div", { class: "fC" }, left, right);
  }

  function render(keepYamlEditor) {
    root = layoutRoot();
    if (!root) return;
    const layout = root.dataset.layout;
    const scroll = window.scrollY;
    const old = keepYamlEditor && root.querySelector("textarea.yaml-edit");
    document.querySelectorAll(".submit-root").forEach((r) => r.replaceChildren());
    const tasks = h("datalist", { id: "f-tasks" }, Object.entries(REG.tasks).map(([t, n]) => h("option", { value: t }, n)));
    root.append(topBar(), tasks, { A: layoutA, B: layoutB, C: layoutC }[layout]());
    if (old) root.querySelector("textarea.yaml-edit").replaceWith(old);
    changed(false, !!old);
    window.scrollTo(0, scroll);
  }

  // after every edit: re-validate, mark fields, refresh previews
  function changed(idMayChange, skipYamlEditor) {
    if (!root) return;
    validate();
    const { yaml, files } = output();
    root.querySelectorAll(".f-bad").forEach((el) => el.classList.remove("f-bad"));
    root.querySelectorAll(".f-err").forEach((el) => (el.textContent = ""));
    const perSec = {};
    for (const er of S.errors) {
      const top = er.path.split("/")[1];
      const sec = (SECTIONS.find((s) => s[2].includes(top)) || ["other"])[0];
      perSec[sec] = (perSec[sec] || 0) + 1;
      const el = root.querySelector(`[data-path="${er.path}"]`) || root.querySelector(`[data-path="/${top}"]`);
      if (el) { el.classList.add("f-bad"); const m = el.querySelector(":scope > .f-err"); if (m && !m.textContent) m.textContent = er.msg; }
    }
    root.querySelectorAll(".f-cnt").forEach((el) => (el.textContent = perSec[el.dataset.sec] ? `(${perSec[el.dataset.sec]})` : ""));
    root.querySelectorAll(".f-stepbtn").forEach((el) => el.classList.toggle("err", !!perSec[el.dataset.sec]));
    root.querySelectorAll("pre.f-yaml").forEach((el) => (el.textContent = files.map((f) => `# ${f.path}\n${f.text}`).join("\n")));
    const ta = root.querySelector("textarea.yaml-edit");
    if (ta && !skipYamlEditor && document.activeElement !== ta) ta.value = yaml;
    const errs = root.querySelector(".errs");
    if (errs) errs.textContent = S.errors.map((e) => `${e.path || "/"}: ${e.msg}`).join("\n") || "";
    if (errs) errs.style.whiteSpace = "pre-wrap";
    const st = root.querySelector(".f-status");
    if (st) { st.textContent = S.errors.length ? `${S.errors.length} problem(s)` : "✓ valid against FDIS Registry Profile v0.1"; st.className = "f-status " + (S.errors.length ? "bad" : "ok"); }
    if (idMayChange) { const idEl = root.querySelector(".f-id"); if (idEl) idEl.value = currentId() || "(assigned from the primary Task)"; root.querySelector(".f-top b").textContent = S.editing ? `Editing ${S.editing}` : `New Research Project ${currentId() ? "→ " + currentId() : ""}`; }
    root.querySelectorAll(".dest").forEach((d) => d.redraw && !d.contains(document.activeElement) && d.redraw());
  }

  document.addEventListener("variantchange", () => render());
  render();
})();
