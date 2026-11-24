#!/usr/bin/env python3
"""finance-charts-pptx.py — the two all-finance charts as a PowerPoint deck.

Bill's deck versions of the charts in the data-landscapers post *All finance dataset goes
live* (2026-10-05): "The rise of African finance" (yearly totals by source, 2024-2026) and
"Who pays for what" (topics over US$500 million, total and share by source). Built 2026-11-24
from the October method, which reproduces the post's images from that day's table. The post's
PNGs are not touched; this writes a .pptx with native, editable charts.

    python scripts/finance-charts-pptx.py [--src CSV] [--out PPTX]

Defaults: `site/finance/all/all-finance.csv`, and `~/Downloads/all-finance-charts-{today}.pptx`.
Needs `python-pptx`. The subtitles are fixed text: the script prints a WARNING when the data
no longer supports them, and the wording then needs revising by hand.
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
ap.add_argument("--out", default=os.path.join(os.path.expanduser("~"), "Downloads", f"all-finance-charts-{TODAY}.pptx"))
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
WORD = {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
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

# ---------- Slide 2: who pays for what ----------
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

prs.save(OUT)
print("saved", OUT, "| x", round(mult, 2), "|", n, "topics")
for t in order: print(NAMES[t], [round(yt[(y, t)]) for y in YEARS])
for k in topics: print(TOPIC.get(k, k), round(sum(tt[k].values())), {NAMES[t]: round(100*tt[k][t]/sum(tt[k].values())) for t in src})
