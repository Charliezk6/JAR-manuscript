# -*- coding: utf-8 -*-
"""Rasterise Figure 1 and Figure 2 to print-resolution PNG for the Word file.
Plotting data come from Data Availability Note Section 8.17 (unchanged)."""
import os

from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Users\Administrator\WorkBuddy\2026-10-23-06-03-49"
S = 3                      # supersampling factor (660x440 -> 1980x1320)
W, H = 660, 440
T, B = 46, 94
L, R = 78, 40
PW, PH = W - L - R, H - T - B
PAD = 24.0
CW, CH = W * S, H * S

FONT = None
for cand in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf",
             r"C:\Windows\Fonts\DejaVuSans.ttf"):
    if os.path.exists(cand):
        FONT = cand
        break


def f(sz):
    if FONT:
        return ImageFont.truetype(FONT, int(sz * S))
    return ImageFont.load_default()


def X(i, n):
    if n <= 1:
        return (L + PW / 2.0) * S
    return (L + PAD + (PW - 2 * PAD) * i / (n - 1.0)) * S


def Y(v, ymin, ymax):
    return (T + PH * (ymax - v) / (ymax - ymin)) * S


def dashed(d, p0, p1, dash, color, w):
    if not dash or dash == "solid":
        d.line([p0, p1], fill=color, width=w)
        return
    on, off = [float(x) for x in dash.split(",")]
    x0, y0 = p0
    x1, y1 = p1
    import math
    seg = math.hypot(x1 - x0, y1 - y0)
    if seg == 0:
        return
    ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
    pos, pen = 0.0, True
    while pos < seg:
        step = (on if pen else off) * S
        end = min(pos + step, seg)
        if pen:
            d.line([(x0 + ux * pos, y0 + uy * pos), (x0 + ux * end, y0 + uy * end)],
                   fill=color, width=w)
        pos = end
        pen = not pen


def marker(d, kind, x, y, color):
    r = 3.7 * S
    if kind == "circle":
        d.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=color)
    elif kind == "square":
        d.rectangle([x - r, y - r, x + r, y + r], fill=color, outline=color)
    elif kind == "tri":
        d.polygon([(x, y - r * 1.16), (x + r * 1.1, y + r * 0.95),
                   (x - r * 1.1, y + r * 0.95)], fill=color, outline=color)


def vtext(d, xy, text, font, fill):
    tmp = Image.new("RGBA", (font.size * (len(text) + 2), font.size * 2), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((0, 0), text, font=font, fill=fill)
    tmp = tmp.rotate(90, expand=True)
    d.bitmap = None
    img = d._image
    img.paste(tmp, (int(xy[0]), int(xy[1] - tmp.size[1] / 2)), tmp)


def build(series, ymin, ymax, step, xtitle, ytitle, xlabels, legend, band=None):
    img = Image.new("RGB", (CW, CH), "white")
    d = ImageDraw.Draw(img)
    AX = (0, 0, 0)
    GRID = (214, 214, 214)
    w1 = max(1, int(1.4 * S))

    # horizontal gridlines + y tick labels
    v = 0.0
    while v <= ymax + 1e-9:
        y = Y(v, ymin, ymax)
        d.line([(L * S, y), ((W - R) * S, y)], fill=GRID, width=max(1, int(0.8 * S)))
        lbl = ("%g" % round(v, 4))
        ft = f(11)
        d.text(((L - 10) * S - d.textlength(lbl, font=ft), y - ft.size * 0.62),
               lbl, font=ft, fill=AX)
        v += step
    v = -step
    while v >= ymin - 1e-9:
        y = Y(v, ymin, ymax)
        d.line([(L * S, y), ((W - R) * S, y)], fill=GRID, width=max(1, int(0.8 * S)))
        lbl = ("%g" % round(v, 4))
        ft = f(11)
        d.text(((L - 10) * S - d.textlength(lbl, font=ft), y - ft.size * 0.62),
               lbl, font=ft, fill=AX)
        v -= step

    # axes
    d.line([(L * S, T * S), (L * S, (H - B) * S)], fill=AX, width=w1)
    d.line([(L * S, (H - B) * S), ((W - R) * S, (H - B) * S)], fill=AX, width=w1)

    # shaded band (Figure 2: years two and three)
    if band:
        a, b = band
        d.rectangle([X(a, 5) - 6 * S, T * S, X(b, 5) + 6 * S, (H - B) * S],
                    fill=(240, 240, 240))

    n = len(xlabels)
    for label, vals, dash, mk, color in series:
        pts = [(X(i, n), Y(v, ymin, ymax)) for i, v in enumerate(vals)]
        for i in range(len(pts) - 1):
            dashed(d, pts[i], pts[i + 1], dash, color, w1)
        for (px, py) in pts:
            marker(d, mk, px, py, color)

        # x tick labels
    ft = f(12)
    for i, lb in enumerate(xlabels):
        w = d.textlength(str(lb), font=ft)
        d.text((X(i, n) - w / 2, (H - B + 10) * S), str(lb), font=ft, fill=AX)
    xw = d.textlength(xtitle, font=ft)
    d.text(((L + PW / 2.0) * S - xw / 2, (H - B + 34) * S), xtitle, font=ft, fill=AX)

    ft2 = f(11)
    vtext(d, ((L - 58) * S, (T + PH / 2.0) * S), ytitle, ft2, AX)

    # legend
    fl = f(11)
    total = 0.0
    widths = []
    for label, vals, dash, mk, color in series:
        w = d.textlength(label, font=fl) + 26 * S
        widths.append(w)
        total += w
    total += 18 * S * (len(series) - 1)
    x0 = (W * S - total) / 2.0
    y0 = (H - B + 56) * S
    for (label, vals, dash, mk, color), w in zip(series, widths):
        dashed(d, (x0, y0 + fl.size * 0.45), (x0 + 14 * S, y0 + fl.size * 0.45),
               dash, color, w1)
        marker(d, mk, x0 + 7 * S, y0 + fl.size * 0.45, color)
        d.text((x0 + 20 * S, y0), label, font=fl, fill=AX)
        x0 += w + 18 * S

    return img


def main():
    f1 = build(
        series=[
            ("Joint clusters (970 clusters, 2,622 cells)",
             [-0.202, -0.398, -0.269, 0.912, -0.612], "solid", "circle", (0, 0, 0)),
            ("All other clusters (6,781 clusters, 16,754 cells)",
             [-0.078, -0.025, -0.046, 0.103, 0.078], "6,3", "square", (90, 90, 90)),
            ("Balanced panel (1,203 firms)",
             [-0.032, -0.038, -0.042, 0.019, 0.147], "2,3", "tri", (150, 150, 150)),
        ],
        ymin=-0.75, ymax=1.00, step=0.25,
        xtitle="Signing-partner clock year",
        ytitle="Residualised mean E-score",
        xlabels=[1, 2, 3, 4, 5], legend=True)

    f2 = build(
        series=[
            ("Non-balanced firms (spells complete inside the window)",
             [0.0, 0.140, 0.181, 0.839, -0.359], "solid", "circle", (0, 0, 0)),
            ("Balanced firms (observed in all eleven years)",
             [0.0, -0.025, -0.040, 0.051, 0.163], "6,3", "square", (90, 90, 90)),
        ],
        ymin=-0.50, ymax=1.00, step=0.25,
        xtitle="Signing-partner clock year",
        ytitle="Implied E level against the year-one base",
        xlabels=[1, 2, 3, 4, 5], legend=True, band=(1, 2))

    p1 = os.path.join(BASE, "_fig1.png")
    p2 = os.path.join(BASE, "_fig2.png")
    f1.save(p1, "PNG", dpi=(300, 300))
    f2.save(p2, "PNG", dpi=(300, 300))
    print("saved %s %s" % (p1, f1.size))
    print("saved %s %s" % (p2, f2.size))


if __name__ == "__main__":
    main()
