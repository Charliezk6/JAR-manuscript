# -*- coding: utf-8 -*-
"""Draw Figure 1 and Figure 2 for the JAR manuscript from the deposited plotting
data in Data Availability Note Section 8.17. Pure SVG, no external deps."""
import os

OUT = r"C:\Users\Administrator\WorkBuddy\2026-10-23-06-03-49"

W, H = 660, 440
T, B = 46, 94
L, R = 78, 40
PW = W - L - R
PH = H - T - B
PAD = 24.0


def sx(i, n):
    if n <= 1:
        return L + PW / 2.0
    return L + PAD + (PW - 2 * PAD) * i / (n - 1.0)


def sy(v, ymin, ymax):
    return T + PH * (ymax - v) / (ymax - ymin)


def tick_vals(ymin, ymax, step):
    out, v = [], 0.0
    while v <= ymax + 1e-9:
        out.append(round(v, 4))
        v += step
    v = -step
    while v >= ymin - 1e-9:
        out.append(round(v, 4))
        v -= step
    return sorted(set(out))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def marker(kind, x, y, fill, stroke):
    if kind == "circle":
        return ('<circle cx="%.1f" cy="%.1f" r="3.7" fill="%s" stroke="%s" '
                'stroke-width="1.2"/>' % (x, y, fill, stroke))
    if kind == "square":
        return ('<rect x="%.1f" y="%.1f" width="7.0" height="7.0" fill="%s" '
                'stroke="%s" stroke-width="1.2"/>'
                % (x - 3.5, y - 3.5, fill, stroke))
    if kind == "tri":
        return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" '
                'stroke="%s" stroke-width="1.2"/>'
                % (x, y - 4.3, x + 4.1, y + 3.5, x - 4.1, y + 3.5, fill, stroke))
    return ""


def build(series, ymin, ymax, step, xtitle, ytitle, xlabels, band=None,
          zero_line=True, lead=0.0):
    """series: list of (label, values, dash, marker_kind, color)"""
    p = []
    p.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d" font-family="Times New Roman, Times, serif">'
             % (W, H, W, H))
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H))

    n = len(series[0][1])

    # shaded band (drawn inside the plot frame, behind everything)
    if band is not None:
        x0 = sx(band[0], n)
        x1 = sx(band[1], n)
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="#F0F0F0" stroke="none"/>' % (x0, T, x1 - x0, PH))
        p.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#555555" '
                 'text-anchor="middle">%s</text>'
                 % ((x0 + x1) / 2.0, T + 13, esc("years 2-3")))

    # horizontal gridlines + y ticks
    for v in tick_vals(ymin, ymax, step):
        y = sy(v, ymin, ymax)
        dash = ' stroke-dasharray="3,3"' if abs(v) > 1e-9 or not zero_line else ' stroke-dasharray="2,2"'
        col = "#B8B8B8" if abs(v) < 1e-9 else "#E0E0E0"
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1"%s/>' % (L, y, L + PW, y, col, dash))
        lab = ("%g" % v) if abs(v) > 1e-9 else "0"
        p.append('<text x="%.1f" y="%.1f" font-size="12" fill="#111111" '
                 'text-anchor="end">%s</text>' % (L - 8, y + 4, lab))

    # frame
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
             'stroke="#111111" stroke-width="1.1"/>' % (L, T, PW, PH))

    # series
    for label, vals, dash, mk, col in series:
        pts = [(sx(i, n), sy(v, ymin, ymax)) for i, v in enumerate(vals)]
        d = " ".join("%.1f,%.1f" % (a, b) for a, b in pts)
        darg = '' if dash == "solid" else ' stroke-dasharray="%s"' % dash
        p.append('<polyline points="%s" fill="none" stroke="%s" '
                 'stroke-width="1.7"%s/>' % (d, col, darg))
        for (a, b) in pts:
            p.append(marker(mk, a, b, "#ffffff", col))

    # x tick labels + axis titles
    for i, lab in enumerate(xlabels):
        x = sx(i, n)
        p.append('<text x="%.1f" y="%.1f" font-size="12" fill="#111111" '
                 'text-anchor="middle">%s</text>'
                 % (x, T + PH + 18, esc(str(lab))))
    p.append('<text x="%.1f" y="%.1f" font-size="12.5" fill="#111111" '
             'text-anchor="middle">%s</text>'
             % (L + PW / 2.0, T + PH + 40, esc(xtitle)))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-size="12.5" '
             'fill="#111111" text-anchor="middle">%s</text>'
             % (20, T + PH / 2.0, esc(ytitle)))

    # legend, two rows if needed
    lx = L
    ly = T + PH + 58
    per_row = 2 if len(series) > 2 and max(len(s[0]) for s in series) > 34 else len(series)
    if len(series) == 3:
        per_row = 3
        colw = PW / 3.0
    else:
        per_row = len(series)
        colw = PW / float(len(series))
    for k, (label, vals, dash, mk, col) in enumerate(series):
        cx = lx + (k % per_row) * colw
        cy = ly + (k // per_row) * 17
        darg = '' if dash == "solid" else ' stroke-dasharray="%s"' % dash
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.7"%s/>' % (cx, cy, cx + 17, cy, col, darg))
        p.append(marker(mk, cx + 8.5, cy, "#ffffff", col))
        p.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#111111">%s</text>'
                 % (cx + 23, cy + 3.6, esc(label)))
    p.append('</svg>')
    return "\n".join(p)


def main():
    # ---- Figure 1: DAN 8.17 "Figure 1 data" ----
    f1 = build(
        series=[
            ("Joint clusters",
             [-0.202, -0.398, -0.269, 0.912, -0.612], "solid", "circle", "#000000"),
            ("All other clusters",
             [-0.078, -0.025, -0.046, 0.103, 0.078], "6,3", "square", "#5A5A5A"),
            ("Balanced panel",
             [-0.032, -0.038, -0.042, 0.019, 0.147], "2,3", "tri", "#909090"),
        ],
        ymin=-0.75, ymax=1.00, step=0.25,
        xtitle="Signing-partner clock year",
        ytitle="Residualized mean E score",
        xlabels=[1, 2, 3, 4, 5],
    )
    # ---- Figure 2: DAN 8.17 implied levels against the year-one base ----
    f2 = build(
        series=[
            ("Non-balanced firms",
             [0.0, 0.140, 0.181, 0.839, -0.359], "solid", "circle", "#000000"),
            ("Balanced firms",
             [0.0, -0.025, -0.040, 0.051, 0.163], "6,3", "square", "#5A5A5A"),
        ],
        ymin=-0.50, ymax=1.00, step=0.25,
        xtitle="Signing-partner clock year",
        ytitle="Regression-implied E level (year 1 = 0)",
        xlabels=[1, 2, 3, 4, 5],
        band=(1, 2),  # zero-based indices for years 2 and 3
    )

    p1 = os.path.join(OUT, "JAR档案_Figure1_20261023.svg")
    p2 = os.path.join(OUT, "JAR档案_Figure2_20261023.svg")
    for path, txt in ((p1, f1), (p2, f2)):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(txt)
        print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))

    html = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Manuscript figures</title><style>
body{font-family:"Times New Roman",Times,serif;color:#111;background:#fff;
     max-width:760px;margin:32px auto;padding:0 20px;line-height:1.5}
figure{margin:0 0 44px}figcaption{font-size:12.5pt;margin-top:10px;text-align:left}
.note{font-size:11.5pt;color:#555;border-left:3px solid #ddd;padding-left:12px;margin-top:8px}
h1{font-size:16pt;font-weight:normal;border-bottom:1px solid #ccc;padding-bottom:8px}
</style></head><body>
<h1>Figures drawn from Data Availability Note &sect;8.17</h1>
<figure>
__SVG1__
<figcaption><b>Figure 1.</b> Mean E-score by signing-partner clock year, residualized
on pair-firm (or firm) and year fixed effects. Joint five-year clusters (970 clusters,
2,622 cells); all other clusters (6,781 clusters, 16,754 cells); balanced panel
(1,203 firms). Plotted values are residualized cell means, not regression estimates;
we quote the regression contrasts of Tables 8 and 12 (+1.201, &minus;0.161 and
&minus;0.113).</figcaption>
</figure>
<figure>
__SVG2__
<figcaption><b>Figure 2.</b> Pre-trend check by balanced status: regression-implied E
levels against the year-one base. Non-balanced firms are those whose observed partner
spells complete inside the window (18,152 rows); balanced firms are observed in all
eleven years (13,122 rows). Points come from one firm-and-year fixed-effects regression
with full controls (N = 31,274); the shaded band marks years two and three, the window
before the deadline can bind.</figcaption>
</figure>
<div class="note"><b>Drafting note (not part of the manuscript).</b> Both figures are
drawn only from the plotted series that Section 8.17 deposits. That section deposits
cell means and cell counts but no cell-level standard errors, so the 95 percent
confidence whiskers the caption promises cannot be reproduced from the package as it
stands. Either deposit the cell SEs alongside the means, or drop the whisker clause
from both captions. Suggested replacement clause for Figure 1:
&ldquo;Plotted values are residualized cell means without interval estimates; the
regression contrasts we quote are in Tables 8 and 12.&rdquo;</div>
</body></html>"""
    html = html.replace("__SVG1__", f1).replace("__SVG2__", f2)
    p3 = os.path.join(OUT, "JAR档案_Figures预览_20261023.html")
    with open(p3, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("wrote %s (%d bytes)" % (p3, os.path.getsize(p3)))


if __name__ == "__main__":
    main()
