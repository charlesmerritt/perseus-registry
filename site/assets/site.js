// Directory and People table helpers: filter box and click-to-sort headers.
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
