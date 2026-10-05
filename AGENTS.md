# Agent guide

Read `README.md` for the project map. Rules and pointers for LLM agents follow.

## Where to look
- **Questions about a source**: find it in `00_index/source_catalog.csv` (path, topic, pages), then read the PDF in `01_sources/<topic>/`. The text of every PDF is already extracted in `04_pipeline/work/pdfs/extracted.json` (field `file` = PDF name); search that before reading PDFs page by page. Exception: Bellwald is a scan with no text layer, so use the page images `04_pipeline/work/pdfs/bellwald-*.png`.
- **Facts about rights, concessions, actors or quantities**: query `02_outputs/anniviers_rights_dataset/rights_dataset.sqlite`; field definitions are in its `data_dictionary.json`. Every relation links to evidence (page and quote), so cite evidence IDs and don't paraphrase without them.
- **Timeline and negotiation events**: `02_outputs/negotiation_concession/negotiation_concession_分析.csv`.
- **Coordinates and place names**: `03_reference_data/geodata_resources/data/swissnames3d_2026.sqlite` (read-only; ~500k rows, so always filter). Do not open the 600+ MB CSV/GPKG files directly.
- **Water flows below Moiry**: `02_outputs/moiry_flow_allocation/flow_evidence.csv`.

## Rules
- `01_sources/` and `03_reference_data/` are read-only.
- Do not rename files in `02_outputs/`. `anniviers_rights_dataset/manifest.json` stores SHA-256 hashes, and `sources.local_filename` refers to PDFs by bare filename (they now live in `01_sources/<topic>/`; search there).
- Don't edit `02_outputs/` by hand. To regenerate, edit the script in `04_pipeline/scripts/` and run it from the project root (see `04_pipeline/README.md`).
- New one-off intermediates go in `04_pipeline/work/`, new deliverables in a new `02_outputs/<topic>/` folder with a short README, and new PDFs in `01_sources/<topic>/` plus a row in `source_catalog.csv`.
- Ignore `99_archive/`; nothing there is current.
- Keep the distinctions the existing outputs make: a concession holder ≠ a shareholder ≠ a granting commune; a water-supply agreement ≠ a concession transfer; unknown ≠ zero; plant flows in series cannot be summed.
