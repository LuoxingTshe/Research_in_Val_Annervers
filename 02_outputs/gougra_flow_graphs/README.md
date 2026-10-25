# Gougra flow graphs (node–edge)

Generated 2026-10-12. Node–edge flow graphs for the three periods, replacing the Sankey layout. Upstream catchments are on the left; the Rhône is a vertical axis on the right (Turtmann above Chippis, since the Rhône flows west). All three use the same column positions and balance to the same natural runoff (332.2 hm³/yr), so they can be laid side by side. Values are identical to `../gougra_period_sankeys/period_models.json`.

| File | Period |
|---|---|
| `gougra_flowgraph_1_before-1958.svg` | State c. 1950: AIAG run-of-river plant at Chippis (gallery ≤ 7 m³/s), no storage; Turtmänna used in its own valley |
| `gougra_flowgraph_2_after-1958.svg` | Gougra scheme as commissioned 1958–61, design average year (Robert 1962, Table 2) |
| `gougra_flowgraph_3_after-2039-return.svg` | After the upper stage reverts to the grantors (31 Dec 2039), today's rules in a mean year, with grantor shares |
| `*_preview.png` | Raster previews |
| `flow_graph_*.json` | Graph specs: node positions and types, edge values and notes |

Editing: live text, explicit colours, layers `title`, `legend`, `graph` › `column-guides`, `rhone`, `edges`, `nodes`, `label-halos`, `labels`, plus `notes` (and `grantor shares` in the 2039 graph). Edges have ids such as `edge_moiry_to_mottec`, nodes `node_vissoie`. Fonts: Source Serif 4, Source Sans 3, IBM Plex Mono.

Reading the graphs:
- Circle = catchment / runoff source; dark dot = intake or junction; trapezoid = reservoir; numbered blue square = plant stage (C = Chippis before 1958); dashed square = plants outside the scheme (ITAG, Turtmann valley); green diamond = reach with a statutory minimum flow; grey diamond = reach without one; yellow dot = abstraction; dashed circle = unturbined water (balance term).
- Edge width is proportional to annual volume (hm³/yr); the number on each edge is the volume. Dashed edges are estimates, ceilings or calibration terms.
- In the 2039 graph the pumping loop is a real return arrow from the Mottec basin to Moiry (≈ 15.3 hm³/yr, storage-pump equivalent of 30.2 GWh).
- Reference IDs [R##] match `../gougra_period_sankeys/EVIDENCE.md`.

Regenerate (from the project root):
```
python3 04_pipeline/scripts/build_flow_graphs.py 02_outputs/gougra_period_sankeys/period_models.json 02_outputs/gougra_flow_graphs
python3 04_pipeline/scripts/render_flow_graph.py 02_outputs/gougra_flow_graphs/flow_graph_1_before-1958.json 02_outputs/gougra_flow_graphs/gougra_flowgraph_1_before-1958.svg
(same for 2_after-1958 and 3_after-2039-return)
```
