"""Build the abbreviation / company check table for the negotiation timeline.

Writes 02_outputs/timeline_abbreviations/timeline_abbreviations.csv and .svg.
Run from the project root: python3 04_pipeline/scripts/build_timeline_abbreviations.py
"""
import csv
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("02_outputs/timeline_abbreviations")

COLUMNS = [
    "timeline_label", "full_name_original", "description", "type", "timeline_events",
    "history_and_status", "local_evidence", "external_sources", "confidence", "notes",
]

# Savoy = R10 Savoy 2025 working paper; page numbers are PDF pages.
ROWS = [
    ["SIS", "Services industriels de Sierre",
     "Municipal utility (electricity) of the town of Sierre", "Municipal utility",
     "1908: takes over two Navizence water-power concessions from private holders (granted by Ayer and St-Jean)",
     "Later became Sierre-Energie SA (Siesa); Siesa merged with Energie de Sion-Région (esr) to form OIKEN SA (Sion). OIKEN now holds 1.0% of FMG",
     "Savoy p.77; Hoeffleur 1962 p.10 (\"Services Industriels de Sierre (SIS)\")",
     "https://1815.ch/news/wallis/aktuell/oiken ; https://www.alpiq.com/newsroom/media-releases/mottec-hydropower-plant-optimised-for-a-sustainable-energy-future",
     "High", "Year of the SIS→Siesa conversion not verified; the OIKEN merger was around 2018–2019"],
    ["AIAG", "Aluminium-Industrie-Aktien-Gesellschaft (French: S.A. pour l'Industrie de l'Aluminium)",
     "Swiss aluminium company with a smelter at Chippis", "Industrial company (aluminium)",
     "1905: seven municipalities grant the Navizence water-power concession for the Vissoie–Chippis stretch, 99 years",
     "Founded in Zürich in 1889; renamed Alusuisse in 1963; Alusuisse-Lonza Group in 1990; Algroup in 1998; acquired by Alcan in October 2000. Held 30% of FMG when FMG was founded in 1952",
     "Savoy p.77 (\"ancien nom d'AluSuisse, puis d'Algroup\"); Robert 1962 p.2 (FMG shareholder list)",
     "https://hls-dhs-dss.ch/fr/articles/041942 ; https://www.sec.gov/Archives/edgar/data/0000004285/000095012301002940/m09446e10-k405.txt",
     "High", ""],
    ["EOS", "S.A. l'Energie de l'Ouest-Suisse (Energie Ouest Suisse)",
     "Western Swiss power company, Lausanne", "Power company",
     "1945 Haute-Printse concession; 1951 Bornet water rights for electricity; 1963 compensation to FMM; 1990 connection-cost repayment from SEBA; 1992 WWF appeals withdrawn for a settlement; 2000 Nendaz storage and water supply",
     "Founded 14 March 1919; merged with Atel Holding in 2009 to form Alpiq. The former shareholders' holding vehicle is now EOS Holding SA",
     "Savoy p.7 (abbreviation list), p.24 note 13 (\"En 2009, EOS SA et Atel Holding SA fusionnent pour donner naissance à Alpiq SA\"), p.28",
     "https://www.isil.nb.admin.ch/en/institutions/energie-ouest-suisse-eos-documentation-ch-001187-x/ ; https://en.wikipedia.org/wiki/Alpiq",
     "High", "Events after 2009 should name Alpiq (the timeline's 2031 entry already does)"],
    ["FMG", "Forces Motrices de la Gougra SA",
     "Gougra hydropower company (Moiry dam; Mottec, Vissoie and Navizence plants)", "Hydropower company",
     "1953 takes over Isotherme's concessions; 2004/2009 80-year relicensing; 2006–07 snowmaking water; 2008 Niouc; 2013–16 WWF agreement; 2017 Briey; 2018 bisses convention; 2022 reversion price; 2039 and 2084 expiries",
     "Founded 1952. Initial shareholders: ATEL 30%, AIAG 30%, Louis de Roll 30%, Union Bank of Switzerland 6%, Sierre municipality 4%. Current shareholders: Alpiq 54%, Rhonewerke 27.5%, Anniviers 7.71%, Sierre 7.5%, Chippis 1.79%, OIKEN 1.0%, Chalais 0.5%",
     "Savoy p.7, p.78; Robert 1962 p.2; rights_dataset entities: fmg",
     "https://www.alpiq.com/newsroom/media-releases/mottec-hydropower-plant-optimised-for-a-sustainable-energy-future ; https://www.alpiq.com/fileadmin/ALPIQ/energy/assets/gougra/fmg_rapport_gestion_2025.pdf",
     "High", "FMG is the direct concession holder; Alpiq is the controlling shareholder, not the concession holder"],
    ["FMM", "Forces Motrices de Mauvoisin SA",
     "Mauvoisin hydropower company (Val de Bagnes), Sion", "Hydropower company",
     "1963: supplies Saxon with substitute water instead of the Printse (existing 350 L/s entitlement); EOS pays FMM compensation",
     "Still operating; Axpo Group holds about 68% (2019 figure); other shareholders not verified",
     "Savoy p.30, p.36 (\"Forces motrices de Mauvoisin (FMM)\")",
     "https://graph.swiss/companies/forces-motrices-de-mauvoisin-sa/1184678 ; https://www.axpo.com/group/en/news-and-stories/magazine/renewable-energy/nature-knows-no-mercy-extern.html",
     "High", ""],
    ["FMHL", "Forces Motrices Hongrin-Léman SA",
     "Hongrin–Léman pumped-storage company (Vaud)", "Hydropower company",
     "1948–1963 joint concession granted by Vaud and Fribourg; 2022→2023 deferred ecological flood release; 2023–2024 snowmaking agreement with TLML",
     "Founded 1963. Shareholders (2014): Romande Energie 41.13%, Alpiq 39.30%, Groupe E 13.13%, City of Lausanne (SiL) 6.43%; technical operation by HYDRO Exploitation SA",
     "Savoy p.7 (abbreviation list), p.57",
     "https://www.romande-energie.ch/images/Files/communiques_archives/140605_communique_fr.pdf ; https://www.lausanne.ch/vie-pratique/energies-et-eau/services-industriels/a-propos-sil/nos-activites/electricite/production/hydraulique/barrage-de-hongrin.html",
     "High", "Stakes are post-2014 capital increase figures and may have shifted slightly since"],
    ["SEBA", "Société d'extension de boissons alimentaires (now Aproz Sources Minérales SA)",
     "Aproz mineral water company, Nendaz", "Beverage company",
     "18 May 1990 tripartite agreement: Nendaz lets SEBA use the Bouillets source until 2031; SEBA repays EOS's connection costs",
     "Founded 1947 as SEBA, called Seba Aproz from 1958 and Aproz Sources Minérales SA from 2008; part of the Migros group since 1958 (now Migros Industrie)",
     "Savoy p.8 (abbreviation list), p.29 note 32, p.47",
     "https://business-monitor.ch/fr/companies/73576-aproz-sources-minerales-sa ; https://www.migrosindustrie.ch/ffb-group/en/?p=5256",
     "High", "Founding year differs between sources (1946 / 1947; commercial register entry 1956)"],
    ["WWF", "WWF (World Wide Fund for Nature)",
     "In Switzerland: WWF Suisse / Schweiz", "Environmental NGO (not a company)",
     "1992 Cleuson-Dixence appeals withdrawn for a settlement; 2004/2009 objection to the Navizence relicensing (filed late); 2013–2016 no appeal against the Vissoie–Niouc tunnel in return for Plats de la Lée restoration funding",
     "—",
     "Savoy p.24, p.37, p.104–105 (the source always writes just \"le WWF\")",
     "",
     "Medium", "Not a company. The source does not say whether the national organisation or the WWF Valais section acted; keeping \"WWF\" on the timeline is fine"],
    ["TLML", "Télé Leysin-Les Mosses-La Lécherette SA",
     "Leysin–Les Mosses lift company (Vaud)", "Lift company",
     "2023–2024: snowmaking water agreement with FMHL (160,000–200,000 m³/year); project withdrawn in 2024",
     "Formed in 2011 by merging Télé Leysin SA and Remontées mécaniques Mosses-Lécherette SA; still operating",
     "Savoy p.8 (abbreviation list), p.61, p.68",
     "https://www.alpesvaudoises.ch/en/pages/tlml ; https://latele.ch/actualite/articles/les-mosses-et-leysin-le-grand-recul-des-canons-a-neige-dans-la-montagne",
     "High", ""],
    ["Lonza", "Lonza SA / AG",
     "Chemical and pharmaceutical company (named directly, no abbreviation)", "Industrial company (chemicals)",
     "1908 Lower Printse: the concession Nendaz granted to a private holder is later taken over by Lonza; renounced in 1966",
     "Founded 1897 (power plant at Gampel); absorbed into Alusuisse in 1973/74; spun off and listed as Lonza Group AG in 1999",
     "Savoy p.23 (incl. note 12: 1966 renunciation letters to the cantonal government and Nendaz)",
     "https://hls-dhs-dss.ch/de/articles/041941/",
     "High", "From 1973 it belonged to the same group as Alusuisse, AIAG's successor"],
    ["Isotherme SA", "Isotherme SA",
     "Private company (no abbreviation)", "Company (activity unknown)",
     "After 1943: takes over the Gougra concessions that Grimentz and Ayer granted to private holders; transfers them to FMG in 1953",
     "In the early 1950s it also obtained Turtmänna concessions from three Turtmann-valley municipalities, all transferred to FMG in 1953. No later trace found",
     "Savoy p.77–78, p.116; rights_dataset entities: isotherme",
     "",
     "Medium", "No other sources found online; the timeline's wording matches the source"],
    ["Alpiq", "Alpiq SA (Alpiq Holding AG)",
     "Power group, Lausanne (no abbreviation)", "Power company",
     "2031: Cleuson / First Dixence concessions expire and assets revert to the public grantors",
     "Formed in 2009 by the merger of EOS and Atel; controlling shareholder of FMG (54%) and shareholder of FMHL (about 39%)",
     "Savoy p.24 note 13, p.28 (\"Alpiq SA (anciennement EOS)\"); rights_dataset entities: alpiq",
     "https://en.wikipedia.org/wiki/Alpiq",
     "High", ""],
    ["Zinal / Grimentz lift companies", "Remontées mécaniques de Zinal; Remontées mécaniques de Grimentz",
     "Zinal and Grimentz lift companies", "Lift companies",
     "2006–2007: FMG supplies snowmaking water to both companies, which pay for it",
     "Zinal agreement signed 2006, Grimentz agreement 2007; the two later merged into Remontées mécaniques Grimentz-Zinal (RMGZ)",
     "Savoy p.7 (RMGZ abbreviation), p.102–103; rights_dataset entities: zinal_lifts, grimentz_lifts, rmgz",
     "",
     "High", ""],
]


def text_width(s, size):
    w = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            w += size
        elif ch in "mwMW%":
            w += size * 0.9
        elif ch.isupper():
            w += size * 0.72
        elif ch in " .,;:’'|/()il":
            w += size * 0.32
        else:
            w += size * 0.6
    return w


def wrap(s, width, size):
    lines, cur = [], ""
    for ch in s:
        if text_width(cur + ch, size) > width:
            # Break Latin words at the last space when possible.
            cut = cur.rfind(" ") if ord(ch) < 0x2E80 and ch != " " else -1
            if cut > len(cur) // 3:
                lines.append(cur[:cut])
                cur = cur[cut + 1:] + ch
            else:
                lines.append(cur)
                cur = ch.lstrip()
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines or [""]


def build_svg(rows):
    size, lh, pad = 13, 18, 10
    # (header, source column index, width)
    cols = [("Timeline label", 0, 130), ("Full name (original)", 1, 270), ("Type", 3, 130),
            ("Events on the timeline", 4, 340), ("History and current status", 5, 420),
            ("Confidence / notes", None, 240)]
    x0, total_w = 24, sum(c[2] for c in cols)
    y = 30
    out = []
    out.append(f'<text x="{x0}" y="{y}" class="title">Timeline abbreviations and companies</text>')
    y += 22
    out.append(f'<text x="{x0}" y="{y}" class="sub">For the “Negotiation, concessions &amp; rights exchange” timeline. '
               f'Based on Savoy 2025, Robert 1962, Hoeffleur 1962 and public sources; checked 2026-10-09. '
               f'Source links are in the CSV of the same name.</text>')
    y += 18
    head_h = lh + 2 * pad
    out.append(f'<rect x="{x0}" y="{y}" width="{total_w}" height="{head_h}" class="head"/>')
    x = x0
    for name, _, w in cols:
        out.append(f'<text x="{x + pad}" y="{y + pad + size}" class="th">{escape(name)}</text>')
        x += w
    y += head_h
    for i, r in enumerate(rows):
        cells = []
        for name, idx, w in cols:
            if idx is None:
                cells.append([r[8]] + (wrap(r[9], w - 2 * pad, size) if r[9] else []))
            elif idx == 1:
                cells.append(wrap(r[1], w - 2 * pad, size) + wrap(r[2], w - 2 * pad, size - 1))
            else:
                cells.append(wrap(r[idx], w - 2 * pad, size))
        n = max(len(c) for c in cells)
        h = n * lh + 2 * pad
        cls = "row alt" if i % 2 else "row"
        out.append(f'<rect x="{x0}" y="{y}" width="{total_w}" height="{h}" class="{cls}"/>')
        x = x0
        for ci, ((name, idx, w), lines) in enumerate(zip(cols, cells)):
            n_full = len(wrap(r[1], w - 2 * pad, size)) if idx == 1 else len(lines)
            for li, line in enumerate(lines):
                cl = "abbr" if ci == 0 else ("muted" if idx == 1 and li >= n_full else "td")
                if ci == 5 and li == 0 and line == "Medium":
                    cl = "warn"
                out.append(f'<text x="{x + pad}" y="{y + pad + size + li * lh}" class="{cl}">{escape(line)}</text>')
            x += w
        out.append(f'<line x1="{x0}" y1="{y + h}" x2="{x0 + total_w}" y2="{y + h}" class="rule"/>')
        y += h
    x = x0
    for _, _, w in cols[:-1]:
        x += w
        out.append(f'<line x1="{x}" y1="{70}" x2="{x}" y2="{y}" class="vrule"/>')
    y += 26
    out.append(f'<text x="{x0}" y="{y}" class="sub">Confidence: High = full name in a local source and consistent public sources; '
               f'Medium = source wording only, or the entity type is qualified. WWF is an environmental NGO, not a company.</text>')
    W, H = x0 * 2 + total_w, y + 24
    style = """
    text{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;fill:#1f2933}
    .title{font-size:20px;font-weight:600}
    .sub{font-size:12px;fill:#52606d}
    .th{font-size:13px;font-weight:600;fill:#fff}
    .td{font-size:13px}
    .abbr{font-size:14px;font-weight:700;fill:#2f4b6e}
    .muted{font-size:12px;fill:#616e7c}
    .warn{font-size:13px;font-weight:600;fill:#a23b3b}
    .head{fill:#4d6e8f}
    .row{fill:#ffffff}
    .alt{fill:#f2f5f8}
    .rule{stroke:#cbd2d9;stroke-width:1}
    .vrule{stroke:#e4e7eb;stroke-width:1}
    """
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<style>{style}</style>\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
            + "\n".join(out) + "\n</svg>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "timeline_abbreviations.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(COLUMNS)
        w.writerows(ROWS)
    (OUT / "timeline_abbreviations.svg").write_text(build_svg(ROWS), encoding="utf-8")
    print(f"wrote {len(ROWS)} rows to {OUT}")


if __name__ == "__main__":
    main()
