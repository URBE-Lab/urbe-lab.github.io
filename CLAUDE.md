# CLAUDE.md: URBE Lab website

Handoff notes for Claude Code sessions working on this repository. Read this first.

## What this is

Public website for the URBE Lab (PI: Pablo Knobel, PhD, Instructor, Department of Environmental Medicine, Icahn School of Medicine at Mount Sinai). Built with **Quarto** (website project) and deployed to GitHub Pages at <https://urbe-lab.github.io> by `.github/workflows/publish.yml`. **Taken down Oct 2026** pending Mount Sinai approval: publishing is manual only (push trigger removed) and the Pages site was unpublished.

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
| `index.qmd` | Home: kicker label and intro (no headline or subheadline: Pablo's choice) |
| `research.qmd` | Research themes (`.theme-grid` / `.theme-card`), methods, funding |
| `team.qmd`, `team/*.qmd` | Team grid; one file per person; `order:` sets position; `team/_template.qmd` for new people |
| `publications.qmd` | APA list grouped in year blocks (`::::: pub-year` / `::: yr` / `:::: entries`), PI name in bold, entries alphabetical within year |
| `join.qmd` | Opportunities (Teaching page removed Oct 2026) |
| `resources/*.qmd` | Resources sidebar section: Framework references, Data sources (placeholders) |
| `pi.qmd` | "About Pablo": bio, appointments, education, honors, service and appointments, media |
| `styles/light.scss`, `styles/dark.scss` | Theme colors and fonts (Bootstrap/Quarto variables + `--u-*` CSS variables) |
| `styles/custom.css` | Shared component styles |
| `scripts/check_news.py`, `news-bot.json`, `data/known_*.txt` | Publications bot (see below) |

## Design (style "C1", chosen Oct 2026)

- Dark teal sidebar and footer (`#10292a`) with the URBE • lab logo at the top.
- Colors: teal `#0f766e` (links, labels), amber `#b45309` text / `#f59e0b` lines (accents). Dark mode via the toggle.
- Fonts (Google Fonts): Space Grotesk (headings), Inter (body), DM Mono (labels, dates, years, roles).
- Components: monospace kicker labels; research cards = white with thin border and amber top stripe; team photos round with one teal ring for everyone; publications with a year column; news dates as `YYYY-MM` in amber monospace and type labels as amber outlined tags.
- No stat tiles (decided against for now).
- **Logo:** final files in `images/logo/`: `urbe-logo-*` (mark + text), `urbe-wordmark-*` (text only), `urbe-mark-*` (mark only), favicons. Sidebar uses `urbe-logo-dark.svg` (menu is always dark); favicon `favicon.svg` + PNG fallbacks.

## Publications bot

`.github/workflows/check-news.yml` runs weekly (Mondays) and on demand. `scripts/check_news.py` (standard-library Python) searches PubMed, ORCID (`0000-0001-6902-0286`), Crossref, and OpenAlex (by ORCID) for new papers, and NIH RePORTER for new awards with Pablo as PI. It adds publication entries to `publications.qmd`, lists new NIH awards in the PR body (not added anywhere), and opens a PR for review. News drafting removed Oct 2026.

- Seed run (first time): run the workflow with **seed** checked so existing papers are recorded as known, not re-added. Known DOIs missing from the page must be added by hand.
- Co-first/senior marks and title capitalization need manual fixes in the PR.
- Google Scholar not used (no API; blocks bots). OpenAlex covers most of its extra items.
- Not covered: non-NIH grants, Co-I roles, P30 pilot sub-awards, conferences, awards (add manually).
- Status (Oct 2026): logic tested offline with mock data only; first live run not yet done.

## Open items

- Placeholders: lab culture text, team members and photos, Join page details, PI photo, CV PDF, faculty liaison start year, Resources page content. No LinkedIn or Bluesky links (Pablo's choice).
- Publications checked against Crossref (Oct 2026): every entry has a DOI; author lists are APA 7 (up to 20 authors, then ". . ." and the last author).
- Mount Sinai Website Governance policy (checked Oct 2026): independent sites showing Mount Sinai affiliation need explicit permission from Digital Marketing and Branding; questions to Conflicts.of.Interest@mssm.edu. Permission not yet requested. Do not use Mount Sinai logos.
