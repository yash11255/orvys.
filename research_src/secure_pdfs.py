#!/usr/bin/env python3
"""Stamps a tiled ORVYS watermark into the content of every page of every research PDF,
then locks the PDF (AES-256): anyone can open and print it, but editing, copying text,
extracting pages and annotating are blocked in standard PDF software.
Run with the project venv: research_src/.venv/bin/python research_src/secure_pdfs.py
"""
import pathlib, secrets, sys
from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions as P

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
stamp = PdfReader(HERE / "stamp.pdf").pages[0]
owner = secrets.token_urlsafe(32)  # random, never stored: the lock cannot be lifted with a known password
perms = P.PRINT | P.PRINT_TO_REPRESENTATION

done = 0
for pdf in sorted((ROOT / "research" / "pdf").rglob("*.pdf")):
    reader = PdfReader(pdf)
    if reader.is_encrypted:
        print("skip (already secured):", pdf.name); continue
    w = PdfWriter()
    for page in reader.pages:
        w.add_page(page)
    for page in w.pages:
        for img in page.images:              # shrink embedded photos: max 800 px, JPEG q55
            try:
                im = img.image
                if im.width > 800:
                    im = im.resize((800, round(im.height * 800 / im.width)))
                img.replace(im.convert("RGB"), quality=55)
            except Exception:
                pass
        page.compress_content_streams()
        page.merge_page(stamp, over=True)   # burned into the page content, above the text
    w.add_metadata({"/Title": (reader.metadata or {}).get("/Title", pdf.stem), "/Author": "Orvys Research", "/Creator": "Orvys (www.orvys.in)", "/Producer": "Orvys"})
    w.encrypt(user_password="", owner_password=owner, permissions_flag=perms, algorithm="AES-256")
    with open(pdf, "wb") as f:
        w.write(f)
    done += 1
print(f"Secured {done} PDFs (watermark stamped + locked)")
