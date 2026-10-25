# Gougra period Sankey diagrams

Generated 2026-10-11. Three annual water-balance Sankey diagrams of the Gougra / Navizence system, all balanced to the same natural runoff (332.2 hm³/yr = BAFU MQN Navisence at Chippis + Turtmänna at Turtmann), so the periods can be compared. Every number on a diagram carries a reference ID `[R##]`; `EVIDENCE.md` gives each one's citation, DOI/URL and cited pages.

## Files
| Path | Content |
|---|---|
| `svg/gougra_sankey_1_before-1958.svg` | State c. 1950: AIAG run-of-river plant at Chippis (gallery ≤ 7 m³/s), no storage; Turtmänna used in its own valley (ITAG) |
| `svg/gougra_sankey_2_after-1958.svg` | Gougra scheme as commissioned 1958–61: design average year from Robert 1962, Table 2 |
| `svg/gougra_sankey_3_after-2039-return.svg` | After the upper-stage concessions revert to the grantors (31 Dec 2039): flows under today's rules in a mean year (v2 model), with grantor shares |
| `preview/*.png` | Raster previews of the three SVGs |
| `EVIDENCE.md` | For each reference ID: full citation, original title and DOI/URL, local file, cited pages (31 locators), which diagram uses each page, what it supports |
| `references.json` | Reference register (citations, pages, diagrams) used by the evidence scripts |
| `period_models.json` | Nodes, links (true `value`, drawn `display`, `uncertain`), notes and totals of the three diagrams |

The SVGs are editable: live text, explicit colours, named layers (`title`, `legend`, `sankey` › `column-heads`, `links`, `nodes`, `label-halos`, `labels`, plus `grantor-shares` and `notes`); each link and node has an id such as `link_moiry_to_mottec`. Fonts: Source Serif 4, Source Sans 3, IBM Plex Mono (Google Fonts). Hatched bands are estimates, ceilings or undocumented splits; those under 4 hm³ are drawn at 4 hm³.

## Evidence
Page images of the cited sources are not published (copyright). `EVIDENCE.md` lists every cited page; the images can be regenerated locally into the git-ignored `04_pipeline/work/evidence/` (commands at the end of `EVIDENCE.md`). The three web sources (R10 BFE WASTA, R11 BAFU MQN, R12 Federal Court ATF 150 II 83) are rendered from the responses archived on 2026-10-06 in `04_pipeline/work/web_sources/`.

## Key numbers
- Before 1958: gallery intake at Vissoie ≈ 126 hm³/yr (monthly MQN capped at 7 m³/s), ≈ 83 hm³ left in the river; theoretical gross output at Chippis ≈ 202 GWh/yr (590 m). No production record found.
- After 1958: design average year 569 GWh/yr (Lona 4, Mottec 125, Vissoie 185, Chippis 255; 347 winter / 222 summer). Moiry catchment ≈ 35.3 and Tourtemagne → Moiry ≈ 38.8 hm³ split by catchment area (estimate).
- After 2039: WASTA expected 137 / 216 / 299 GWh/yr (Mottec / Vissoie incl. aux. / Navizence). Grantor shares of upper-stage hydraulic power: Anniviers 55.4 %, Ergisch 18.1 %, Turtmann-Unterems 11.9 %, Oberems 9.4 %, Canton 2.4 % (up to 31.7 %), Chippis 2.2 %, Chalais 0.6 %.

## Main assumptions
- Natural runoff from BAFU MQN (recent reference period) is used for all three periods; glaciers were larger before 1958, so the early volumes are indicative.
- "Not captured" bands = MQN natural flow minus design or WASTA-calibrated volumes: indicative, since the two come from different periods.
- After 2039 the physical system and operating rules are assumed unchanged; the new concession, Moiry raising (≈ 9 m) and a larger Vissoie–Niouc gallery are not yet decided and are only noted.
- The VS message gives 450 GWh/yr mean upper-stage production; WASTA gives 355 GWh for Mottec + Vissoie + Lona. The difference is unexplained.

## Regenerate
```
python3 04_pipeline/scripts/build_period_sankeys.py 02_outputs/flow_diagram_sources/mqn_points.csv 02_outputs/gougra_cascade_energy/cascade_model.json
node 04_pipeline/scripts/render_period_sankeys.js period_models.json svg            # needs playwright, d3, d3-sankey, @fontsource
python3 04_pipeline/scripts/build_evidence_index.py 02_outputs/gougra_period_sankeys/references.json 00_index/reference_list.csv 02_outputs/gougra_period_sankeys/EVIDENCE.md
```
(The build script writes `period_models.json` to the working directory.)
