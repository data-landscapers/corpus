#!/usr/bin/env python3
"""finance-charts-pptx.py — the all-finance deck, rebuilt from the published tables alone.

    python scripts/finance-charts-pptx.py [--src CSV] [--out PPTX]

Reads three files and nothing else: `site/finance/all/all-finance.csv`, `lookups/country-reference.csv`
(area, population, names) and `lookups/taxonomy.csv` (topic to chapter). Map shapes come from
`site/maturity/data/africa.json`. Every slide covers YEARS. Bill's running order (2026-11-24):

1. Where the money goes: a pie of chapters, each big chapter's topics as bars drawn out from it.
1a. Where the money comes from: the same design, sources and their instruments; budgets get no panel.
2. Who pays for what: topics over US$500 million, total and share by source.
3. The foundations: FOUNDATIONS (Bill's ten) as 100% bars by source, under all digital finance.
4. The rise of African finance: yearly totals by source.
5. But the rise rests on a few deals: African finance as two treemaps, by country (continent-wide
   XAF and XSS merged as "Africa") and by financier (under US$15 million grouped as Other).
6. Where the money lands: connectivity per km² beside all digital finance per head (deliberately
   all finance; Bill, 2026-11-24). Regional codes and countries under SMALL_KM2 are left out.
7. The same two measures on one bivariate map.

Default output: `Claude outputs/all-finance-deck-{today}.pptx`. Needs `python-pptx`. The subtitles
carry fixed claims: the script prints a WARNING when the data no longer supports one.
"""
import argparse, datetime, os
import csv, io, sys, collections
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today()
ap = argparse.ArgumentParser()
ap.add_argument("--src", default=os.path.join(ROOT, "site", "finance", "all", "all-finance.csv"))
ap.add_argument("--out", default=os.path.join(ROOT, "Claude outputs", f"all-finance-deck-{TODAY}.pptx"))
a = ap.parse_args()
SRC, OUT = a.src, a.out
FONT = "Calibri"
INK, INK2, FAINT, RULE = "1A1A18", "4A4A44", "8A8A80", "D8D5CC"
PAPER, ACCENT, GREY = "FAF8F4", "C84B2F", "A8A79E"
SRC_COL = {"budget": "D9A23A", "other African finance": "C84B2F",
           "other non-African finance": "1A63A8", "aid": "5FA8DB"}
NAMES = {"budget": "National budgets", "other African finance": "African finance",
         "other non-African finance": "Non-African finance", "aid": "Aid"}
TOPIC = {"Data Storage": "Data storage", "Other GovTech and e-Gov": "Other GovTech and e-gov",
         "Digital Identity and CRVS": "Digital identity and CRVS", "Data Exchange": "Data exchange",
         "Digital Payments and Fintech": "Digital payments and fintech", "ICT Industry": "ICT industry"}
YEARS = ["2024", "2025", "2026"]
AS_AT = TODAY.strftime("%B %Y")

rows = list(csv.DictReader(io.open(SRC, encoding="utf-8-sig")))
REF = {r["ISO-3 Code"]: r for r in csv.DictReader(io.open(os.path.join(ROOT, "lookups", "country-reference.csv"), encoding="utf-8-sig"))}
CHAPTER = {r["Level 2"]: r["Level 1"] for r in csv.DictReader(io.open(os.path.join(ROOT, "lookups", "taxonomy.csv"), encoding="utf-8-sig"))}
REGION = {"XAF": "Africa", "XSS": "Africa", "XEA": "East Africa", "XWA": "West Africa", "XCA": "Central Africa",
          "XNA": "North Africa", "XSA": "Southern Africa"}
FOUNDATIONS = ["Standards", "Data protection", "Digitalisation of sub-national government", "Research institutions",
               "Legislation and regulation", "Regional collaboration", "Open data", "Digital divides",
               "Public debate and participation in policymaking", "Rural digital data capture"]   # Bill's ten
SMALL_KM2 = 12000      # leaves out Gambia, Cape Verde, Mauritius, Comoros, São Tomé and Seychelles
FIN_OTHER = 15         # US$ m: African financiers below this are one "Other" box
def usd(r): return float(r["value_usd"] or 0) / 1e6
INYEARS = [r for r in rows if r["year"] in YEARS]
unknown = {r["primary_topic"] for r in INYEARS} - set(CHAPTER)
if unknown: print("WARNING: topics missing from taxonomy.csv:", sorted(unknown))
yt = collections.defaultdict(float)
tt = collections.defaultdict(lambda: collections.defaultdict(float))
for r in rows:
    v = float(r["value_usd"] or 0) / 1e6
    yt[(r["year"], r["type"])] += v
    if r["year"] in YEARS:
        tt[r["primary_topic"]][r["type"]] += v

def rgb(h): return RGBColor.from_string(h)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]

def text(slide, x, y, w, h, runs, size, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = align
    if isinstance(runs, str): runs = [(runs, {})]
    for t, o in runs:
        r = p.add_run(); r.text = t
        r.font.name = FONT; r.font.size = Pt(o.get("size", size))
        r.font.bold = o.get("bold", bold); r.font.color.rgb = rgb(o.get("color", color))
    return tb

def frame(slide, title, sub, note):
    bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = rgb(PAPER)
    text(slide, 0.6, 0.35, 12.1, 0.7, title, 34, bold=True)
    text(slide, 0.6, 1.05, 11.0, 0.7, sub, 16, color=INK2)
    ln = slide.shapes.add_connector(1, Inches(0.6), Inches(6.62), Inches(12.73), Inches(6.62))
    ln.line.color.rgb = rgb(RULE); ln.line.width = Pt(0.75)
    text(slide, 0.6, 6.68, 12.1, 0.45, note, 10, color=FAINT)
    text(slide, 0.6, 7.08, 8, 0.25, "Source: Data Landscapers, All finance table", 10, color=INK, bold=True)
    text(slide, 8.7, 7.08, 4.03, 0.25, "data-landscapers.io", 10, color=FAINT, align=PP_ALIGN.RIGHT)

from pptx.oxml.ns import qn
from lxml import etree
from pptx.enum.chart import XL_TICK_MARK
def inner(chart, x, y, w, h):
    pa = chart._chartSpace.chart.plotArea
    old = pa.find(qn("c:layout"))
    if old is not None: pa.remove(old)
    lay = etree.SubElement(pa, qn("c:layout")); pa.remove(lay); pa.insert(0, lay)
    ml = etree.SubElement(lay, qn("c:manualLayout"))
    for tag, val in (("layoutTarget","inner"),("xMode","edge"),("yMode","edge"),("x",x),("y",y),("w",w),("h",h)):
        etree.SubElement(ml, qn("c:"+tag)).set("val", str(val))
def axis_font(ax, size=12, color=FAINT):
    ax.tick_labels.font.size = Pt(size); ax.tick_labels.font.name = FONT
    ax.tick_labels.font.color.rgb = rgb(color)

DEF = ("African and non-African finance: non-state commitments other than aid, by where the financier is from. "
       "Aid: grants, concessional loans and technical assistance. National budgets: states’ own digital lines. "
       "Commitments, not disbursements.")

# ---------- Slide 1: the rise of African finance ----------
s = prs.slides.add_slide(BLANK)
afr = [yt[(y, "other African finance")] for y in YEARS]
mult = afr[2] / afr[0]
WORD = {4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
if afr[2] <= yt[("2026", "budget")]:
    print("WARNING: African finance no longer exceeds national budgets in 2026; slide 1 subtitle is wrong")
frame(s, "The rise of African finance",
      f"African financiers committed {"nearly" if mult < round(mult) else "over"} {WORD.get(round(mult), round(mult))} times as much to the continent’s digital sector in 2026 "
      "as in 2024, overtaking what African states budget for it themselves.  US$ millions",
      DEF + f"  * 2026 as recorded to {AS_AT}.")
order = ["other non-African finance", "budget", "aid", "other African finance"]  # accent drawn last, on top
cd = CategoryChartData(); cd.categories = ["2024", "2025", "2026*"]
for t in order:
    cd.add_series(NAMES[t], [round(yt[(y, t)]) for y in YEARS])
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.6), Inches(1.85), Inches(9.0), Inches(4.65), cd)
ch = gf.chart; ch.has_legend = False; ch.has_title = False; ch.font.name = FONT
inner(ch, 0.08, 0.04, 0.9, 0.84)
va, ca = ch.value_axis, ch.category_axis
ca.major_tick_mark = XL_TICK_MARK.NONE
va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = rgb(RULE)
va.format.line.fill.background(); va.tick_labels.number_format = '#,##0'; va.tick_labels.number_format_is_linked = False
va.minimum_scale = 0; va.maximum_scale = 8000; va.major_unit = 2000
axis_font(va); axis_font(ca, 14, INK2); ca.format.line.color.rgb = rgb(INK2)
for ser, t in zip(ch.plots[0].series, order):
    hi = t == "other African finance"
    col = ACCENT if hi else GREY
    ser.format.line.color.rgb = rgb(col); ser.format.line.width = Pt(4.5 if hi else 2.5); ser.smooth = False
    ser.marker.style = 8; ser.marker.size = 11 if hi else 6
    ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = rgb(col)
    ser.marker.format.line.color.rgb = rgb(PAPER if hi else col)
    if hi:
        dl = ser.points[0].data_label; dl.has_text_frame = True; dl.text_frame.text = f"{afr[0]:,.0f}"
        dl.position = XL_LABEL_POSITION.BELOW
        f = dl.text_frame.paragraphs[0].runs[0].font; f.size = Pt(14); f.bold = True; f.color.rgb = rgb(INK); f.name = FONT
# end labels, placed against the plot's value scale
plot_top, plot_bot = 1.85 + 0.04 * 4.65, 1.85 + 0.88 * 4.65   # pinned inner plot area
def ypos(v): return plot_bot - (plot_bot - plot_top) * v / 8000
ends = sorted(((round(yt[("2026", t)]), t) for t in order), reverse=True)
placed = []
for v, t in ends:
    y = ypos(v) - 0.17
    if placed and y < placed[-1] + 0.36: y = placed[-1] + 0.36
    placed.append(y)
    hi = t == "other African finance"
    text(s, 9.85, y, 2.2, 0.34, NAMES[t], 15 if hi else 14, color=INK if hi else INK2, bold=hi)
    text(s, 11.8, y, 0.93, 0.34, f"{v:,}", 15 if hi else 14, color=INK if hi else INK2, bold=hi, align=PP_ALIGN.RIGHT)
text(s, 4.6, ypos(4200), 3.0, 0.4, f"×{mult:.1f} in two years", 16, color=ACCENT, bold=True)

# ---------- Slide 2: the reality check, as two treemaps ----------
def squarify(vals, x, y, w, h):
    """Squarified treemap (Bruls et al.); vals sorted descending, returns (x, y, w, h) each."""
    tot = sum(vals); vals = [v * w * h / tot for v in vals]; out = []
    def worst(row, side):
        s_ = sum(row); return max(max(side * side * r / (s_ * s_), s_ * s_ / (side * side * r)) for r in row)
    while vals:
        side = min(w, h); row = [vals.pop(0)]
        while vals and worst(row + [vals[0]], side) <= worst(row, side): row.append(vals.pop(0))
        s_ = sum(row)
        if w >= h:
            cw = s_ / h; yy = y
            for r in row: out.append((x, yy, cw, r / cw)); yy += r / cw
            x += cw; w -= cw
        else:
            rh = s_ / w; xx = x
            for r in row: out.append((xx, y, r / rh, rh)); xx += r / rh
            y += rh; h -= rh
    return out
def treemap(slide, items, x, y, w, h, heading):
    tot = sum(v for _, v in items)
    text(slide, x, y - 0.38, w, 0.3, heading, 14, color=INK2, bold=True)
    shades = ["C84B2F", "D4705A", "DE8E7D", "E7AB9F", "EEC5BC"]
    for i, ((name, v), (rx, ry, rw, rh)) in enumerate(zip(items, squarify([v for _, v in items], x, y, w, h))):
        big = v / tot >= 0.05
        col = shades[min(i, 4)] if name != "Other" else "D8D5CC"
        r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(rx), Inches(ry), Inches(rw), Inches(rh))
        r.fill.solid(); r.fill.fore_color.rgb = rgb(col); r.line.color.rgb = rgb(PAPER); r.line.width = Pt(1.5)
        r.shadow.inherit = False
        if rw < 0.75 or rh < 0.5: continue
        tf = r.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.06)
        size = 14 if v / tot >= 0.15 else 11 if big else 8
        dark = i >= 2 or name == "Other"
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
        r1 = p.add_run(); r1.text = name
        r1.font.size = Pt(size); r1.font.bold = True; r1.font.name = FONT
        r1.font.color.rgb = rgb(INK if dark else "FFFFFF")
        if rh >= 0.55:
            p2 = tf.add_paragraph(); r2 = p2.add_run()
            r2.text = f"{v / 1e6:,.0f}  ({100 * v / tot:.0f}%)" if big else f"{v / 1e6:,.0f}"
            r2.font.size = Pt(size); r2.font.name = FONT; r2.font.color.rgb = rgb(INK if dark else "FFFFFF")
    return tot
if True:
    tc, tf_ = collections.Counter(), collections.Counter()
    for r in INYEARS:
        if r["type"] != "other African finance": continue
        c = r["country"]; tc[REGION.get(c, REF.get(c, {}).get("Country Name", c))] += usd(r) * 1e6
        tf_[r["financier"]] += usd(r) * 1e6
    oth = sum(v for k, v in tf_.items() if v < FIN_OTHER * 1e6)
    ctry = tc.most_common()
    fin = [(k, v) for k, v in tf_.most_common() if v >= FIN_OTHER * 1e6] + ([("Other", oth)] if oth else [])
    s = prs.slides.add_slide(BLANK)
    ct, ft = sum(v for _, v in ctry), sum(v for _, v in fin)
    if abs(ct - ft) > 1e6 or abs(ct / 1e6 - sum(afr)) > 5:
        print(f"WARNING: treemap totals {ct/1e6:,.0f} / {ft/1e6:,.0f} do not match African finance 2024-2026, {sum(afr):,.0f}")
    f3 = sum(v for _, v in fin[:3]) / ft; c3 = sum(v for _, v in ctry[:3]) / ct
    frame(s, "But the rise rests on a few deals",
          f"Three financiers account for {100 * f3:.0f}% of African finance since 2024, and continent-wide deals "
          f"plus two countries take {100 * c3:.0f}%. Most African countries see little or none of it.  US$ millions",
          f"African finance: non-state commitments other than aid by financiers from Africa, 2024 to 2026, as recorded to {AS_AT}. "
          "Africa: continent-wide and multi-country commitments. Commitments, not disbursements.")
    treemap(s, ctry, 0.6, 2.3, 5.9, 4.15, "By country")
    treemap(s, fin, 6.83, 2.3, 5.9, 4.15, "By financier")

# ---------- Slide 3: who pays for what ----------
s = prs.slides.add_slide(BLANK)
frame(s, "Who pays for what in Africa’s digital sector",
      "African and non-African financiers back connectivity, data storage and AI. Identity, statistics, "
      "registries and e-government fall mostly to states’ own budgets.",
      "Topics receiving more than US$500 million are shown. " + DEF + f" 2024 to 2026, as recorded to {AS_AT}.")
# legend
x = 0.6
for t in ["budget", "other African finance", "other non-African finance", "aid"]:
    sw = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.88), Inches(0.2), Inches(0.2))
    sw.fill.solid(); sw.fill.fore_color.rgb = rgb(SRC_COL[t]); sw.line.fill.background()
    text(s, x + 0.28, 1.83, 2.2, 0.3, NAMES[t], 14, color=INK2)
    x += 0.28 + len(NAMES[t]) * 0.085 + 0.45
for k, t in (("Connectivity", ("other African finance", "other non-African finance")),
             ("Data Storage", ("other African finance", "other non-African finance")),
             ("AI", ("other African finance", "other non-African finance")),
             ("Digital Identity and CRVS", ("budget",)), ("National statistics", ("budget",)),
             ("Registries", ("budget",)), ("Other GovTech and e-Gov", ("budget",))):
    if sum(tt[k][x] for x in t) <= sum(tt[k].values()) / 2:
        print(f"WARNING: {k} is no longer mostly {' + '.join(t)}; slide 2 subtitle is wrong")
topics = sorted((k for k, d in tt.items() if sum(d.values()) > 500), key=lambda k: -sum(tt[k].values()))
cats = [TOPIC.get(k, k) for k in topics]
n = len(topics)
CH_Y, CH_H = 2.6, 4.0
text(s, 3.7, 2.3, 3, 0.3, "Total, US$ millions", 12, color=FAINT)
text(s, 7.1, 2.3, 3, 0.3, "Share by source, %", 12, color=FAINT)
# totals
cd = CategoryChartData(); cd.categories = list(reversed(cats))
cd.add_series("Total", [round(sum(tt[k].values())) for k in reversed(topics)])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.6), Inches(CH_Y), Inches(6.2), Inches(CH_H), cd)
ch = gf.chart; ch.has_legend = False; ch.has_title = False; ch.font.name = FONT
inner(ch, 0.5, 0.0, 0.5, 0.9)
pl = ch.plots[0]; pl.gap_width = 70
ser = pl.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb("B5B1A8")
pl.has_data_labels = True; dls = pl.data_labels
dls.number_format = '#,##0'; dls.number_format_is_linked = False; dls.position = XL_LABEL_POSITION.OUTSIDE_END
dls.font.size = Pt(12); dls.font.color.rgb = rgb(INK2); dls.font.name = FONT
va, ca = ch.value_axis, ch.category_axis
va.visible = False; va.has_major_gridlines = False; va.minimum_scale = 0
va.maximum_scale = max(sum(d.values()) for d in tt.values()) * 1.45
axis_font(ca, 12, INK); ca.format.line.color.rgb = rgb(INK2); ca.major_tick_mark = XL_TICK_MARK.NONE
# shares
src = ["budget", "other African finance", "other non-African finance", "aid"]
cd = CategoryChartData(); cd.categories = list(reversed(cats))
shares = {t: [100 * tt[k][t] / sum(tt[k].values()) for k in reversed(topics)] for t in src}
for t in src: cd.add_series(NAMES[t], [round(v, 1) for v in shares[t]])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED_100, Inches(7.0), Inches(CH_Y), Inches(5.73), Inches(CH_H), cd)
ch = gf.chart; ch.has_legend = False; ch.has_title = False; ch.font.name = FONT
inner(ch, 0.02, 0.0, 0.94, 0.9)
pl = ch.plots[0]; pl.gap_width = 70; pl.overlap = 100
va, ca = ch.value_axis, ch.category_axis
ca.tick_label_position = XL_TICK_LABEL_POSITION.NONE; ca.format.line.fill.background()
va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = rgb(RULE)
va.major_unit = 0.25; va.tick_labels.number_format = '0%'; va.tick_labels.number_format_is_linked = False
va.format.line.fill.background(); axis_font(va)
for ser, t in zip(pl.series, src):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(SRC_COL[t])
    ser.format.line.color.rgb = rgb(PAPER); ser.format.line.width = Pt(1)
    for i, v in enumerate(shares[t]):
        if round(v) >= 10:
            dl = ser.points[i].data_label; dl.has_text_frame = True; dl.text_frame.text = str(round(v))
            dl.position = XL_LABEL_POSITION.CENTER
            f = dl.text_frame.paragraphs[0].runs[0].font
            f.size = Pt(12); f.bold = True; f.name = FONT
            f.color.rgb = rgb(INK if t == "budget" else "FFFFFF")

# ---------- Last slide: chapters, with each chapter's topics drawn out ----------
import math
if True:
    cell = collections.defaultdict(lambda: collections.defaultdict(float))   # (chapter, topic) -> type -> US$ m
    for r in INYEARS:
        t = r["primary_topic"]
        if t in CHAPTER: cell[(CHAPTER[t], t)][r["type"]] += usd(r)
    chap = collections.OrderedDict()
    for (c, t), d in sorted(cell.items(), key=lambda kv: -sum(kv[1].values())):
        chap.setdefault(c, [0, collections.OrderedDict()]); chap[c][0] += sum(d.values()); chap[c][1][t] = sum(d.values())
    chap = collections.OrderedDict(sorted(chap.items(), key=lambda kv: -kv[1][0]))
    total = sum(c[0] for c in chap.values())
    big = [k for k, c in chap.items() if c[0] / total >= 0.025]
    small = [k for k in chap if k not in big]
    COL = dict(zip(big, ["C84B2F", "1A63A8", "D9A23A", "5FA8DB", "6E9E5A", "8E6BB0"]))
    CHN = {"ICT Infrastructure": "ICT infrastructure", "DPI": "Digital public infrastructure"}
    s = prs.slides.add_slide(BLANK)
    frame(s, "Where the money goes",
          f"All digital finance in Africa, 2024 to 2026, by chapter and topic. ICT infrastructure takes "
          f"{100 * chap[big[0]][0] / total:.0f}% and digital public infrastructure {100 * chap[big[1]][0] / total:.0f}%.  US$ millions",
          "All sources: national budgets, aid, and African and non-African finance. Grey slice: " + ", ".join(k.lower() for k in small) + ". "
          "Topics under 3% of their chapter are grouped as Other. "
          f"Commitments, not disbursements, as recorded to {AS_AT}.")
    # pie, pinned so its geometry is known
    CX, CY, R = 6.55, 4.15, 1.45
    cd = CategoryChartData(); cd.categories = [CHN.get(k, k) for k in big] + ["Other"]
    cd.add_series("Chapters", [round(chap[k][0]) for k in big] + [round(sum(chap[k][0] for k in small))])
    gf = s.shapes.add_chart(XL_CHART_TYPE.PIE, Inches(CX - R), Inches(CY - R), Inches(2 * R), Inches(2 * R), cd)
    ch = gf.chart; ch.has_legend = False; ch.has_title = False; inner(ch, 0, 0, 1, 1)
    START = 282  # puts ICT infrastructure upper right, DPI lower right, the rest on the left
    fsa = ch.plots[0]._element.find(qn("c:firstSliceAng"))
    if fsa is None: fsa = etree.SubElement(ch.plots[0]._element, qn("c:firstSliceAng"))
    fsa.set("val", str(START))
    ch.plots[0].vary_by_categories = True
    vals = [chap[k][0] for k in big] + [sum(chap[k][0] for k in small)]
    for i, pt in enumerate(ch.plots[0].series[0].points):
        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(COL[big[i]] if i < len(big) else GREY)
        pt.format.line.color.rgb = rgb(PAPER); pt.format.line.width = Pt(1.5)
    mids, acc = [], 0
    for v in vals:
        mids.append(math.radians(START + 360 * (acc + v / 2) / total)); acc += v
    def edge(a_, r_): return CX + r_ * math.sin(a_), CY - r_ * math.cos(a_)
    for i, v in enumerate(vals):   # percentages on the slices big enough to hold them
        if v / total >= 0.05:
            x_, y_ = edge(mids[i], R * 0.62)
            text(s, x_ - 0.5, y_ - 0.17, 1.0, 0.34, f"{100 * v / total:.0f}%", 16, color="FFFFFF", bold=True, align=PP_ALIGN.CENTER)
    # one panel per big chapter: (x, y, w, h)
    PANEL = {big[0]: (8.45, 1.75, 4.3, 2.05), big[1]: (8.45, 4.05, 4.3, 2.5),
             big[2]: (0.6, 5.15, 4.1, 1.4), big[3]: (0.6, 3.65, 4.1, 1.35), big[4]: (0.6, 1.75, 4.1, 1.75)}
    for i, k in enumerate(big):
        if k not in PANEL: continue
        px, py, pw, ph = PANEL[k]; ctot, tops = chap[k][0], chap[k][1]
        keep = [(t, v) for t, v in tops.items() if v / ctot >= 0.03]
        rest = [(t, v) for t, v in tops.items() if v / ctot < 0.03]
        if len(rest) == 1: keep += rest
        elif rest: keep.append(("Other", sum(v for _, v in rest)))
        text(s, px, py, pw, 0.3, [(CHN.get(k, k), {"bold": True, "color": COL[k]}), (f"  {ctot:,.0f}", {"color": INK2})], 13)
        cd = CategoryChartData(); cd.categories = [TOPIC.get(t, t) for t, _ in reversed(keep)]
        cd.add_series(k, [round(v) for _, v in reversed(keep)])
        gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(px), Inches(py + 0.3), Inches(pw), Inches(ph - 0.3), cd)
        c2 = gf.chart; c2.has_legend = False; c2.has_title = False; c2.font.name = FONT
        inner(c2, 0.62, 0.0, 0.25, 1.0)
        pl = c2.plots[0]; pl.gap_width = 40
        sr = pl.series[0]; sr.format.fill.solid(); sr.format.fill.fore_color.rgb = rgb(COL[k])
        pl.has_data_labels = True; dls = pl.data_labels
        dls.number_format = '#,##0'; dls.number_format_is_linked = False; dls.position = XL_LABEL_POSITION.OUTSIDE_END
        dls.font.size = Pt(10); dls.font.color.rgb = rgb(INK2); dls.font.name = FONT
        va, ca = c2.value_axis, c2.category_axis
        va.visible = False; va.has_major_gridlines = False; va.minimum_scale = 0
        axis_font(ca, 10, INK); ca.format.line.color.rgb = rgb(COL[k]); ca.major_tick_mark = XL_TICK_MARK.NONE
        # leader from the slice to the panel
        sx, sy = edge(mids[i], R + 0.04)
        tx = px - 0.1 if px > CX else px + pw + 0.1
        ty = py + ph / 2
        ln = s.shapes.add_connector(1, Inches(sx), Inches(sy), Inches(tx), Inches(ty))
        ln.line.color.rgb = rgb(COL[k]); ln.line.width = Pt(1.25)

# ---------- Where the money comes from: types, with each one's instruments drawn out ----------
if True:
    inst = collections.defaultdict(collections.Counter)   # type -> instrument -> US$ m
    for r in INYEARS: inst[r["type"]][r["instrument"] or "Unknown"] += usd(r)
    TYPES = ["other non-African finance", "other African finance", "aid", "budget"]   # clockwise from START
    TNAME = {"other non-African finance": "Non-African finance", "other African finance": "African finance",
             "aid": "Aid", "budget": "National budgets"}
    INAME = {"Self Funded": "Self-funded", "Unknown": "Not stated", "MoU": "MoU",
             "Concessional Loan": "Concessional loan", "Commercial Loan": "Commercial loan",
             "Technical Assistance": "Technical assistance", "Joint Venture": "Joint venture", "Line of Credit": "Line of credit"}
    tot_t = {t: sum(inst[t].values()) for t in TYPES}; total = sum(tot_t.values())
    s = prs.slides.add_slide(BLANK)
    frame(s, "Where the money comes from",
          f"All digital finance in Africa, {YEARS[0]} to {YEARS[-1]}, by source and instrument. Self-funded investment and "
          f"memoranda of understanding make up {100 * sum(inst[t][i] for t in TYPES[:2] for i in ('Self Funded', 'MoU')) / (tot_t[TYPES[0]] + tot_t[TYPES[1]]):.0f}% "
          "of African and non-African finance.  US$ millions",
          DEF + " Instruments under 3% of their source are grouped as Other. "
          f"National budgets have no instrument breakdown. As recorded to {AS_AT}.")
    CX, CY, R = 6.55, 4.15, 1.45
    cd = CategoryChartData(); cd.categories = [TNAME[t] for t in TYPES]
    cd.add_series("Sources", [round(tot_t[t]) for t in TYPES])
    gf = s.shapes.add_chart(XL_CHART_TYPE.PIE, Inches(CX - R), Inches(CY - R), Inches(2 * R), Inches(2 * R), cd)
    ch = gf.chart; ch.has_legend = False; ch.has_title = False; inner(ch, 0, 0, 1, 1)
    START = 346  # non-African finance upper right, African finance at the bottom, aid lower left, budgets upper left
    fsa = ch.plots[0]._element.find(qn("c:firstSliceAng"))
    if fsa is None: fsa = etree.SubElement(ch.plots[0]._element, qn("c:firstSliceAng"))
    fsa.set("val", str(START))
    ch.plots[0].vary_by_categories = True
    for i, pt in enumerate(ch.plots[0].series[0].points):
        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(SRC_COL[TYPES[i]])
        pt.format.line.color.rgb = rgb(PAPER); pt.format.line.width = Pt(1.5)
    mids, acc = [], 0
    for t in TYPES:
        mids.append(math.radians(START + 360 * (acc + tot_t[t] / 2) / total)); acc += tot_t[t]
    def edge(a_, r_): return CX + r_ * math.sin(a_), CY - r_ * math.cos(a_)
    for i, t in enumerate(TYPES):
        x_, y_ = edge(mids[i], R * 0.62)
        text(s, x_ - 0.5, y_ - 0.17, 1.0, 0.34, f"{100 * tot_t[t] / total:.0f}%", 16,
             color=INK if t == "budget" else "FFFFFF", bold=True, align=PP_ALIGN.CENTER)
    # budgets: named beside their slice, no panel
    x_, y_ = edge(mids[3], R + 0.15)
    text(s, x_ - 2.6, y_ - 0.5, 2.5, 0.3, [(TNAME["budget"], {"bold": True, "color": "B7801A"}), (f"  {tot_t['budget']:,.0f}", {"color": INK2})], 13, align=PP_ALIGN.RIGHT)
    text(s, x_ - 2.6, y_ - 0.2, 2.5, 0.3, "States’ own lines: no instruments", 10.5, color=FAINT, align=PP_ALIGN.RIGHT)
    PANEL = {TYPES[0]: (8.45, 1.75, 4.3, 2.75), TYPES[1]: (8.45, 4.75, 4.3, 1.8), TYPES[2]: (0.6, 4.45, 4.1, 1.3)}
    for i, k in enumerate(TYPES):
        if k not in PANEL: continue
        px, py, pw, ph = PANEL[k]; ctot = tot_t[k]
        tops = [(n, v) for n, v in inst[k].most_common() if v > 0]
        keep = [(n, v) for n, v in tops if v / ctot >= 0.03]
        rest = [(n, v) for n, v in tops if v / ctot < 0.03]
        if len(rest) == 1: keep += rest
        elif rest: keep.append(("Other", sum(v for _, v in rest)))
        col = SRC_COL[k]
        text(s, px, py, pw, 0.3, [(TNAME[k], {"bold": True, "color": col}), (f"  {ctot:,.0f}", {"color": INK2})], 13)
        cd = CategoryChartData(); cd.categories = [INAME.get(n, n) for n, _ in reversed(keep)]
        cd.add_series(k, [round(v) for _, v in reversed(keep)])
        gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(px), Inches(py + 0.3), Inches(pw), Inches(ph - 0.3), cd)
        c2 = gf.chart; c2.has_legend = False; c2.has_title = False; c2.font.name = FONT
        inner(c2, 0.62, 0.0, 0.25, 1.0)
        pl = c2.plots[0]; pl.gap_width = 40
        sr = pl.series[0]; sr.format.fill.solid(); sr.format.fill.fore_color.rgb = rgb(col)
        pl.has_data_labels = True; dls = pl.data_labels
        dls.number_format = '#,##0'; dls.number_format_is_linked = False; dls.position = XL_LABEL_POSITION.OUTSIDE_END
        dls.font.size = Pt(10); dls.font.color.rgb = rgb(INK2); dls.font.name = FONT
        va, ca = c2.value_axis, c2.category_axis
        va.visible = False; va.has_major_gridlines = False; va.minimum_scale = 0
        axis_font(ca, 10, INK); ca.format.line.color.rgb = rgb(col); ca.major_tick_mark = XL_TICK_MARK.NONE
        sx, sy = edge(mids[i], R + 0.04)
        tx = px - 0.1 if px > CX else px + pw + 0.1
        ln = s.shapes.add_connector(1, Inches(sx), Inches(sy), Inches(tx), Inches(py + ph / 2))
        ln.line.color.rgb = rgb(col); ln.line.width = Pt(1.25)

# ---------- Last slide: the foundations only states and donors pay for ----------
if True:
    cols = ["aid", "budget", "other African finance", "other non-African finance"]
    piv = collections.defaultdict(lambda: {c: 0.0 for c in cols})
    for (c, t), d in cell.items():
        for k, v in d.items(): piv[t][k] += v
    allf = {c: sum(piv[t][c] for t in piv) for c in cols}
    found = list(FOUNDATIONS)
    found.sort(key=lambda t: -sum(piv[t].values()))
    PRIV = ("other African finance", "other non-African finance")
    ftot = {c: sum(piv[k][c] for k in found) for c in cols}; fsum = sum(ftot.values())
    priv, privall = sum(ftot[c] for c in PRIV), sum(allf[c] for c in PRIV)
    s = prs.slides.add_slide(BLANK)
    frame(s, "The foundations only states and donors pay for",
          f"Standards, data protection, regulation, research and public participation get {100 * fsum / sum(allf.values()):.0f}% "
          f"of digital finance. Budgets and aid pay for nearly all of it; private finance put in US${priv:.1f} million of US${privall / 1000:.1f} billion.",
          f"Ten of the smallest topics, 2024 to 2026, as recorded to {AS_AT}. " + DEF)
    x = 0.6
    for t in ["budget", "aid", "other African finance", "other non-African finance"]:
        sw = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.88), Inches(0.2), Inches(0.2))
        sw.fill.solid(); sw.fill.fore_color.rgb = rgb(SRC_COL[t]); sw.line.fill.background()
        text(s, x + 0.28, 1.83, 2.2, 0.3, NAMES[t], 14, color=INK2)
        x += 0.28 + len(NAMES[t]) * 0.085 + 0.45
    text(s, 11.45, 2.2, 1.28, 0.3, "US$ millions", 12, color=FAINT, align=PP_ALIGN.RIGHT)
    cats = ["All digital finance", "The ten below"] + [TOPIC.get(k, k).replace("Public debate and participation in policymaking", "Public debate and participation") for k in found]
    data = [allf, ftot] + [piv[k] for k in found]
    order_ = ["budget", "aid", "other African finance", "other non-African finance"]
    cd = CategoryChartData(); cd.categories = list(reversed(cats))
    for t in order_:
        cd.add_series(NAMES[t], [round(100 * d[t] / sum(d.values()), 1) for d in reversed(data)])
    CY_, CH_ = 2.5, 4.05
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED_100, Inches(0.6), Inches(CY_), Inches(10.9), Inches(CH_), cd)
    ch = gf.chart; ch.has_legend = False; ch.has_title = False; ch.font.name = FONT
    inner(ch, 0.3, 0.0, 0.68, 0.92)
    pl = ch.plots[0]; pl.gap_width = 45; pl.overlap = 100
    va, ca = ch.value_axis, ch.category_axis
    va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = rgb(RULE)
    va.major_unit = 0.25; va.tick_labels.number_format = '0%'; va.tick_labels.number_format_is_linked = False
    va.format.line.fill.background(); axis_font(va)
    axis_font(ca, 12, INK); ca.format.line.color.rgb = rgb(INK2); ca.major_tick_mark = XL_TICK_MARK.NONE
    for ser, t in zip(pl.series, order_):
        ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(SRC_COL[t])
        ser.format.line.color.rgb = rgb(PAPER); ser.format.line.width = Pt(1)
        for i, d in enumerate(reversed(data)):
            v = 100 * d[t] / sum(d.values())
            if round(v) >= 8:
                dl = ser.points[i].data_label; dl.has_text_frame = True; dl.text_frame.text = str(round(v))
                dl.position = XL_LABEL_POSITION.CENTER
                f = dl.text_frame.paragraphs[0].runs[0].font
                f.size = Pt(11); f.bold = True; f.name = FONT; f.color.rgb = rgb(INK if t in ("budget", "aid") else "FFFFFF")
    n_ = len(cats); rowh = CH_ * 0.92 / n_
    for i, d in enumerate(data):
        text(s, 11.6, CY_ + rowh * i + rowh / 2 - 0.13, 1.13, 0.26, f"{sum(d.values()):,.0f}", 12,
             color=INK if i < 2 else INK2, bold=i < 2, align=PP_ALIGN.RIGHT)
    ln = s.shapes.add_connector(1, Inches(0.6), Inches(CY_ + rowh * 2), Inches(12.73), Inches(CY_ + rowh * 2))
    ln.line.color.rgb = rgb(INK2); ln.line.width = Pt(0.75)

# ---------- Connectivity per km² beside all finance per head: two maps, then one combined ----------
if True:
    import json
    area = {k: float(r["Area (sq km)"]) for k, r in REF.items() if r["Area (sq km)"]}
    popn = {k: float(r["Population"]) for k, r in REF.items() if r["Population"]}
    small = {k for k, v in area.items() if v < SMALL_KM2}
    spc, spa = collections.Counter(), collections.Counter()
    for r in INYEARS:
        c = r["country"]
        if c not in REF or c in small: continue
        spa[c] += usd(r) * 1e6
        if r["primary_topic"] == "Connectivity": spc[c] += usd(r) * 1e6
    perkm = {k: v / area[k] for k, v in spc.items() if v > 0 and k in area}
    perhd = {k: v / popn[k] for k, v in spa.items() if v > 0 and k in popn}   # all digital finance, deliberately
    geo = json.load(io.open(os.path.join(ROOT, "site", "maturity", "data", "africa.json"), encoding="utf-8"))
    NAME = {f["properties"]["iso3"]: f["properties"]["name"] for f in geo["features"]}
    NAME.update({"COD": "DR Congo", "CAF": "Central African Rep."})
    SHADES = ["F3D9D2", "E7AB9F", "D4705A", "C84B2F", "8E2F1B"]
    def bins(d, n=5):
        v = sorted(d.values()); return [v[int(len(v) * q / n)] for q in range(1, n)]
    def cls(x, b): return sum(x >= t for t in b)
    LON0, LON1, LAT0, LAT1 = -18.0, 52.0, -35.5, 38.0
    def shapes(slide, colf, ox, oy, h):
        sc = h / (LAT1 - LAT0)
        for f in geo["features"]:
            k = f["properties"]["iso3"]; g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                ring = poly[0]
                if len(ring) < 4: continue
                pts = [(Inches(ox + (x - LON0) * sc), Inches(oy + (LAT1 - y) * sc)) for x, y in ring]
                fb = slide.shapes.build_freeform(pts[0][0], pts[0][1], scale=1.0)
                fb.add_line_segments(pts[1:], close=True)
                shp = fb.convert_to_shape(); shp.name = k
                c = colf(k); shp.fill.solid(); shp.fill.fore_color.rgb = rgb(c or PAPER)
                shp.line.color.rgb = rgb(PAPER if c else 'B5B1A8'); shp.line.width = Pt(0.5); shp.shadow.inherit = False
        return ox + (LON1 - LON0) * sc
    def drawmap(slide, d, ox, oy, h, fmt, heading):
        b = bins(d)
        text(slide, ox, oy - 0.42, 5.5, 0.3, heading, 14, color=INK2, bold=True)
        right = shapes(slide, lambda k: SHADES[cls(d[k], b)] if k in d else "E6E3DC", ox, oy, h)
        edges = [min(d.values())] + b + [max(d.values())]
        lx, ly = ox, oy + h + 0.08
        for i in range(5):
            sw = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(lx + i * 0.95), Inches(ly), Inches(0.93), Inches(0.14))
            sw.fill.solid(); sw.fill.fore_color.rgb = rgb(SHADES[i]); sw.line.fill.background(); sw.shadow.inherit = False
            text(slide, lx + i * 0.95, ly + 0.17, 0.93, 0.22, f"{fmt(edges[i])}–{fmt(edges[i + 1])}", 9, color=INK2, align=PP_ALIGN.CENTER)
        tx = right + 0.1
        text(slide, tx, oy + 0.2, 1.9, 0.3, "Highest", 11, color=FAINT, bold=True)
        for i, (k, v) in enumerate(sorted(d.items(), key=lambda kv: -kv[1])[:5]):
            text(slide, tx, oy + 0.5 + i * 0.3, 1.35, 0.28, NAME.get(k, k), 11, color=INK)
            text(slide, tx + 1.2, oy + 0.5 + i * 0.3, 0.7, 0.28, fmt(v), 11, color=INK, bold=True, align=PP_ALIGN.RIGHT)
        text(slide, tx, oy + 2.2, 1.9, 0.3, "Lowest", 11, color=FAINT, bold=True)
        for i, (k, v) in enumerate(sorted(d.items(), key=lambda kv: kv[1])[:3]):
            text(slide, tx, oy + 2.5 + i * 0.3, 1.35, 0.28, NAME.get(k, k), 11, color=INK2)
            text(slide, tx + 1.2, oy + 2.5 + i * 0.3, 0.7, 0.28, fmt(v), 11, color=INK2, align=PP_ALIGN.RIGHT)
    both = sorted(set(perkm) & set(perhd))
    lowboth = [k for k in both if not cls(perkm[k], bins(perkm)) and not cls(perhd[k], bins(perhd))]
    def namelist(ks):
        ns = [NAME.get(k, k).replace("Central African Rep.", "the Central African Republic") for k in ks]
        return ", ".join(ns[:-1]) + " and " + ns[-1] if len(ns) > 1 else "".join(ns)
    FOOT = (f"{YEARS[0]} to {YEARS[-1]}, as recorded to {AS_AT}; commitments, not disbursements. Regional commitments and the "
            f"{WORD.get(len(small), len(small))} smallest countries are left out. ")
    # two maps
    s = prs.slides.add_slide(BLANK)
    top_a = max(perkm, key=perkm.get); top_h = max(perhd, key=perhd.get)
    frame(s, "Where the money lands",
          f"{NAME[top_a]} leads on connectivity per square kilometre, {NAME[top_h]} on all digital finance per head. "
          f"{namelist(lowboth)} are in the lowest fifth on both.",
          FOOT + "Grey: none recorded. Colours: five equal-count groups.")
    drawmap(s, perkm, 0.6, 2.25, 3.75, lambda v: f"{v:,.0f}", "Connectivity, US$ per square kilometre")
    drawmap(s, perhd, 6.85, 2.25, 3.75, lambda v: f"{v:,.1f}" if v < 10 else f"{v:,.0f}", "All digital finance, US$ per head")
    # one combined (bivariate) map: thirds of each measure, crossed
    BIV = [["E8E8E8", "E4ACAC", "C85A5A"],     # rows: per head low to high; columns: per km² low to high
           ["B0D5DF", "AD9EA5", "985356"],
           ["64ACBE", "627F8C", "574249"]]
    bk, bh = bins(perkm, 3), bins(perhd, 3)
    def cell(k): return cls(perhd[k], bh), cls(perkm[k], bk)
    s = prs.slides.add_slide(BLANK)
    corners = {(2, 2): [], (0, 2): [], (2, 0): [], (0, 0): []}
    for k in both:
        if cell(k) in corners: corners[cell(k)].append(k)
    frame(s, "Where the money lands, on one map",
          "Each country is shaded by both measures at once: red for connectivity per square kilometre, blue for "
          "all digital finance per head. Dark is high on both; pale is low on both.",
          FOOT + "Each measure split into three equal-count groups. Outlined: one measure or none recorded.")
    MX, MY, MH = 0.6, 1.95, 4.55
    right = shapes(s, lambda k: BIV[cell(k)[0]][cell(k)[1]] if k in both else None, MX, MY, MH)
    # key: a 3x3 grid, per km² rising to the right, per head rising upward
    KX, KY, KS = right + 0.75, 2.1, 0.36
    for r_ in range(3):
        for c_ in range(3):
            sq = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(KX + c_ * KS), Inches(KY + (2 - r_) * KS), Inches(KS), Inches(KS))
            sq.fill.solid(); sq.fill.fore_color.rgb = rgb(BIV[r_][c_]); sq.line.color.rgb = rgb(PAPER); sq.shadow.inherit = False
    text(s, KX, KY + 3 * KS + 0.05, 1.9, 0.25, "Connectivity per km² →", 10, color=INK2)
    tb = text(s, KX - 0.66, KY + 1.5 * KS - 0.12, 1.08, 0.25, "All per head →", 10, color=INK2, align=PP_ALIGN.CENTER)
    tb.rotation = 270
    # the four corners, named
    GX = KX + 1.45; gy = 1.95
    for (r_, c_), label in (((2, 2), "High on both"), ((0, 2), "Connectivity, little else"),
                            ((2, 0), "Other finance, little connectivity"), ((0, 0), "Low on both")):
        ks = sorted(corners[(r_, c_)], key=lambda k: -(perkm[k] / max(perkm.values()) + perhd[k] / max(perhd.values())))
        sw = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(GX), Inches(gy + 0.04), Inches(0.2), Inches(0.2))
        sw.fill.solid(); sw.fill.fore_color.rgb = rgb(BIV[r_][c_]); sw.line.fill.background(); sw.shadow.inherit = False
        text(s, GX + 0.3, gy, 3.3, 0.28, label, 12, color=INK, bold=True)
        text(s, GX + 0.3, gy + 0.3, 3.2, 0.75, ", ".join(NAME.get(k, k) for k in ks) or "None", 10.5, color=INK2)
        gy += 1.12

# Bill's running order (2026-11-24): the whole picture, then the rise and its reality check
ORDER = ["Where the money goes", "Where the money comes from", "Who pays for what", "The foundations", "The rise of African finance", "But the rise", "Where the money lands"]
lst = prs.slides._sldIdLst
rank = [next((i for i, t in enumerate(ORDER) if sl.shapes[0].text_frame.text.startswith(t)), 99) for sl in prs.slides]
ids = list(lst)
for sid in ids: lst.remove(sid)
for _, sid in sorted(zip(rank, ids), key=lambda p_: p_[0]): lst.append(sid)
prs.save(OUT)
print("saved", OUT, "| x", round(mult, 2), "|", n, "topics")
for t in order: print(NAMES[t], [round(yt[(y, t)]) for y in YEARS])
for k in topics: print(TOPIC.get(k, k), round(sum(tt[k].values())), {NAMES[t]: round(100*tt[k][t]/sum(tt[k].values())) for t in src})
