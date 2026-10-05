# Pipeline

Scripts that generated `02_outputs/` and `03_reference_data/`. Run them from the project root, e.g. `python3 04_pipeline/scripts/draw_timeline.py`. Paths were updated to the new layout on 2026-10-05; the scripts have not been re-run since.

| Order | Script | Reads | Writes |
|---|---|---|---|
| 1 | `build_research.py` | `work/pdfs/extracted.json` | `work/research_rows.json` |
| 2 | `export_research.mjs` | `work/research_rows.json` | `02_outputs/negotiation_concession/*.csv` |
| 3 | `draw_timeline.py` | (data embedded) | `02_outputs/negotiation_concession/*timeline*`, `work/timeline_*` previews |
| 4 | `build_rights_dataset.py` | (data embedded) | `02_outputs/anniviers_rights_dataset/rights_dataset.{json,sqlite}` |
| 5 | `package_rights_dataset.py` | rights_dataset.json | csv/, snapshots/, dictionary, manifest, prior_outputs/ |
| 6 | `download_geodata_resources.py`, `index_geodata.py`, `fetch_*_points.py`, `fetch_qgis_geometry.py` | swisstopo / GeoAdmin (network) | `03_reference_data/geodata_resources/` |
| 7 | `build_concession_review.py` | timeline CSV + rights dataset | `02_outputs/concession_review/` |
| 8 | `build_qgis_data.py` → `export_qgis_workbook.mjs` → `finalize_qgis.py` | review + geodata | `02_outputs/qgis_wgs84_package/` (also re-creates its zip) |
| – | `build_moiry_integrated.py` | (data embedded) | `02_outputs/moiry_flow_allocation/` sankey + network json |

## Dependencies
- Python with Pillow (timeline, sankey).
- `vendor/qgis_geo_libs/`: vendored numpy, shapely, pyproj for the QGIS scripts (61 MB). You can delete it if you install those packages yourself.
- `.mjs` scripts import `@oai/artifact-tool` through `scripts/node_modules`, a symlink into a Codex runtime cache. It only works on this machine.

## work/
Regenerable intermediates: PDF text extractions and page images (`pdfs/`), Moiry source text and figures (`moiry_flow/`), preview PNGs, JSON handoff files. Safe to delete if you never plan to re-run the scripts.
