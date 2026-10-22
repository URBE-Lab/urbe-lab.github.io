#!/usr/bin/env python3
"""Publications bot for the URBE Lab website.

Looks for new papers (ORCID, Crossref, PubMed) and new NIH awards (NIH RePORTER),
then drafts publication entries and lists new awards. It never publishes anything:
the GitHub workflow opens a pull request for a person to review and merge.

Settings live in news-bot.json. Already-seen items live in data/known_*.txt.
First run (or --seed): records everything currently found as "known" and
drafts nothing, so the existing record is not re-added.

Standard library only, so it runs on a plain GitHub runner.
"""
import argparse
import datetime as dt
import html
import json
import pathlib
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "news-bot.json").read_text())
DATA = ROOT / "data"
KNOWN_DOIS = DATA / "known_dois.txt"
KNOWN_GRANTS = DATA / "known_grants.txt"
PR_BODY = ROOT / ".newsbot_pr_body.md"
UA = f"URBE-Lab-website-newsbot/1.0 (mailto:{CFG.get('contact_email', '')})"

warnings = []


# ---------- helpers ----------

def get_json(url, payload=None, headers=None):
    data = json.dumps(payload).encode() if payload is not None else None
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if payload is not None:
        hdrs["Content-Type"] = "application/json"
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def norm_doi(d):
    d = d.strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def read_set(path):
    if not path.exists():
        return None
    return {l.strip() for l in path.read_text().splitlines() if l.strip()}


def write_set(path, items):
    DATA.mkdir(exist_ok=True)
    path.write_text("\n".join(sorted(items)) + "\n")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def safe(source, fn, *a):
    try:
        return list(fn(*a))
    except Exception as e:  # one source failing should not stop the others
        warnings.append(f"{source}: {e}")
        return []


# ---------- paper sources ----------

def dois_orcid(orcid):
    j = get_json(f"https://pub.orcid.org/v3.0/{orcid}/works")
    for g in j.get("group", []):
        for eid in g.get("external-ids", {}).get("external-id", []):
            if eid.get("external-id-type") == "doi":
                yield norm_doi(eid["external-id-value"])


def dois_crossref_orcid(orcid, since):
    q = f"https://api.crossref.org/works?filter=orcid:{orcid},from-pub-date:{since}&rows=100&select=DOI"
    for it in get_json(q)["message"]["items"]:
        yield norm_doi(it["DOI"])


def dois_openalex(orcid, since):
    params = urllib.parse.urlencode({
        "filter": f"author.orcid:{orcid},from_publication_date:{since}",
        "per_page": 200, "select": "doi", "mailto": CFG.get("contact_email", ""),
    })
    for it in get_json(f"https://api.openalex.org/works?{params}")["results"]:
        if it.get("doi"):
            yield norm_doi(it["doi"])


def dois_pubmed(query, since):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    params = urllib.parse.urlencode({
        "db": "pubmed", "term": query, "retmode": "json", "retmax": 100,
        "datetype": "pdat", "mindate": since.replace("-", "/"), "maxdate": "3000",
    })
    ids = get_json(f"{base}esearch.fcgi?{params}")["esearchresult"]["idlist"]
    if not ids:
        return
    s = get_json(f"{base}esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids)}")["result"]
    for pid in s.get("uids", []):
        for aid in s[pid].get("articleids", []):
            if aid.get("idtype") == "doi":
                yield norm_doi(aid["value"])


def crossref_record(doi):
    return get_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")["message"]


# ---------- formatting ----------

def initials(given):
    parts = []
    for word in (given or "").replace(".", " ").split():
        sub = [p for p in word.split("-") if p]
        parts.append("-".join(f"{p[0].upper()}." for p in sub))
    return " ".join(parts)


def is_pi(a):
    orcid = CFG.get("orcid")
    if orcid and orcid in (a.get("ORCID") or ""):
        return True
    return (a.get("family", "").lower() == CFG["author_last_name"].lower()
            and (a.get("given") or " ")[0].upper() == CFG["author_first_initial"].upper())


def apa_authors(authors):
    names = []
    for a in authors:
        n = f"{a.get('family', a.get('name', '?'))}, {initials(a.get('given'))}".rstrip(", ")
        names.append(f"**{n}**" if is_pi(a) else n)
    if len(names) == 1:
        return names[0]
    if len(names) <= 20:
        return ", ".join(names[:-1]) + ", & " + names[-1]
    return ", ".join(names[:19]) + ", . . . " + names[-1]


def pub_date(rec):
    for key in ("published-print", "published-online", "published", "issued"):
        parts = (rec.get(key) or {}).get("date-parts", [[None]])[0]
        if parts and parts[0]:
            y = parts[0]
            m = parts[1] if len(parts) > 1 else 1
            d = parts[2] if len(parts) > 2 else 1
            return dt.date(y, m, d)
    return dt.date.today()


def apa_entry(rec, doi):
    title = strip_tags((rec.get("title") or ["(untitled)"])[0]).rstrip(".")
    journal = strip_tags((rec.get("container-title") or [""])[0])
    vol, issue = rec.get("volume"), rec.get("issue")
    pages = rec.get("page") or rec.get("article-number")
    src = f"*{journal}"
    src += f", {vol}*" if vol else "*"
    if issue:
        src += f"({issue})"
    if pages:
        src += f", {pages.replace('-', '–')}"
    year = pub_date(rec).year
    return f"{apa_authors(rec.get('author', []))} ({year}). {title}. {src}. <https://doi.org/{doi}>"


# ---------- writers ----------

def sort_key(entry):
    t = unicodedata.normalize("NFKD", entry.replace("*", "")).encode("ascii", "ignore").decode()
    return t.lower()


def add_to_publications(entry, year):
    p = ROOT / "publications.qmd"
    s = p.read_text()
    block = re.compile(rf"(::: yr\n{year}\n:::\n\n:::: entries\n)(.*?)(\n::::)", re.S)
    m = block.search(s)
    if m:
        items = [e.strip() for e in m.group(2).split("\n\n") if e.strip()] + [entry]
        items.sort(key=sort_key)
        s = s[:m.start(2)] + "\n\n".join(items) + s[m.end(2):]
    else:
        new = f"::::: pub-year\n::: yr\n{year}\n:::\n\n:::: entries\n{entry}\n::::\n:::::\n\n"
        years = [(mm.start(), int(mm.group(1))) for mm in
                 re.finditer(r"::::: pub-year\n::: yr\n(\d{4})", s)]
        pos = next((i for i, y in years if y < year), None)
        s = s[:pos] + new + s[pos:] if pos is not None else s.rstrip() + "\n\n" + new
    p.write_text(s)


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", action="store_true", help="record current items as known; draft nothing")
    args = ap.parse_args()

    since = (dt.date.today() - dt.timedelta(days=CFG.get("lookback_days", 180))).isoformat()
    orcid = CFG.get("orcid", "").strip()
    if not orcid:
        warnings.append("No ORCID iD set in news-bot.json; using the PubMed name search only.")

    found = set(safe("PubMed", dois_pubmed, CFG["pubmed_query"], since))
    if orcid:
        found |= set(safe("ORCID", dois_orcid, orcid))
        found |= set(safe("Crossref", dois_crossref_orcid, orcid, since))
        found |= set(safe("OpenAlex", dois_openalex, orcid, since))

    grants = {}
    nih = CFG.get("nih_pi")
    if nih:
        def nih_search():
            fy = dt.date.today().year
            payload = {"criteria": {"pi_names": [nih], "fiscal_years": [fy - 1, fy, fy + 1]},
                       "limit": 50, "offset": 0}
            for r in get_json("https://api.reporter.nih.gov/v2/projects/search", payload)["results"]:
                yield r
        for r in safe("NIH RePORTER", nih_search):
            key = r.get("core_project_num") or r.get("project_num")
            if key:
                grants.setdefault(key, r)

    known_dois, known_grants = read_set(KNOWN_DOIS), read_set(KNOWN_GRANTS)
    seeding = args.seed or known_dois is None
    lines = []

    if seeding:
        write_set(KNOWN_DOIS, (known_dois or set()) | found)
        write_set(KNOWN_GRANTS, (known_grants or set()) | set(grants))
        lines.append(f"Seed run: recorded {len(found)} papers and {len(grants)} NIH projects "
                     "as already known. Nothing drafted.")
    else:
        new_dois = sorted(found - known_dois)
        for doi in new_dois:
            try:
                rec = crossref_record(doi)
            except Exception as e:
                warnings.append(f"Crossref lookup failed for {doi}: {e}")
                continue
            if rec.get("type") != "journal-article":
                known_dois.add(doi)
                continue
            authors = rec.get("author", [])
            pos = [i for i, a in enumerate(authors) if is_pi(a)]
            if not pos:  # name search matched someone else
                known_dois.add(doi)
                lines.append(f"- Skipped `{doi}`: no matching author in the record (likely a namesake).")
                continue
            lead = pos[0] in (0, len(authors) - 1)
            kind = "Publication" if lead else "Collaborator paper"
            date = pub_date(rec)
            entry = apa_entry(rec, doi)
            journal = strip_tags((rec.get("container-title") or [""])[0])
            short = strip_tags((rec.get("title") or [""])[0])
            add_to_publications(entry, date.year)
            known_dois.add(doi)
            lines.append(f"- **{kind}** — {short} ({journal}, {date:%Y-%m}). Added to `publications.qmd`. "
                         "Check: title capitalization, co-first/senior marks, author list.")
        new_grants = sorted(set(grants) - known_grants)
        for key in new_grants:
            r = grants[key]
            title = (r.get("project_title") or key).strip()
            ic = (r.get("agency_ic_admin") or {}).get("abbreviation", "NIH")
            known_grants.add(key)
            lines.append(f"- **Grant** — {title} ({ic} {key}). Not added anywhere: "
                         "add it to Funding in `research.qmd` by hand if wanted.")
        write_set(KNOWN_DOIS, known_dois)
        write_set(KNOWN_GRANTS, known_grants)
        if not new_dois and not new_grants:
            lines.append("Nothing new found.")

    body = ["## Publications bot results", ""] + lines
    if warnings:
        body += ["", "### Warnings"] + [f"- {w}" for w in warnings]
    body += ["", "Edit the drafted entries in this pull request if needed, then merge to publish. "
             "Close it to discard."]
    PR_BODY.write_text("\n".join(body) + "\n")
    print("\n".join(body))


if __name__ == "__main__":
    sys.exit(main())
