const fs = require('fs');

const initialJSON = `[{"id": 60, "title": "Comparison Task #60", "slug": "comparison-task-60", "difficulty": "Medium", "difficulty_key": "medium", "tags": ["math", "comparisons"], "acceptance_rate": null, "submission_count": 0, "discussion_count": 0, "user_status": "none", "url": "/problems/60/"}, {"id": 59, "title": "Square Sum Task #59", "slug": "square-sum-task-59", "difficulty": "Easy", "difficulty_key": "easy", "tags": [], "acceptance_rate": null, "submission_count": 0, "discussion_count": 0, "user_status": "none", "url": "/problems/59/"}]`;

const results = JSON.parse(initialJSON);

function esc(s) {
    // Mock esc for node
    return String(s).replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function badgeClass(d) {
if (d === "easy") return "badge-diff-easy";
if (d === "hard") return "badge-diff-hard";
return "badge-diff-medium";
}

function statusIcon(st) {
if (st === "solved") return '<i class="fa-solid fa-check text-success" title="Solved" aria-label="Solved"></i>';
if (st === "attempted") return '<i class="fa-solid fa-clock-rotate-left text-warning" title="Attempted" aria-label="Attempted"></i>';
return '<i class="fa-regular fa-circle text-muted" title="Not started" aria-label="Not started"></i>';
}

function renderCard(p) {
const acc = p.acceptance_rate != null ? p.acceptance_rate + "%" : "—";
const href = esc(p.url || ("/problems/" + p.id + "/"));
return (
  '<a class="oj-card oj-card-link p-3 h-100 d-flex flex-column" href="' + href + '" aria-label="Open problem: ' + esc(p.title || '') + '">' +
    '<div class="d-flex justify-content-between gap-2 mb-2">' +
      '<div class="fw-semibold">' + esc(p.title || "Untitled") + "</div>" +
      '<span class="badge ' + badgeClass(p.difficulty_key) + '">' + esc(p.difficulty) + "</span>" +
    "</div>" +
    '<div class="small text-muted mb-2">' + (p.tags && p.tags.length ? esc(p.tags.join(", ")) : "—") + "</div>" +
    '<div class="mt-auto d-flex justify-content-between small">' +
      '<span>Acceptance: ' + esc(String(acc)) + "</span>" +
      '<span>Subs: ' + p.submission_count + "</span>" +
      "<span>" + statusIcon(p.user_status) + "</span>" +
    "</div>" +
  "</a>"
);
}

try {
    results.forEach(function (p) {
        console.log("Rendering:", p.title);
        const html = renderCard(p);
        console.log("HTML OK length:", html.length);
    });
    console.log("Success! No JS crash in rendering string.");
} catch (e) {
    console.error("Crash!", e);
}
