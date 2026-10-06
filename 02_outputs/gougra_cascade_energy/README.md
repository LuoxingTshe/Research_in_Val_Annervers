# Gougra Cascade Water Balance (staging · theoretical energy · winter/summer strategy)

Generated 2026-10-05 by `04_pipeline/scripts/build_cascade_energy.py` (template `cascade_energy_template.html` in the same folder). Run from the project root:

```
python3 04_pipeline/scripts/build_cascade_energy.py
```

## Files
- `index.html`: minimal Sankey diagram, per-stage theoretical energy table, residual-flow mechanism, and a winter/summer pumping-revenue calculator with editable prices. Loads d3 / d3-sankey from a CDN.
- `cascade_model.json`: Sankey nodes and links (true `value` and drawn `display` width, `uncertain` flag) plus all computed results.

## Basis (difference from `moiry_flow_allocation/`)
The quantitative Sankey in `moiry_flow_allocation/` stops at the inflow total and does not allocate further. This output is a **theoretical model**: the four 2025 annual-report inflow areas (Moiry 28.45, Tourtemagne 47.56, Mottec 106.50, Vissoie 12.00 hm³) are mapped to their entry points, statutory residual flows (annualised, upper-bound case) and irrigation/snowmaking ceilings are removed, and all remaining water is assumed to pass every downstream stage. Stage volumes are the same water reused in series and must not be summed.

Diagram layout: each tributary joins at the stage where it is captured, so large flows do not cross. Hatched bands (snowmaking, irrigation, extra release at the Mottec intake, Vissoie-area share of the 470 L/s) are estimates or ceilings, drawn at a minimum of 4 hm³ for legibility; labels and tooltips give the modelled value.

| Item | Value | Source |
|---|---:|---|
| Gross head Lona / Mottec / Vissoie / Navizence | 331 / 685 (Tourtemagne direct 613) / 439 / 590 m | Robert 1962; Mottier; Savoy PDF 79 |
| 2025 theoretical volume Mottec / Vissoie / Navizence | 73.6 / 172.7 / 176.5 hm³ | this model |
| Theoretical gross energy (η = 1) | 4.5 + 128.0 + 206.6 + 283.7 = 622.8 GWh | this model |
| Net at η = 0.85 | 529.4 GWh (2025 actual 453.9) | this model; FMG RG 2025 |
| Residual-flow volumes | Gougra 2.21; St-Jean–Vissoie 9.46; below Vissoie 14.82; Fang 1.58 hm³ | Savoy PDF 80–81, annualised |
| Energy forgone to residual flows (upper bound) | 22.6 GWh/yr | this model |
| Statutory gross power | ≈ 79 MW (8.70 MCHF ÷ 110 CHF/kWth) | FMG RG 2025, note 4 |
| 1962 design year winter / summer | 347 / 222 GWh (Moiry stage 111 GWh, all in winter) | Robert 1962, Table 2 |
| 2025 monthly-mean price winter / summer | 114.3 / 75.0 CHF/MWh | euenergy.live (ENTSO-E) |

## Main assumptions (unknown ≠ zero)
- The split of Tourtemagne water between direct turbining and siphon pumping into Moiry is not published; counted as direct. Lona volume estimated by catchment share.
- The Navizence 300 L/s credits only the Gougra release, ignoring lateral inflow, so the residual-flow cost is an upper bound.
- Briey 45 L/s and Niouc < 60 L/s both over 139 days. Ricard and Granges draw from the residual reach in unknown amounts and are not shown.
- Pumping: siphon pump mean head 63 m at 80 %; storage pump 617 m at 85 %. Prices are monthly means and ignore intraday low-price pumping.
- Revenue figures are market-value estimates: FMG settles with shareholders at cost plus 10 %, so price effects fall on the shareholders; water fees and special tax are levied on theoretical power and do not change with seasonal strategy.

## Vector files (`vector/`)
Editable exports of the figures, light theme, white background. Text is live, colours are written as plain hex, and each figure is grouped into named layers (`title`, `legend`, `links`, `nodes`, `labels`, `label-halos`, `footnote`). Links and nodes carry ids such as `link_moiry_to_mottec` and `node_vissoie`.
- `gougra_cascade_sankey.svg` / `.pdf`: Sankey diagram with title, legend and footnote.
- `gougra_price_2025.svg` / `.pdf`: 2025 monthly mean day-ahead prices.
- `gougra_storage_value.svg` / `.pdf`: revenue per m³, summer direct vs. stored for winter (at 2025 seasonal mean prices).

Fonts: Source Serif 4, Source Sans 3 and IBM Plex Mono (free on Google Fonts); install them before editing the SVGs or text falls back to Helvetica / Menlo. The PDFs embed the fonts. The `label-halos` layer is a white outline under the labels that keeps them legible over flows; delete or recolour it as needed (in the PDF it is drawn as outlines).
Regenerate after `build_cascade_energy.py` with `node 04_pipeline/scripts/export_vector.js` (needs playwright, d3, d3-sankey and @fontsource packages; paths in the script are relative to its working folder).
