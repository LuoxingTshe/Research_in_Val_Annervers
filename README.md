# Research Resources — Val d'Anniviers / Gougra

Research on water, hydropower concessions, bisses (irrigation channels) and landscape commons in Val d'Anniviers (Valais, CH): the Gougra hydropower scheme (Moiry dam, Mottec, Vissoie, Navizence), its concession expiring in 2039, and the local rights and agreements built around it.

Reorganised 2026-10-05. Folders are numbered in reading order.

```
00_index/            What exists: reading list and source catalog
01_sources/          Original PDFs, grouped by topic (read-only)
02_outputs/          Finished analysis results: the deliverables
03_reference_data/   Large external datasets (swisstopo place names, 676 MB)
04_pipeline/         Scripts that produced 02_outputs, plus their working files
99_archive/          Superseded or redundant files kept for safety; can be deleted
```

## 00_index
- `00_Research Resources.pdf`: the master reading list, including sources not yet downloaded (Viallon, Epiney, Marthaler, Bugmann, image and GIS portals).
- `source_catalog.csv`: one row per PDF in `01_sources/`, with path, topic, author, year, language, page count and citation.

## 01_sources
| Folder | Contents |
|---|---|
| `hydropower/` | Gougra engineering articles (Robert, Hoeffleur, Stucky, Mottier 1959–62), Flaminio & Reynard 2023, Savoy 2025 (governance, 143 pp: the key source) |
| `concessions/` | Bagnoud 2022 (2039 expiry), Kanton Wallis 2025 model concession, Commune d'Anniviers bisses inventory 2017 |
| `bisses_irrigation/` | Bellwald (guardian huts), Stevenson 1946 |
| `landscape_commons/` | Gerber & Hess 2017, Louvin & Calvo 2025 |
| `geology/` | Zimmermann 1955 |

## 02_outputs
| Folder | What it is | Start with |
|---|---|---|
| `negotiation_concession/` | 52-record timeline of concession and compensation negotiations, plus the timeline chart and a source screening checklist | `negotiation_concession_timeline.png` |
| `anniviers_rights_dataset/` | Relational dataset of who holds which water or concession rights (entities, relations, evidence, snapshots 1953→2039) | `README.md`, `relations_readable.csv` |
| `concession_review/` | Review list of geographic objects named in the concessions | `concession_地物与客体_审理清单.md` |
| `qgis_wgs84_package/` | Those objects geocoded (WGS84) for QGIS: points, lines, unlocated objects | `README_导入与审理说明.md` |
| `moiry_flow_allocation/` | How water below Moiry dam is allocated (ecological flows, irrigation, hydropower), with a Sankey diagram | `研究说明.md` |
| `gougra_cascade_energy/` | Theoretical cascade model: 2025 inflows routed through Mottec → Vissoie → Navizence with residual flows, per-stage theoretical energy, winter/summer pumping value | `index.html`, `README.md` |

Dependency chain: `negotiation_concession` → `anniviers_rights_dataset` → `concession_review` → `qgis_wgs84_package`, with `03_reference_data/geodata_resources` supplying coordinates.

## 03_reference_data
`geodata_resources/`: swissNAMES3D 2026 (an offline SQLite database of all Swiss place names), GeoAdmin API docs and saved query responses. Search it with `python3 search_local.py 'Moiry'` from that folder. It can be downloaded again using `download_manifest.json`.

## 04_pipeline
See `04_pipeline/README.md`. Run scripts from the project root.

## Note on languages
Most generated notes and README files are in Chinese; source PDFs are in French, German and English. File names were kept unchanged so that existing cross-references and checksums still work.
