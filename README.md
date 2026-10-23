# URBE Lab website

Source for <https://urbe-lab.github.io>, built with [Quarto](https://quarto.org) and published with GitHub Pages. The site is currently offline pending institutional approval; publishing is manual only (Actions → "Build and publish site" → Run workflow). Nothing needs to be installed locally: edit files in the GitHub web editor or in a Codespace.

## One-time setup

1. In the `URBE-Lab` organization, create a **public** repository named exactly `urbe-lab.github.io`.
2. Upload these files (or push with git) to the `main` branch.
3. Repository **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Check the **Actions** tab: the first run takes ~2 minutes. The site will be live at <https://urbe-lab.github.io>.

## Structure

| File / folder | What it is |
|---|---|
| `_quarto.yml` | Site settings and sidebar menu |
| `index.qmd` | Home page (shows the 4 latest news items) |
| `research.qmd` | Research themes, current projects, funding |
| `team.qmd` + `team/` | Team page; one `.qmd` file per person |
| `publications.qmd` | Publication list (APA, by year) |
| `news.qmd` + `news/` | News list; one `.qmd` file per item |
| `join.qmd` | Opportunities and how to apply |
| `teaching.qmd` | Courses and mentoring |
| `pi.qmd` | PI profile |
| `images/` | Logo, photos (`images/team/` for headshots) |
| `files/` | Downloadable files (e.g., CV PDF) |
| `styles/` | Colors and fonts (light and dark mode) |

## Common edits

- **Add a team member:** copy `team/_template.qmd` and follow the instructions inside.
- **Add news:** copy `news/_template.qmd` and follow the instructions inside.
- **Add a paper:** add an entry under the right year in `publications.qmd`.
- **Placeholders:** text marked `[...]{.ph}` shows highlighted in yellow on the site. Search the repo for `{.ph}` to find what is left.

## News bot (papers and NIH grants)

Every Monday, `.github/workflows/check-news.yml` runs `scripts/check_news.py`. It looks for new papers (PubMed name search, plus ORCID and Crossref once an ORCID iD is set) and new NIH awards (NIH RePORTER), drafts a news item and a publications entry for each, and opens a **pull request**. Nothing is published until someone reviews and merges it.

- **Settings:** `news-bot.json` (ORCID iD, PubMed query, NIH PI name).
- **First run:** Actions → "Check for new papers and grants" → Run workflow with **seed** checked. This records everything already out as known, so old papers don't become news.
- **One-time permission:** Settings → Actions → General → Workflow permissions → check "Allow GitHub Actions to create and approve pull requests" (for the organization and the repository).
- **Classification:** first- or last-author papers are labeled Publication; others are labeled Collaborator paper. Co-first and senior-author marks must be added by hand.
- **Not covered:** non-NIH grants, NIH awards where you are not a listed PI (Co-I roles, P30 pilot sub-awards), conferences, and awards. Add those with `news/_template.qmd`.
- GitHub pauses scheduled workflows after 60 days without repository activity; re-enable them in the Actions tab if that happens.

## Preview locally (optional)

With Quarto installed: `quarto preview`.
