#!/usr/bin/env python3
"""
Renders static watermarked PDF files for all research pages and 38 district pages
using headless Chrome.
"""
import subprocess, pathlib, sys, time, concurrent.futures

ROOT = pathlib.Path(__file__).parent.parent
PDF_DIR = ROOT / "research" / "pdf"
DIST_PDF_DIR = PDF_DIR / "districts"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def get_targets():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    DIST_PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    targets = [
        (ROOT / "research" / "index.html", PDF_DIR / "bihar-csr-research-hub.pdf"),
        (ROOT / "research" / "diagnostic.html", PDF_DIR / "bihar-csr-diagnostic.pdf"),
        (ROOT / "research" / "policy.html", PDF_DIR / "bihar-csr-policy.pdf"),
        (ROOT / "research" / "skilling.html", PDF_DIR / "bihar-csr-skilling.pdf"),
        (ROOT / "research" / "ecosystem.html", PDF_DIR / "bihar-csr-ecosystem.pdf"),
        (ROOT / "research" / "tracker.html", PDF_DIR / "bihar-csr-tracker.pdf"),
    ]
    
    dist_htmls = sorted((ROOT / "research" / "districts").glob("*.html"))
    for dh in dist_htmls:
        slug = dh.stem
        if slug == "index":
            targets.append((dh, DIST_PDF_DIR / "all-districts-directory.pdf"))
        else:
            targets.append((dh, DIST_PDF_DIR / f"{slug}-csr-research.pdf"))
            
    return targets

def render_all(base="http://localhost:8810"):
    """Render through the local web server (start it first) so CSS, fonts and images load."""
    import json, tempfile
    targets = []
    for src, dst in get_targets():
        if src.exists():
            rel = src.relative_to(ROOT).as_posix()
            url = "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
            targets.append({"url": url, "out": str(dst.resolve())})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(targets, f)
    print(f"Rendering {len(targets)} watermarked PDFs via {base} ...")
    t0 = time.time()
    subprocess.run(["node", str(pathlib.Path(__file__).parent / "render_pdfs.cjs"), f.name, base], check=False)
    print(f"Done in {time.time() - t0:.1f}s")
    venv_py = pathlib.Path(__file__).parent / ".venv" / "bin" / "python"
    subprocess.run([str(venv_py), str(pathlib.Path(__file__).parent / "secure_pdfs.py")], check=False)


if __name__ == "__main__":
    render_all()

