"""Render every cited PDF page in references.json to PNG with a uniform name:
   R{nn}_{token}_{year}_p{NNN}.png   (NNN = PDF page index, 1-based)
Run from project root: python3 04_pipeline/scripts/capture_evidence_pages.py <references.json> <outdir> [dpi]"""
import json, os, subprocess, sys, tempfile, shutil
refs = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]; dpi = sys.argv[3] if len(sys.argv) > 3 else "150"
os.makedirs(out, exist_ok=True)
for rid, r in refs.items():
    if r["type"] != "pdf": continue
    for pg in r["pages"]:
        name = f"{rid}_{r['token']}_{r['year']}_p{int(pg):03d}.png"
        tmp = tempfile.mkdtemp()
        subprocess.run(["pdftoppm", "-r", dpi, "-f", pg, "-l", pg, "-png", "-singlefile", r["path"], os.path.join(tmp, "x")], check=True)
        shutil.move(os.path.join(tmp, "x.png"), os.path.join(out, name)); shutil.rmtree(tmp)
        print(name)
