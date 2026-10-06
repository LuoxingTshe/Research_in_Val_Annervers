# Gougra Cascade Water Balance (v2, mean year)

Version 2, generated 2026-10-06 by `04_pipeline/scripts/build_cascade_energy.py` (template `cascade_energy_template.html` beside it), using the new evidence in `02_outputs/flow_diagram_sources/`. Version 1 (2025 inflows, η = 0.85 assumption) is in git history (commit 7065e47).

```
python3 04_pipeline/scripts/build_cascade_energy.py            # model + index.html
node 04_pipeline/scripts/export_vector.js                      # vector/ (needs playwright, d3, d3-sankey, @fontsource)
```

## What changed from v1
| | v1 (5 Oct) | v2 (6 Oct) |
|---|---|---|
| Year basis | 2025 inflow, 194.5 hm³ | 10-year mean inflow, 265.5 hm³ (2025 area shares × 1.365) |
| Plant volumes | all remaining water assumed turbined | BFE WASTA expected generation ÷ leaflet energy coefficient |
| Heads | Robert 1962 maximum gross heads | WASTA heads (Lona 319, Mottec 640, Vissoie 437, Navizence 591 m) |
| Energy per stage | theoretical only, η = 0.85 assumed | WASTA expected generation + theoretical gross; overall efficiency derived |
| New bands | — | pumping (≈ 15 hm³ = 30.2 GWh), water not turbined at Mottec, Vissoie spill (tunnel bottleneck), recapture at Vissoie intake |
| Residual-flow cost | 22.6 GWh (missed the lower stage for upstream releases) | 33.4 GWh, coefficients applied over every stage skipped |

## Mean-year results
| Plant | Head m | Turbined hm³/yr | Theoretical gross GWh/yr | WASTA expected GWh/yr |
|---|---:|---:|---:|---:|
| Lona | 319 | 2.9 | 2.5 | 2.0 |
| Mottec | 640 | 95.3 (range 88.4–103.5) | 166.3 | 137.05 |
| Vissoie | 437 | 216.0 | 257.2 | 213.0 + 3.1 aux. |
| Navizence | 591 | 233.9 | 376.7 | 298.7 |
| Total | | | 802.7 | 653.85 |

Balance terms (calibration, not measurements): pumped ≈ 15.27 hm³; not turbined at Mottec ≈ 21.18 hm³; overflow at Mottec intake ≈ 2.01 hm³; recaptured at Vissoie intake ≈ 23.19 hm³; Vissoie spill ≈ 13.49 hm³ (BGE 150 II 83: ≈ 20 hm³ in 2001). Residual flows: Gougra 2.21, St-Jean–Vissoie 9.46, below Vissoie 14.82, Fang 1.58 hm³/yr.

Inflow check against BAFU MQN (natural, modelled): Moiry dam + Lona 44.9 (model 38.83); Turtmänna 1728 m ≤ 64.0 (model 64.92); Navisence at Mottec + Moulins + Nava 139.9 (model 145.37).

## Assumptions
- Mean-year inflow split uses the 2025 reporting-area shares.
- Surplus above Mottec is routed as spill to the Gougra/Navizence and recaptured at Vissoie; if it is lost at Tourtemagne instead, the Vissoie spill shrinks accordingly.
- Pumped volume is the storage-pump equivalent of 30.2 GWh (617 m, 85 %); siphon transfers would mean a larger volume at lower cost.
- Residual flows annualised and deducted in full; irrigation at allocation ceilings; snowmaking 0.11 % of inflow. Ricard and Granges not shown.
- The 2021 asset list places the Nava and Moulins intakes among the Vissoie-stage intakes; some Moulins water may enter one stage lower than drawn.
- Strategy section uses leaflet energy coefficients, 2025 monthly mean prices and the leaflet's 52 % winter share.

## Files
- `index.html`: page (Sankey, stage table, residual flows, winter/summer strategy calculator).
- `cascade_model.json`: nodes, links (true `value`, drawn `display`, `uncertain`), all results.
- `vector/`: editable SVG and PDF of the Sankey and the two small charts; layers `title`, `legend`, `links`, `nodes`, `label-halos`, `labels`, `footnote`; fonts Source Serif 4, Source Sans 3, IBM Plex Mono (embedded in the PDFs).
