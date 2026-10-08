# Research Resources — Val d'Anniviers / Gougra

Research on water, hydropower concessions, bisses (irrigation channels) and landscape commons in Val d'Anniviers (Valais, CH): the Gougra hydropower scheme (Moiry dam, Mottec, Vissoie, Navizence), its concession expiring in 2039, and the local rights and agreements built around it.

Reorganised 2026-10-05. Folders are numbered in reading order. Work history and the next research goal are kept in `RESEARCH_LOG.md`.

```
00_index/            Bibliography (reference_list.csv)
01_sources/          Original PDFs, grouped by topic (local only, not in git; read-only)
02_outputs/          Finished analysis results: the deliverables
03_reference_data/   Large external datasets (swisstopo place names, 676 MB)
04_pipeline/         Scripts that produced 02_outputs, plus their working files
99_archive/          Superseded or redundant files kept for safety; can be deleted
```

## 00_index
- `reference_list.csv`: the bibliography, one row per item under its original title, with author, year, container, pages, DOI/URL and topic. IDs: `R` = publications, `W` = websites, `P` = image and GIS portals. `local_copy` = yes when the full text is held locally.

## Source texts (local only)
Full texts are not published in this repository for copyright reasons. Local copies sit in `01_sources/<topic>/` (hydropower, concessions, bisses_irrigation, landscape_commons, geology), `02_outputs/moiry_flow_allocation/sources/` and `04_pipeline/work/`; all are listed in `.gitignore`. To work with them, obtain each item from the DOI/URL in `reference_list.csv`.

## 02_outputs
| Folder | What it is | Start with |
|---|---|---|
| `negotiation_concession/` | 52-record timeline of concession and compensation negotiations, plus the timeline chart and a source screening checklist | `negotiation_concession_timeline.png` |
| `anniviers_rights_dataset/` | Relational dataset of who holds which water or concession rights (entities, relations, evidence, snapshots 1953→2039) | `README.md`, `relations_readable.csv` |
| `concession_review/` | Review list of geographic objects named in the concessions | `concession_地物与客体_审理清单.md` |
| `qgis_wgs84_package/` | Those objects geocoded (WGS84) for QGIS: points, lines, unlocated objects | `README_导入与审理说明.md` |
| `moiry_flow_allocation/` | How water below Moiry dam is allocated (ecological flows, irrigation, hydropower), with a Sankey diagram | `研究说明.md` |
| `gougra_cascade_energy/` | Theoretical cascade model: 2025 inflows routed through Mottec → Vissoie → Navizence with residual flows, per-stage theoretical energy, winter/summer pumping value | `index.html`, `README.md` |
| `flow_diagram_sources/` | Web sources gathered 2026-10-06 for a more detailed flow diagram: BFE per-plant statistics, BAFU natural monthly flows per intake, full intake list (Convention 2022), Vissoie spill (BGE 150 II 83), cross-checks against the cascade model | `README.md`, `evidence_additions.csv` |
| `concession_objects_merged/` | Object-level point (11) and line (20) GeoJSON layers that replace the four GeoJSON files formerly in `qgis_wgs84_package`, with feature type, construction year (web/literature/inferred) and each concession event year in its own field | `README.md` |
| `valley_economic_narrative/` | Narrative of the valley's economic shift (agro-pastoral → tourism, hydropower, multi-use landscape) for the landscape design assignment, with page citations | `README.md` |

Dependency chain: `negotiation_concession` → `anniviers_rights_dataset` → `concession_review` → `qgis_wgs84_package`, with `03_reference_data/geodata_resources` supplying coordinates.

## 03_reference_data
`geodata_resources/`: swissNAMES3D 2026 (an offline SQLite database of all Swiss place names), GeoAdmin API docs and saved query responses. Search it with `python3 search_local.py 'Moiry'` from that folder. It can be downloaded again using `download_manifest.json`.

## 04_pipeline
See `04_pipeline/README.md`. Run scripts from the project root.

## Note on languages
Most generated notes and README files are in Chinese; source PDFs are in French, German and English. File names were kept unchanged so that existing cross-references and checksums still work.
