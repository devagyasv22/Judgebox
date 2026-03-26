# Manual testing checklist (responsive UI)

Use browser devtools device emulation and real devices where possible.

## Breakpoints

- **Mobile:** &lt; 576px — hamburger nav, stacked columns, touch targets ≥ 44px for primary actions.
- **Tablet:** 576px–768px — two-column layouts where defined; filters sidebar stacks above list.
- **Desktop:** &gt; 768px — full navbar search, multi-column contest and problem layouts.

## Pages

- [ ] **Home** — hero, stats, featured carousel, announcements, quick contest card.
- [ ] **Search** (`/search/?q=`) — problems, contests, users lists.
- [ ] **Problems** — sidebar filters, AJAX apply, grid/list toggle, API `/problems/api/`.
- [ ] **Problem detail** — statement tabs, CodeMirror theme/font, run custom / run tests, AI review (if API key set).
- [ ] **Playground** (`/compiler/`) — split layout, run, result page link.
- [ ] **Contests list** — tabs, cards, links to detail.
- [ ] **Contest detail** — register, countdown, enter contest, standings link.
- [ ] **Contest dashboard / problem** — sidebar, submit, standings.
- [ ] **Standings** — table loads, optional AJAX refresh.
- [ ] **Submissions review** — filters, code collapse.
- [ ] **Dashboard / profile / edit profile / auth / community** — forms and navigation.

## Accessibility spot-checks

- [ ] Keyboard: Tab through navbar, forms, and modals; focus visible.
- [ ] Screen reader: nav landmark, search `aria-label`, icon-only buttons have `title`/`aria-label` where used.

## Database note

If you see **`OperationalError: no such column: contests_contest.slug`** (or similar), your `db.sqlite3` was created from an **older** contests schema than this repo. Back it up and recreate:

```bash
mv db.sqlite3 db.sqlite3.bak
python manage.py migrate
```

Then create a superuser again if needed: `python manage.py createsuperuser`.
