"""Write EVIDENCE.md: one retrieval entry per cited page or web source of the period Sankeys
(citation, original title, DOI/URL, page locators, diagrams, what each page supports).
Page images are not published; regenerate them locally with capture_evidence_pages.py / render_web_evidence.js.
Run from project root: python3 04_pipeline/scripts/build_evidence_index.py <references.json> <reference_list.csv> <out.md>"""
import csv, json, sys
refs = json.load(open(sys.argv[1], encoding="utf-8"))
bib = {r["id"]: r for r in csv.DictReader(open(sys.argv[2], encoding="utf-8-sig"))}
# Diagram reference ID -> bibliography ID in 00_index/reference_list.csv (None = web dataset not in the list)
BIB = {"R01": "R01", "R02": "R04", "R03": "R03", "R04": "R10", "R05": "R08", "R06": "R05", "R07": "R06",
       "R08": "R11", "R09": "R14", "R10": None, "R11": None, "R12": "R13", "R13": "R07"}
cell = lambda s: str(s).replace("|", "\\|")
L = ["# Evidence index: Gougra period Sankeys", "",
     "Every number on the three diagrams carries a reference ID `[R##]`. This file lists, for each ID, the full citation, "
     "the original title and DOI/URL (from `00_index/reference_list.csv`), and each cited page with the diagrams it feeds and what it supports. "
     "Page images of the sources are not published (copyright); see *Regenerate page images* at the end.", "",
     "Diagrams: `1` = before 1958, `2` = after 1958, `3` = after 2039 return.", ""]
for rid, r in refs.items():
    b = bib.get(BIB[rid]) if BIB[rid] else None
    L += [f"## {rid} · {r['token']} {r['year']}", "", f"- Citation: {r['citation']}"]
    if b:
        L.append(f"- Bibliography: `{b['id']}` in `reference_list.csv` · {b['author']} ({b['year']}). *{b['title']}*."
                 + (f" {b['container']}" if b["container"] else "") + (f", {b['volume_issue_pages']}" if b["volume_issue_pages"] else "") + ".")
    url = r.get("url") or (b["doi_url"] if b else "")
    L.append(f"- DOI/URL: {url}" if url else "- DOI/URL: none recorded")
    if r["type"] == "pdf":
        L.append(f"- Local copy (not published): `{r['path']}`")
    else:
        L.append(f"- Retrieved {r['retrieved']}; archived response: `04_pipeline/work/web_sources/{r['archive']}`" + (" (not published)" if r["archive"].endswith(".txt") else ""))
    off = r.get("printed_offset", 0)
    L += ["", "| Locator | Diagrams | Supports |", "|---|---|---|"]
    for pg, what in r["pages"].items():
        loc = pg if pg.startswith("web") else f"PDF p. {pg}" + (f" (printed p. {int(pg) + off})" if off else "")
        used = "; ".join(sorted(u.split()[0] for u in r.get("used_in", {}).get(pg, "").split("; ") if u))
        L.append(f"| {loc} | {used} | {cell(what)} |")
    L.append("")
L += ["## Regenerate page images", "",
      "Images go to a git-ignored folder; never commit them.", "", "```",
      "python3 04_pipeline/scripts/capture_evidence_pages.py 02_outputs/gougra_period_sankeys/references.json 04_pipeline/work/evidence 150   # needs pdftoppm",
      "node 04_pipeline/scripts/render_web_evidence.js 02_outputs/gougra_period_sankeys/references.json 04_pipeline/work/web_sources 04_pipeline/work/evidence   # needs playwright",
      "```", "", "Image names: `R{nn}_{token}_{year}_p{NNN}.png` (PDF page index, 1-based) or `..._web{NN}.png`.", ""]
open(sys.argv[3], "w", encoding="utf-8").write("\n".join(L))
