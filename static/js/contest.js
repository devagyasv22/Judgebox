(function () {
  "use strict";

  function parseEndTime(el) {
    const iso = el.getAttribute("data-end");
    if (!iso) return null;
    return new Date(iso).getTime();
  }

  function formatRemaining(ms) {
    if (ms <= 0) return "00:00:00";
    const s = Math.floor(ms / 1000);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    const pad = function (n) {
      return n < 10 ? "0" + n : "" + n;
    };
    return pad(h) + ":" + pad(m) + ":" + pad(sec);
  }

  function tickTimer() {
    const el = document.getElementById("contest-countdown");
    if (!el) return;
    const end = parseEndTime(el);
    if (!end) return;
    function update() {
      const left = end - Date.now();
      el.textContent = formatRemaining(left);
      el.classList.remove("warn", "critical");
      if (left < 10 * 60 * 1000 && left > 0) el.classList.add("warn");
      if (left < 3 * 60 * 1000 && left > 0) el.classList.add("critical");
    }
    update();
    setInterval(update, 1000);
  }

  function pollStandings() {
    const table = document.getElementById("standings-body");
    if (!table) return;
    const url = table.getAttribute("data-poll-url");
    if (!url) return;
    const interval = parseInt(table.getAttribute("data-poll-ms") || "8000", 10);

    async function refresh() {
      try {
        const res = await fetch(url, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!res.ok) return;
        const data = await res.json();
        if (!data.rows) return;
        table.innerHTML = "";
        data.rows.forEach(function (r) {
          const tr = document.createElement("tr");
          tr.innerHTML =
            "<td>" +
            r.rank +
            "</td><td>" +
            escapeHtml(r.username) +
            "</td><td>" +
            r.solved +
            " / " +
            r.total +
            "</td><td>" +
            r.penalty +
            "</td>";
          table.appendChild(tr);
        });
      } catch (e) {}
    }

    setInterval(refresh, interval);
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  document.addEventListener("DOMContentLoaded", function () {
    tickTimer();
    pollStandings();
  });
})();
