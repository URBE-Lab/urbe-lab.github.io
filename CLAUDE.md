# CLAUDE.md: URBE Lab website

Handoff notes for Claude Code sessions working on this repository. Read this first.

## What this is

Public website for the URBE Lab (PI: Pablo Knobel, PhD, Instructor, Department of Environmental Medicine, Icahn School of Medicine at Mount Sinai). Built with **Quarto** (website project) and deployed to GitHub Pages at <https://urbe-lab.github.io> by `.github/workflows/publish.yml` on every push to `main`.

## Working rules

- **Never push to `main` directly.** Work on a branch and open a pull request; Pablo reviews and merges. Merging publishes.
- **Public repo:** never add PHI, identifiable data, unpublished results, pending-grant details, or student information without the person's consent.
- **Never invent facts** (dates, titles, roles, links). If something is unknown, leave a placeholder: `[Placeholder: what is needed]{.ph}` (renders highlighted in yellow). Search `{.ph}` to list what is left.
- Before opening a PR, run `quarto render` and confirm it builds with no warnings; check changed pages visually when layout or styling changed.
- Keep edits targeted; don't rewrite pages that weren't part of the request.
- US spelling, APA citation style.
- Pablo's preferences: concise replies, outline before large changes and wait for review, end each work cycle with a brief final review (writing, code, privacy, reproducibility; issues and easy fixes only).

## Structure

| Path | Purpose |
|---|---|
| `_quarto.yml` | Site config and sidebar menu |
| `index.qmd` | Home: kicker label, headline + subheadline (placeholders), intro, latest 4 news |
| `research.qmd` | Research themes (`.theme-grid` / `.theme-card`), methods, funding |
| `team.qmd`, `team/*.qmd` | Team grid; one file per person; `order:` sets position; `team/_template.qmd` for new people |
| `publications.qmd` | APA list grouped in year blocks (`::::: pub-year` / `::: yr` / `:::: entries`), PI name in bold, entries alphabetical within year |
| `news.qmd`, `news/*.qmd` | News table with Type column (`categories:`); `news/_template.qmd` lists allowed types: Publication, Collaborator paper, Conference, Grant, Award, Appointment, Lab |
| `join.qmd`, `teaching.qmd` | Opportunities; courses and mentoring |
| `pi.qmd` | "About Pablo": bio, appointments, education, honors, service and appointments, media |
| `styles/light.scss`, `styles/dark.scss` | Theme colors and fonts (Bootstrap/Quarto variables + `--u-*` CSS variables) |
| `styles/custom.css` | Shared component styles |
| `scripts/check_news.py`, `news-bot.json`, `data/known_*.txt` | News bot (see below) |

## Design (style "C1", chosen Oct 2026)

- Dark teal sidebar and footer (`#10292a`), text wordmark "URBE" with a "LAB · NYC" monospace subline.
- Colors: teal `#0f766e` (links, labels), amber `#b45309` text / `#f59e0b` lines (accents). Dark mode via the toggle.
- Fonts (Google Fonts): Space Grotesk (headings), Inter (body), DM Mono (labels, dates, years, roles).
- Components: monospace kicker labels; research cards = white with thin border and amber top stripe; team photos round with one teal ring for everyone; publications with a year column; news dates as `YYYY-MM` in amber monospace and type labels as amber outlined tags.
- No stat tiles (decided against for now).
- **Logo:** not decided. Four hand-drawn candidate marks were traced to SVG in a separate chat; the favicon `images/logo-mark.svg` is a placeholder.

## News bot

`.github/workflows/check-news.yml` runs weekly (Mondays) and on demand. `scripts/check_news.py` (standard-library Python) searches PubMed, ORCID (`0000-0001-6902-0286`), and Crossref for new papers, and NIH RePORTER for new awards with Pablo as PI. It drafts news items and publication entries and opens a PR for review.

- Seed run (first time): run the workflow with **seed** checked so existing papers are recorded as known, not announced.
- Lead (first/last author) → `Publication`; otherwise → `Collaborator paper`. Co-first/senior marks and title capitalization need manual fixes in the PR.
- Not covered: non-NIH grants, Co-I roles, P30 pilot sub-awards, conferences, awards (add manually).
- Status (Oct 2026): logic tested offline with mock data only; first live run not yet done.

## Open items

- Placeholders: home headline/subheadline and tagline, department link, lab culture text, team members and photos, Join page details, PI photo, links (Google Scholar, Mount Sinai profile, LinkedIn/Bluesky), CV PDF, faculty liaison start year, course additions.
- Publication entries to verify against PubMed (from CV): Environ Int 2025 vol. 185 and Ecotoxicol Environ Saf 2025 vol. 259 (volumes look like 2024/2023), Health & Place 2022 first-author name ("Núñez" vs "Fernández-Núñez"), J Urban Health 2025 pages "1–10"; four entries end in "et al."; no DOIs yet.
- Logo decision.
- Check Mount Sinai web/branding policy for lab sites.
