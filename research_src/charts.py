"""Small SVG chart helpers for Orvys Research (static, print-friendly)."""
import html

NAVY, NAVY2, GOLD, GREY, MUTE, LINE = "#0e1a29", "#1b2d44", "#a8864f", "#c9d0d9", "#5f6b7a", "#e4e1da"


def esc(s):
    return html.escape(str(s))


def hbar(items, fmt, width=760, row=26, label_w=170, title=None, ref=None):
    """items: list of (label, value, highlight_bool). ref: (value, label) dashed reference line."""
    maxv = max([v for _, v, _ in items] + ([ref[0]] if ref else [])) or 1
    plot = width - label_w - 90
    h = len(items) * row + 30
    out = [f'<svg viewBox="0 0 {width} {h}" width="100%" role="img" aria-label="{esc(title or "")}" font-family="Inter, DM Sans, sans-serif">']
    for i, (lab, v, hi) in enumerate(items):
        y = 10 + i * row
        w = max(v / maxv * plot, 0 if v == 0 else 1.5)
        col = GOLD if hi else NAVY2
        out.append(f'<text x="{label_w - 10}" y="{y + row * .62:.1f}" text-anchor="end" font-size="13" fill="{NAVY if hi else MUTE}" font-weight="{700 if hi else 400}">{esc(lab)}</text>')
        out.append(f'<rect x="{label_w}" y="{y + 4}" width="{w:.1f}" height="{row - 10}" fill="{col}" rx="1.5"><title>{esc(lab)}: {esc(fmt(v))}</title></rect>')
        out.append(f'<text x="{label_w + w + 7:.1f}" y="{y + row * .62:.1f}" font-size="12.5" fill="{NAVY}" font-weight="{700 if hi else 500}">{esc(fmt(v))}</text>')
    if ref:
        x = label_w + ref[0] / maxv * plot
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="4" y2="{h - 18}" stroke="{GOLD}" stroke-dasharray="4 4" stroke-width="1.4"/>')
        out.append(f'<text x="{x + 6:.1f}" y="{h - 4}" font-size="12" fill="{GOLD}" font-weight="600">{esc(ref[1])}</text>')
    out.append("</svg>")
    return "".join(out)


def vbar(labels, values, fmt, width=760, height=300, highlight_last=True, title=None):
    maxv = max([v or 0 for v in values]) or 1
    n = len(values)
    left, bottom, top = 50, height - 36, 26
    band = (width - left - 20) / n
    bw = band * 0.52
    out = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="{esc(title or "")}" font-family="Inter, DM Sans, sans-serif">']
    for t in range(5):
        v = maxv * t / 4
        y = bottom - (bottom - top) * t / 4
        out.append(f'<line x1="{left}" x2="{width - 10}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{MUTE}">{v:.1f}</text>')
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = left + i * band + (band - bw) / 2
        val = v or 0
        hgt = (bottom - top) * val / maxv
        col = GOLD if (highlight_last and i == n - 1) else NAVY2
        out.append(f'<rect x="{x:.1f}" y="{bottom - hgt:.1f}" width="{bw:.1f}" height="{max(hgt, 0):.1f}" fill="{col}" rx="2"><title>{esc(lab)}: {esc(fmt(v))}</title></rect>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{bottom - hgt - 8:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{NAVY}">{esc(fmt(v))}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{bottom + 22}" text-anchor="middle" font-size="12" fill="{MUTE}">{esc(lab)}</text>')
    out.append("</svg>")
    return "".join(out)


def stacked(labels, a, b, a_name, b_name, width=760, height=300, title=None):
    tot = [x + y for x, y in zip(a, b)]
    maxv = max(tot) or 1
    n = len(labels)
    left, bottom, top = 50, height - 56, 24
    band = (width - left - 20) / n
    bw = band * 0.5
    out = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="{esc(title or "")}" font-family="Inter, DM Sans, sans-serif">']
    for i in range(n):
        x = left + i * band + (band - bw) / 2
        ha = (bottom - top) * a[i] / maxv
        hb = (bottom - top) * b[i] / maxv
        out.append(f'<rect x="{x:.1f}" y="{bottom - ha:.1f}" width="{bw:.1f}" height="{ha:.1f}" fill="{NAVY2}"><title>{esc(labels[i])} {esc(a_name)}: ₹{a[i]:.2f} Cr</title></rect>')
        out.append(f'<rect x="{x:.1f}" y="{bottom - ha - hb:.1f}" width="{bw:.1f}" height="{hb:.1f}" fill="{GOLD}"><title>{esc(labels[i])} {esc(b_name)}: ₹{b[i]:.2f} Cr</title></rect>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{bottom - ha - hb - 8:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{NAVY}">₹{tot[i]:.0f} Cr</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{bottom + 20}" text-anchor="middle" font-size="12" fill="{MUTE}">{esc(labels[i])}</text>')
    out.append(f'<rect x="{left}" y="{height - 22}" width="12" height="12" fill="{NAVY2}"/><text x="{left + 18}" y="{height - 12}" font-size="12" fill="{NAVY}">{esc(a_name)}</text>')
    out.append(f'<rect x="{left + 150}" y="{height - 22}" width="12" height="12" fill="{GOLD}"/><text x="{left + 168}" y="{height - 12}" font-size="12" fill="{NAVY}">{esc(b_name)}</text>')
    out.append("</svg>")
    return "".join(out)


def share_pair(rows, width=760, title=None):
    """rows: list of (label, pop_share, csr_share)."""
    row = 64
    h = len(rows) * row + 40
    plot = width - 230
    out = [f'<svg viewBox="0 0 {width} {h}" width="100%" role="img" aria-label="{esc(title or "")}" font-family="Inter, DM Sans, sans-serif">']
    for i, (lab, p, c) in enumerate(rows):
        y = 10 + i * row
        out.append(f'<text x="0" y="{y + 15}" font-size="13.5" font-weight="700" fill="{NAVY}">{esc(lab)}</text>')
        out.append(f'<rect x="200" y="{y + 2}" width="{plot * p / 100:.1f}" height="18" fill="{GREY}"/><text x="{205 + plot * p / 100:.1f}" y="{y + 16}" font-size="12" fill="{MUTE}">{p:.1f}% of people</text>')
        out.append(f'<rect x="200" y="{y + 26}" width="{max(plot * c / 100, 1.5):.1f}" height="18" fill="{GOLD}"/><text x="{205 + max(plot * c / 100, 1.5):.1f}" y="{y + 40}" font-size="12" font-weight="700" fill="{GOLD}">{c:.1f}% of CSR</text>')
    out.append("</svg>")
    return "".join(out)
