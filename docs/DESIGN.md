# Devagya OJ — UI design notes

## Color palette (CSS variables in `static/css/main.css`)

| Token | Dark default | Usage |
|-------|----------------|-------|
| `--bg-root` | `#0f0f0f` | Page background |
| `--bg-surface` | `#141414` | Cards / panels |
| `--bg-elevated` | `#1a1a1a` | Inputs, nested surfaces |
| `--border` | `#2a2a2a` | Borders |
| `--text` | `#e8e8ea` | Primary text |
| `--text-muted` | `#9ca3af` | Secondary text |
| `--accent` | `#3b82f6` | Primary actions, links |
| `--accent-2` | `#8b5cf6` | Gradient partner |
| `--success` | `#22c55e` | Success / AC |
| `--warning` | `#eab308` | Warnings / TLE |
| `--danger` | `#ef4444` | Errors / WA |

Light theme overrides the same variables when `html[data-theme="light"]` is set (toggle in the navbar).

## Reusable patterns

- **Difficulty badges:** `badge-diff-easy`, `badge-diff-medium`, `badge-diff-hard` (semantic colors).
- **Verdict badges:** `verdict-ac`, `verdict-wa`, `verdict-tle`, `verdict-ce`.
- **Cards:** `oj-card` + optional `oj-card-header`.
- **Primary CTA:** `btn-oj-primary`.
- **Layout:** Bootstrap 5.3 grid; main content uses `.oj-main` with top padding for the fixed navbar.

## Icons & fonts

- Font Awesome 6 (CDN) for icons.
- System UI stack via `--font`.

## JavaScript modules

- `static/js/main.js` — theme persistence (`localStorage`), keyboard shortcuts (Ctrl/Cmd+Enter submits when `[data-submit-code]` exists).
- `static/js/utils.js` — `OJ.toast`, `OJ.copyText`, `OJ.debounce`, cookie helper.
- `static/js/contest.js` — contest countdown (`#contest-countdown` + `data-end` ISO timestamp), standings polling (`#standings-body` + `data-poll-url`).
