// Layout switcher (until layouts are chosen, issue 0007): ?variant=A|B|C, floating bar, ← → keys.
(function () {
  const secs = [...document.querySelectorAll("section.variant")];
  const keys = secs.map((s) => s.dataset.variant);
  const params = new URLSearchParams(location.search);
  let cur = keys.includes(params.get("variant")) ? params.get("variant") : keys[0];

  const bar = document.createElement("div");
  bar.className = "proto-switcher";
  bar.innerHTML = '<button aria-label="previous variant">←</button><span></span><button aria-label="next variant">→</button>';
  document.body.appendChild(bar);
  const [prev, label, next] = bar.children;

  function show(k) {
    cur = k;
    secs.forEach((s) => (s.hidden = s.dataset.variant !== k));
    const s = secs.find((s) => s.dataset.variant === k);
    label.textContent = keys.length > 1 ? `${k} (${s.dataset.name}) · ${keys.indexOf(k) + 1}/${keys.length}` : `${s.dataset.name}`;
    const p = new URLSearchParams(location.search);
    p.set("variant", k);
    history.replaceState(null, "", "?" + p + location.hash);
    // carry the variant across internal links so a reviewer stays in one layout
    document.querySelectorAll("a[href]").forEach((a) => {
      const h = a.getAttribute("href");
      if (/^https?:|^#|^mailto:/.test(h)) return;
      const [rest, hash = ""] = h.split("#");
      const [path, q = ""] = rest.split("?");
      const ap = new URLSearchParams(q);
      ap.set("variant", k);
      a.setAttribute("href", path + "?" + ap + (hash ? "#" + hash : ""));
    });
    document.dispatchEvent(new CustomEvent("variantchange", { detail: k }));
  }
  const step = (d) => show(keys[(keys.indexOf(cur) + d + keys.length) % keys.length]);
  prev.onclick = () => step(-1);
  next.onclick = () => step(1);
  if (keys.length < 2) prev.disabled = next.disabled = true;
  document.addEventListener("keydown", (ev) => {
    const t = ev.target;
    if (t.closest && t.closest("input,textarea,select,[contenteditable]")) return;
    if (ev.key === "ArrowLeft") step(-1);
    if (ev.key === "ArrowRight") step(1);
  });
  show(cur);
})();

// directory table helpers
function filterRows(input) {
  const q = input.value.toLowerCase();
  input.parentElement.querySelectorAll("table.dir tbody tr").forEach((tr) => {
    tr.hidden = q && !tr.textContent.toLowerCase().includes(q);
  });
}
document.querySelectorAll("table.sortable th").forEach((th, i) => {
  th.onclick = () => {
    const tb = th.closest("table").tBodies[0];
    const dir = (th.dataset.dir = th.dataset.dir === "1" ? "-1" : "1");
    [...tb.rows]
      .sort((a, b) => {
        const k = (r) => r.cells[i].dataset.sort ?? r.cells[i].textContent;
        return String(k(a)).localeCompare(String(k(b)), undefined, { numeric: true }) * dir;
      })
      .forEach((r) => tb.appendChild(r));
  };
});
