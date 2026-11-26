"""Build the two PDF reports of Khalid's Work.

    1. ../1_social_classes/HOW_CLASSES_ARE_DEFINED.pdf  - methodology note on the consumption-based social classes
    2. ../0_household_master/HIES_vs_Census_2023.pdf    - benchmarking HIES 2024-25 against the 2023 Census

Every number is computed here from the project's output files, except the Census 2023 benchmarks (CENSUS below).
Charts are drawn with matplotlib as SVG; pages are HTML printed to PDF with Microsoft Edge (headless).

Run from this folder:  python build_reports.py
Needs: ../0_household_master/outputs/household_master.csv and ../1_social_classes/outputs/household_classes.csv
"""
import io
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
FIG = HERE / "figures"
HTML = HERE / "html"
FIG.mkdir(exist_ok=True)
HTML.mkdir(exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ----------------------------------------------------------------------------------------------- style
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
CLASS_COLORS = ["#eda100", "#1baf7a", "#eb6834", "#2a78d6", "#e34948"]   # same class colours as the notebook charts; validated (CVD-safe adjacent pairs)
NAMES = ["Lower", "Lower-middle", "Middle", "Upper-middle", "Upper"]

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 8.5, "text.color": INK, "axes.labelcolor": INK2,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "xtick.color": INK2, "ytick.color": INK2,
    "xtick.major.size": 0, "ytick.major.size": 0, "xtick.major.pad": 4, "ytick.major.pad": 4,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
    "legend.frameon": False, "legend.fontsize": 8, "svg.fonttype": "none",
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.bbox": "tight", "savefig.pad_inches": 0.04,
    "hatch.color": ORANGE, "hatch.linewidth": 0.7,
})

def hgrid(ax):
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)

def save(fig, name):
    fig.savefig(FIG / f"{name}.svg")
    plt.close(fig)
    return (FIG / f"{name}.svg").read_text(encoding="utf-8").split("?>", 1)[-1]   # inline SVG

def wmean(x, w):
    return float(np.average(x, weights=w))

fmt0 = lambda v: f"{v:,.0f}"
fmt1 = lambda v: f"{v:,.1f}"
fmt2 = lambda v: f"{v:,.2f}"

# ----------------------------------------------------------------------------------------------- shared page CSS
CSS = """
@page { size: A4; margin: 22mm 19mm 20mm 19mm;
  @top-left { content: "%(running)s"; font: 7.5pt "Segoe UI"; color: #898781; vertical-align: bottom; padding-bottom: 3mm; }
  @top-right { content: "HIES 2024-25"; font: 7.5pt "Segoe UI"; color: #898781; vertical-align: bottom; padding-bottom: 3mm; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.5pt "Segoe UI"; color: #898781; vertical-align: top; padding-top: 3mm; }
  @bottom-left { content: "%(footer)s"; font: 7.5pt "Segoe UI"; color: #898781; vertical-align: top; padding-top: 3mm; }
}
@page :first { @top-left { content: none; } @top-right { content: none; } }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Segoe UI", system-ui, sans-serif; font-size: 9.6pt; line-height: 1.5; color: #1f1f1d; margin: 0; background: #fff;
  font-variant-numeric: tabular-nums; }
.kicker { font-size: 8pt; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #2a78d6; margin: 0 0 6pt; }
h1 { font-size: 19pt; font-weight: 600; line-height: 1.2; color: #0d366b; margin: 0 0 4pt; letter-spacing: -0.01em; }
.dek { font-size: 11pt; color: #52514e; margin: 0 0 12pt; font-weight: 300; }
.meta { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0 14pt; border-top: 1.4pt solid #0d366b; border-bottom: 0.6pt solid #c3c2b7;
  padding: 6pt 0 7pt; margin-bottom: 12pt; font-size: 7.8pt; color: #52514e; }
.meta b { display: block; color: #0b0b0b; font-size: 7pt; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1pt; }
.summary { background: #f4f8fd; border-left: 3pt solid #2a78d6; padding: 7pt 12pt 7pt 12pt; margin: 0 0 10pt; break-inside: avoid; }
.summary h2 { font-size: 9pt; text-transform: uppercase; letter-spacing: 0.08em; color: #0d366b; margin: 0 0 4pt; border: none; padding: 0; }
.summary ul { margin: 0; padding-left: 13pt; } .summary li { margin: 2.5pt 0; }
h2 { font-size: 12.5pt; font-weight: 600; color: #0d366b; margin: 16pt 0 5pt; break-after: avoid; }
h2 .n { color: #2a78d6; margin-right: 6pt; }
h3 { font-size: 10pt; font-weight: 600; color: #0b0b0b; margin: 10pt 0 3pt; break-after: avoid; }
p { margin: 0 0 6pt; text-align: justify; hyphens: auto; }
ul, ol { margin: 0 0 6pt; padding-left: 15pt; } li { margin: 1.5pt 0; }
.eq { display: grid; grid-template-columns: 1fr auto; align-items: center; margin: 4pt 0 6pt; padding: 0 0 0 18pt; break-inside: avoid; }
.eq math { font-size: 11pt; justify-self: center; }
.eq .no { color: #898781; font-size: 8.5pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 2pt 0 2pt; }
caption { caption-side: top; text-align: left; font-size: 8.6pt; color: #0b0b0b; padding: 0 0 4pt; }
caption b, figcaption b { color: #0d366b; }
thead th { border-top: 1.2pt solid #0b0b0b; border-bottom: 0.6pt solid #0b0b0b; font-weight: 600; padding: 4pt 5pt; text-align: left; vertical-align: bottom; }
tbody td { padding: 3pt 5pt; border-bottom: 0.4pt solid #e1e0d9; vertical-align: top; }
tbody tr:last-child td { border-bottom: 1.2pt solid #0b0b0b; }
tr.total td { font-weight: 600; border-top: 0.6pt solid #0b0b0b; }
tbody td:first-child { white-space: nowrap; }
td.r, th.r { text-align: right; } td.c, th.c { text-align: center; }
.nowrap tbody td { white-space: nowrap; padding-top: 2pt; padding-bottom: 2pt; }
.tbl { margin: 8pt 0 10pt; break-inside: avoid; }
.note { font-size: 7.4pt; color: #52514e; margin: 3pt 0 0; line-height: 1.4; text-align: left; }
figure { margin: 10pt 0 12pt; break-inside: avoid; }
figure svg { width: 100%; height: auto; display: block; }
figcaption { font-size: 8.6pt; margin: 0 0 5pt; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 14pt; }
.refs { font-size: 7.8pt; color: #52514e; } .refs li { margin: 2pt 0; }
a { color: #1c5cab; text-decoration: none; }
code { font-family: Consolas, monospace; font-size: 8pt; background: #f4f3ef; padding: 0 2pt; }
.pb { break-before: page; }
"""

def page(title, running, footer, body):
    css = CSS.replace("%(running)s", running).replace("%(footer)s", footer)
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head><body>{body}</body></html>'

def to_pdf(html, name, out):
    p = HTML / name
    p.write_text(html, encoding="utf-8")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={out}", p.as_uri()], check=True, capture_output=True)
    print("wrote", out)

def table(caption, head, rows, note="", align=None, total_last=False):
    align = align or ["l"] + ["r"] * (len(head) - 1)
    th = "".join(f'<th class="{a}">{h}</th>' for h, a in zip(head, align))
    trs = []
    for i, r in enumerate(rows):
        cls = ' class="total"' if total_last and i == len(rows) - 1 else ""
        trs.append(f"<tr{cls}>" + "".join(f'<td class="{a}">{v}</td>' for v, a in zip(r, align)) + "</tr>")
    note = f'<p class="note">{note}</p>' if note else ""
    return f'<div class="tbl"><table><caption>{caption}</caption><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>{note}</div>'

def figure(caption, svg, note=""):
    note = f'<p class="note">{note}</p>' if note else ""
    return f"<figure><figcaption>{caption}</figcaption>{svg}{note}</figure>"

def eq(mathml, no):
    return f'<div class="eq"><math display="block">{mathml}</math><span class="no">({no})</span></div>'

# ----------------------------------------------------------------------------------------------- data
master = pd.read_csv(WORK / "0_household_master/outputs/household_master.csv", low_memory=False)
cls = pd.read_csv(WORK / "1_social_classes/outputs/household_classes.csv")
d = master.merge(cls[["hhcode", "class_A", "class_C", "quintile", "per_person", "full_income_pp"]], on="hhcode")
W = d.weight
N_HH, N_POP, N_SAMPLE = W.sum(), d.pop_weight.sum(), len(d)


# =============================================================================================== REPORT 1: classes
# ---- per day and in 2023 PPP dollars (project standard: 2023 US dollars)
# World Bank WDI: PPP conversion factor, private consumption (PA.NUS.PRVT.PP), Pakistan 2023; CPI (FP.CPI.TOTL, 2010 = 100).
# HIES fieldwork ran Oct 2024 - Jun 2025, so the survey price level is the average of the 2024 and 2025 CPI.
PPP_2023 = 59.2849                                   # Rs per international $ in 2023 prices
CPI_2023 = 343.42108
CPI_HIES = (386.80386 + 400.51819) / 2
RS_PER_USD23 = PPP_2023 * CPI_HIES / CPI_2023        # Rs per 2023 PPP $ in 2024-25 prices
DAYS = 365 / 12
day_rs = lambda v: v / DAYS
day_usd = lambda v: v / DAYS / RS_PER_USD23

# K-means (Experiment 1) finds the thresholds; they are then rounded to fixed lines in 2023 PPP $ per person per day.
x = np.log(d.per_person)
centres = np.array([wmean(x[d.class_A == k], W[d.class_A == k]) for k in range(1, 6)])
cuts_km = np.exp((centres[:-1] + centres[1:]) / 2)
reproduced = (np.searchsorted(cuts_km, d.per_person, side="right") + 1 == d.class_A).mean() * 100
share_km = np.array([W[d.class_A == k].sum() for k in range(1, 6)]) / N_HH * 100

LINES_USD = np.array([3, 6, 10, 20])                 # the class lines: $ per person per day, 2023 PPP
cuts = LINES_USD * DAYS * RS_PER_USD23               # the same lines in Rs per person per month, 2024-25 prices
d["cls"] = np.searchsorted(cuts, d.per_person, side="right") + 1
km_same = W[d.cls == d.class_A].sum() / N_HH * 100
share = np.array([W[d.cls == k].sum() for k in range(1, 6)]) / N_HH * 100
hh_m = np.array([W[d.cls == k].sum() for k in range(1, 6)]) / 1e6
mean_pp = np.array([wmean(d.per_person[d.cls == k], W[d.cls == k]) for k in range(1, 6)])
size_k = np.array([wmean(d.hhsize[d.cls == k], W[d.cls == k]) for k in range(1, 6)])

# quintile cut points (household-weighted)
pp_exact = d.exp_total / d.hhsize
qcuts = [pp_exact[d.quintile == q].max() for q in range(1, 5)]

# income classes (Test C): income per person floored at the household-weighted 1st percentile
o = np.argsort(d.full_income_pp.to_numpy())
cw = np.cumsum(W.to_numpy()[o]) / N_HH
p1 = d.full_income_pp.to_numpy()[o][np.searchsorted(cw, 0.01)]
xc = np.log(np.maximum(d.full_income_pp, p1))
centres_c = np.array([wmean(xc[d.class_C == k], W[d.class_C == k]) for k in range(1, 6)])
cuts_c = np.exp((centres_c[:-1] + centres_c[1:]) / 2)
share_c = np.array([W[d.class_C == k].sum() for k in range(1, 6)]) / N_HH * 100
# income per person put into classes with the same fixed lines
inc_cls = np.searchsorted(cuts, d.full_income_pp, side="right") + 1
same = W[d.cls == inc_cls].sum() / N_HH * 100
near = W[np.abs(d.cls - inc_cls) <= 1].sum() / N_HH * 100

spend_avg, inc_avg = wmean(d.exp_total, W), wmean(d.income_full, W)

# ---- Figure: distribution with cut points
fig, ax = plt.subplots(figsize=(6.8, 1.65))
edges = np.r_[np.log(1500), np.log(cuts), np.log(400000)]
step = (edges[-1] - edges[0]) / 90
bins = np.unique(np.concatenate([np.linspace(a, b, max(2, int(round((b - a) / step)) + 1)) for a, b in zip(edges[:-1], edges[1:])]))
widths = np.diff(bins)
for k in range(1, 6):
    sel = d.cls == k
    h, _ = np.histogram(x[sel], bins=bins, weights=W[sel] / 1e6)
    h = h / widths * step
    ax.bar(bins[:-1], h, widths, align="edge", color=CLASS_COLORS[k - 1], label=NAMES[k - 1], linewidth=0)
    # name each class directly above its own bars (two of the colours are light, so the label carries identity)
    lo, hi = edges[k - 1], edges[k]
    xc = (lo + hi) / 2 if k < 5 else np.log(90000)
    ax.text(xc, h.max() + 0.06, NAMES[k - 1].replace("-", "-\n"), ha="center", va="bottom", fontsize=7.5, color=INK,
            fontweight="bold", linespacing=1.0)
for c in cuts:
    ax.axvline(np.log(c), color=INK, lw=0.8, ls=(0, (3, 2)), zorder=3)
top = ax.secondary_xaxis("top")                      # threshold values on their own scale, so they never collide with class names
top.set_xticks(np.log(cuts), [f"${v}" for v in LINES_USD], fontsize=7.5, color=INK)
top.tick_params(length=3, color=INK, pad=2)
top.spines["top"].set_visible(False)
ticks = [1, 2, 5, 10, 20, 50, 100]
ax.set_xticks(np.log(np.array(ticks) * DAYS * RS_PER_USD23), [f"${t}" for t in ticks])
ax.set_xlim(np.log(1500), np.log(400000)); ax.set_ylim(0, 2.35)
ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
ax.set_xlabel("Spending per person per day (2023 PPP $, ratio scale)")
ax.set_ylabel("Households (million)")
hgrid(ax)
svg_dist = save(fig, "classes_distribution")

# main earner's share of household income, by class (for the text)
g = d.groupby("cls")
main_share = np.array([wmean(gg.income_main_earner_month, gg.weight) / wmean(gg.income_full, gg.weight) * 100 for _, gg in g])

# ---- HTML
def rng(k, f):
    return f"below {f(cuts[0])}" if k == 0 else f"above {f(cuts[-1])}" if k == 4 else f"{f(cuts[k - 1])}–{f(cuts[k])}"

rows = [[NAMES[k], rng(k, lambda v: f"${day_usd(v):.0f}"),
         fmt1(share[k]), fmt1(hh_m[k]), fmt1(size_k[k])] for k in range(5)]
rows.append(["All households", "", "100.0", fmt1(N_HH / 1e6), fmt1(N_POP / N_HH)])
class_table = table("<b>Table 1.</b> The five classes, by spending per person per day (2023 PPP dollars)",
                    ["Class", "$ per person per day", "% of households", "Households (million)", "People per household"],
                    rows, total_last=True,
                    note=f"2023 PPP dollars per person per day (step 2); lines rounded from the K-means thresholds (step 5). "
                         f"Source: author's calculations from HIES 2024-25 (PBS), household-weighted.").replace('<div class="tbl">', '<div class="tbl nowrap">')

# ---- durable goods: % of households in each class owning at least one
# only the items that Ghani (2014, KSBL Working Paper 2014-11, Figures 19-20 and appendix table) also reports, so the two can be compared
DUR = [("Mobile phone", ["n_own_mobile"]), ("Electric fan", ["own_fan"]), ("Television", ["own_television", "own_lcd_led"]),
       ("Sewing machine", ["own_sewing_machine"]), ("Washing machine", ["own_washing_machine"]),
       ("Refrigerator or freezer", ["own_refrigerator", "own_freezer"]), ("Motorcycle or scooter", ["own_motorcycle", "own_scooter"]),
       ("Air cooler", ["own_air_cooler"]), ("Air conditioner", ["own_air_conditioner"]), ("Car", ["own_car"]),
       ("Tractor", ["own_tractor_trolley"])]
OWN = {}
dur_rows = []
for lab, cols in DUR:
    if cols is None:
        dur_rows.append([f"<i>{lab}</i>"] + [""] * 6)
        continue
    has = d[cols].fillna(0).sum(axis=1) > 0
    OWN[lab] = [W[has & (d.cls == k)].sum() / W[d.cls == k].sum() * 100 for k in range(1, 6)] + [W[has].sum() / N_HH * 100]
    dur_rows.append([lab] + [fmt0(v) for v in OWN[lab][:5]] + [f"<b>{fmt0(OWN[lab][5])}</b>"])
dur_table = table("<b>Table 3.</b> Ownership of durable goods by class (% of households owning at least one)",
                  ["Item"] + NAMES + ["All"], dur_rows,
                  note="The durables also reported by Ghani (2014) for PSLM 2010-11; his computer item is left out because HIES 2024-25 records only computer use. Mobile phone: at least one member owns one (Section 2C); other items: owned now (Section 7). "
                       "Source: HIES 2024-25, household-weighted.").replace('<div class="tbl">', '<div class="tbl nowrap">')

# ---- imputed (non-cash) consumption by class: owned-home rent, own produce, wages in kind, gifts in kind
d["imp_rent"] = d.exp_imputed_rent
d["imp_food"] = d.inkind_own_production - d.exp_imputed_rent      # v3 includes the owned-home rent
d["imp_all"] = d.imp_rent + d.imp_food + d.inkind_wages + d.inkind_gifts
IMP = ["imp_rent", "imp_food", "inkind_wages", "inkind_gifts", "imp_all"]
imp_rows = []
for k, g in [(k, d[d.cls == k]) for k in range(1, 6)] + [(0, d)]:
    tot = (g.exp_total * g.weight).sum()
    pct = [(g[v] * g.weight).sum() / tot * 100 for v in IMP]
    imp_rows.append([NAMES[k - 1] if k else "All households"] + [fmt1(p) for p in pct[:-1]] + [f"<b>{fmt1(pct[-1])}</b>", "$" + fmt2(day_usd(wmean(g.imp_all / g.hhsize, g.weight)))])
imp_share = (d.imp_all * W).sum() / (d.exp_total * W).sum() * 100
cash_class = np.searchsorted(cuts, (d.exp_total - d.imp_all) / d.hhsize, side="right") + 1
cash_share = np.array([W[cash_class == k].sum() for k in range(1, 6)]) / N_HH * 100
cash_same = W[cash_class == d.cls].sum() / N_HH * 100
imp_table = table("<b>Table 2.</b> Imputed (non-cash) consumption, % of each class's spending",
                  ["Class", "Home rent", "Own produce", "Wages", "Gifts", "Total", "$ per person per day"],
                  imp_rows, total_last=True,
                  note="Home rent: rental value of an owned home. Source: HIES 2024-25, Section 6A; household-weighted.").replace('<div class="tbl">', '<div class="tbl nowrap">')

# ---- urban and rural households classified separately (same K-means as Experiment 1, run within each area)
from sklearn.cluster import KMeans

def kmeans_cuts(pp, w):
    X = np.log(pp.to_numpy()).reshape(-1, 1)
    km = KMeans(n_clusters=5, n_init=50, tol=0, max_iter=3000, random_state=42).fit(X, sample_weight=w)
    c = np.sort(km.cluster_centers_[:, 0])
    return np.exp((c[:-1] + c[1:]) / 2)

AREA = {}
for area in ["urban", "rural"]:
    g = d[d.region == area]
    gw = g.weight
    ac = kmeans_cuts(g.per_person, gw)
    own = np.searchsorted(ac, g.per_person, side="right") + 1
    AREA[area] = dict(
        n=len(g), hh=gw.sum() / 1e6, cuts=ac,
        own=np.array([gw[own == k].sum() for k in range(1, 6)]) / gw.sum() * 100,
        nat=np.array([gw[g.cls == k].sum() for k in range(1, 6)]) / gw.sum() * 100,
        same=gw[own == g.cls].sum() / gw.sum() * 100,
        near=gw[np.abs(own - g.cls) <= 1].sum() / gw.sum() * 100)
U, R = AREA["urban"], AREA["rural"]
ur_ratio = U["cuts"] / R["cuts"]
cell = lambda v: f"${day_usd(v):.2f}"
area_table = table("<b>Table 4.</b> Class thresholds when each area is classified on its own (2023 PPP $ per person per day)",
                   ["Threshold", "Class line", "K-means: national", "urban only", "rural only", "Urban ÷ rural"],
                   [[f"{NAMES[i]} | {NAMES[i + 1]}", f"${LINES_USD[i]}", cell(cuts_km[i]), cell(U["cuts"][i]), cell(R["cuts"][i]), f"{ur_ratio[i]:.2f}"] for i in range(4)],
                   note=f"Urban: {U['n']:,} sampled households ({U['hh']:.1f} million); rural: {R['n']:,} ({R['hh']:.1f} million). Same K-means method as steps 3–4, weighted by the household weight.").replace('<div class="tbl">', '<div class="tbl nowrap">')

# Figure 2: one 100% bar per area, split into the five classes (same colours as Figure 1).
# Top block: everyone judged against the national thresholds. Bottom block: each area judged only against itself.
fig, ax = plt.subplots(figsize=(6.8, 1.9))
BARS = [("Urban", U["nat"]), ("Rural", R["nat"]), ("Urban", U["own"]), ("Rural", R["own"])]
ypos = [4.3, 3.4, 1.4, 0.5]
TEXT_ON = ["#0b0b0b", "#0b0b0b", "#0b0b0b", "#ffffff", "#ffffff"]          # dark text on light fills, white on dark
for y, (lab, vals) in zip(ypos, BARS):
    left = 0
    for k, v in enumerate(vals):
        ax.barh(y, v, 0.72, left=left, color=CLASS_COLORS[k], edgecolor="white", linewidth=1.2,
                label=NAMES[k] if y == ypos[0] else None)
        if v >= 4:
            ax.text(left + v / 2, y, f"{v:.0f}%", ha="center", va="center", fontsize=7.2, color=TEXT_ON[k], fontweight="bold")
        else:
            ax.text(101, y, f"{v:.0f}%", ha="left", va="center", fontsize=7.2, color=INK, fontweight="bold")
        left += v
    ax.text(-1.5, y, lab, ha="right", va="center", fontsize=8, color=INK)
ax.text(0, 5.05, "A.  Same class lines for everyone: " + ", ".join(f"\\${v}" for v in LINES_USD) + " (Table 1)", fontsize=8, color=INK, fontweight="bold", va="bottom")
ax.text(0, 2.15, "B.  Own K-means thresholds for each area: urban " + ", ".join(f"\\${day_usd(c):.2f}" for c in U["cuts"]) + ";  rural " + ", ".join(f"\\${day_usd(c):.2f}" for c in R["cuts"]), fontsize=8, color=INK, fontweight="bold", va="bottom")
ax.set_xlim(0, 105); ax.set_ylim(0, 5.6)
ax.set_yticks([]); ax.set_xticks([])
for sp in ax.spines.values():
    sp.set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.48, -0.02), ncol=5, handlelength=1, handleheight=1, columnspacing=1.4, fontsize=7.5)
svg_area = save(fig, "classes_urban_rural")

# imputed consumption by area, and its total share by (national) class within each area
def imp_pct(g, v):
    return (g[v] * g.weight).sum() / (g.exp_total * g.weight).sum() * 100
IMP_AREA = {}
area_imp_rows = []
for lab, g in [("Urban", d[d.region == "urban"]), ("Rural", d[d.region == "rural"]), ("All households", d)]:
    pct = [imp_pct(g, v) for v in IMP]
    IMP_AREA[lab] = dict(pct=pct, by_class=[imp_pct(g[g.cls == k], "imp_all") for k in range(1, 6)])
    area_imp_rows.append([lab] + [fmt1(p) for p in pct[:-1]] + [f"<b>{fmt1(pct[-1])}</b>",
                         "$" + fmt2(day_usd(wmean(g.imp_all / g.hhsize, g.weight))),
                         fmt0(g.weight[g.imp_rent > 0].sum() / g.weight.sum() * 100),
                         fmt0(g.weight[g.imp_food > 0].sum() / g.weight.sum() * 100)])
area_imp_table = table("<b>Table 5.</b> Imputed (non-cash) consumption in urban and rural households (% of spending, unless stated)",
                       ["Area", "Home rent", "Own produce", "Wages", "Gifts", "Total", "$ per person per day", "% of households: with home rent", "with own produce"],
                       area_imp_rows, total_last=True,
                       note="Same definitions as Table 2. Source: HIES 2024-25, Section 6A; household-weighted.").replace('<div class="tbl">', '<div class="tbl nowrap">')
IU, IR = IMP_AREA["Urban"], IMP_AREA["Rural"]

compare_table = table("<b>Table 2.</b> Thresholds under three definitions (Rs per person per month)",
                      ["Definition", "Lower | Lower-middle", "Lower-middle | Middle", "Middle | Upper-middle", "Upper-middle | Upper"],
                      [["Classes by spending (this note)"] + [fmt0(c) for c in cuts],
                       ["Classes by income (same method)"] + [fmt0(c) for c in cuts_c],
                       ["Quintiles (20% of households each)"] + [fmt0(c) for c in qcuts]],
                      note="Income = cash income from work and pensions, transfers (remittances, BISP, zakat), rent and profit, and income in kind (own produce, rental value of own home).")

body1 = f"""
<p class="kicker">Methodology note</p>
<h1>Consumption-Based Social Classes in Pakistan</h1>
<p class="dek">How the five classes and their thresholds are defined, using HIES 2024-25</p>
<div class="meta">
  <div><b>Data</b>HIES 2024-25, Pakistan Bureau of Statistics</div>
  <div><b>Sample</b>{N_SAMPLE:,} households; four provinces and Islamabad</div>
  <div><b>Unit of analysis</b>Household ({N_HH / 1e6:.1f} million, weighted)</div>
  <div><b>Date</b>November 2026</div>
</div>
<div class="summary"><h2>Summary</h2><ul>
  <li>Households are ranked by spending <b>per person</b> and divided into five classes at <b>$3, $6, $10 and $20</b> per person per day, in 2023 PPP dollars. These lines are the K-means thresholds rounded.</li>
  <li>{share[1] + share[2]:.0f}% of households are lower-middle or middle class; {share[4]:.1f}% ({hh_m[4]:.1f} million households) are upper class.</li>
  <li>Ownership rises steeply with class: {OWN["Car"][4]:.0f}% of upper-class households own a car and {OWN["Air conditioner"][4]:.0f}% an air conditioner, against {OWN["Car"][2]:.0f}% and {OWN["Air conditioner"][2]:.0f}% in the middle class.</li>
</ul></div>

<h2><span class="n">1</span>How the classes are made</h2>
<ol>
  <li><b>Add up each household's spending for one month.</b> This includes everything the household consumed: what it bought, food it grew itself, the rent value of a house it owns, and goods received as wages or gifts. Items asked about over 14 days or 12 months are converted to one month.</li>
  <li><b>Convert to dollars per person per day.</b> Divide by the number of household members, so a large family is not ranked as rich just because it spends more in total; then by 30.4 days and by Rs {RS_PER_USD23:.2f}, the value of one 2023 PPP dollar at 2024-25 prices (the World Bank’s 2023 PPP rate for household consumption, Rs {PPP_2023:.2f}, raised by the {(CPI_HIES / CPI_2023 - 1) * 100:.1f}% price rise to 2024-25).</li>
  <li><b>Let K-means find five groups.</b> K-means places five centres along the spending scale and puts every household, counted with its weight, with its nearest centre. Spending is compared on a ratio scale, so “twice as much” is the same step for poor and rich.</li>
  <li><b>Read off the thresholds.</b> The boundary between two neighbouring classes lies halfway between their centres on that ratio scale. This is the square root of the two centres multiplied together: for example √({day_usd(np.exp(centres[0])):.2f} × {day_usd(np.exp(centres[1])):.2f}) = ${day_usd(cuts_km[0]):.2f}. The four K-means thresholds are {", ".join("$" + fmt2(day_usd(c)) for c in cuts_km)}.</li>
  <li><b>Round them to fixed class lines: ${", $".join(str(v) for v in LINES_USD)}.</b> Round lines are easier to use and, being fixed in 2023 dollars, can be applied unchanged to other survey rounds. {km_same:.0f}% of households are in the same class as under the exact K-means thresholds.</li>
  <li><b>Count the households in each class</b> by adding up their weights.</li>
</ol>

<h2><span class="n">2</span>Checks</h2>
<ul>
  <li><b>Same result every time.</b> K-means is run from 50 random starts and gives the same classes; its thresholds reproduce {reproduced:.0f}% of them, and the rounded lines keep {km_same:.0f}% of households in the same class.</li>
  <li><b>Income gives the same picture.</b> Ranked by income per person with the same lines, {same:.0f}% of households keep their class and {near:.0f}% stay within one class.</li>  <li><b>Totals match the official report.</b> Average household spending and income are within {max(spend_avg / 79150, inc_avg / 82179) * 100 - 100:.0f}% of the PBS HIES 2024-25 report ({spend_avg / 79150 * 100 - 100:.1f}% and {inc_avg / 82179 * 100 - 100:.1f}% higher).</li>
</ul>

<h2><span class="n">3</span>Results</h2>
{class_table}
{figure("<b>Figure 1.</b> Households by spending per person, with the class thresholds", svg_dist,
        "Dashed lines: class lines, in 2023 PPP $ per person per day. The distribution has one peak and no natural gaps; unlike quintiles, the classes give a large middle and a small upper class. Source: HIES 2024-25, household-weighted.")}

<h2><span class="n">4</span>Reading the class lines</h2>
<ul>
  <li><b>They are spending per person, not salaries.</b> A family of six is upper class only if it spends more than 6 × ${LINES_USD[3]} = ${6 * LINES_USD[3]} a day. One earner on $15 a day supporting six people gives $2.50 per person: lower class. The main earner provides only {main_share.min():.0f}–{main_share.max():.0f}% of household income.</li>
  <li><b>Spending includes imputed consumption</b> (Table 2): {imp_share:.1f}% of household spending is not paid in cash. Poorer classes rely more on own produce and gifts, the upper class on the rental value of its homes. With cash spending only and the same thresholds, the lower class would be {cash_share[0]:.0f}% of households instead of {share[0]:.0f}%, the upper class {cash_share[4]:.1f}% instead of {share[4]:.1f}%, and only {cash_same:.0f}% of households would keep their class.</li>
  <li><b>Limits.</b> Spending is not wealth and prices differ between regions. K-means thresholds would move with each survey round; the fixed lines do not, so they can be used for comparisons over time after converting each round's spending to 2023 PPP dollars. The $2/$4/$6 lines of the Middle and Affluent Class analysis are in 2011 PPP dollars and not directly comparable.</li>
</ul>
{imp_table}

<h2><span class="n">5</span>What each class owns</h2>
{dur_table}
<ul>
  <li><b>A mobile phone and an electric fan are near-universal</b>: {OWN["Mobile phone"][0]:.0f}% and {OWN["Electric fan"][0]:.0f}% of households own them even in the lower class.</li>
  <li><b>A refrigerator, washing machine and television mark the middle class</b>: each is owned by {min(OWN[i][2] for i in ["Refrigerator or freezer", "Washing machine", "Television"]):.0f}–{max(OWN[i][2] for i in ["Refrigerator or freezer", "Washing machine", "Television"]):.0f}% of middle-class households but only {min(OWN[i][0] for i in ["Refrigerator or freezer", "Washing machine", "Television"]):.0f}–{max(OWN[i][0] for i in ["Refrigerator or freezer", "Washing machine", "Television"]):.0f}% of lower-class ones.</li>
  <li><b>A car and an air conditioner mark the top</b>: {OWN["Car"][4]:.0f}% and {OWN["Air conditioner"][4]:.0f}% of upper-class households own them, against {OWN["Car"][2]:.0f}% and {OWN["Air conditioner"][2]:.0f}% of the middle class. Ghani (2014) found the same ladder in 2010-11: fan, mobile and TV, then washing machine and fridge, then motorcycle, then car and AC.</li>
  <li><b>Not everything rises with class:</b> sewing machines and motorcycles level off above the middle class, and tractors are rare in every class (at most {max(OWN["Tractor"][:5]):.0f}%).</li>
</ul>

<h2 style="break-before: page; margin-top: 0"><span class="n">6</span>Urban and rural households classified separately</h2>
<p>Steps 1–4 (K-means) were repeated separately for urban and for rural households (Table 4).</p>
{area_table}
{figure("<b>Figure 2.</b> How urban and rural households divide into the five classes (% of households in the area)", svg_area,
        "Each bar = 100% of the area’s households; thresholds in 2023 PPP $ per person per day. A: Table 1 classes split by area. B: each area ranked against itself. Source: HIES 2024-25, household-weighted.")}
<ul>
  <li><b>Compared with all of Pakistan (A), the areas differ.</b> City households spend more, so they sit higher: {U["nat"][4]:.1f}% of urban households are upper class against {R["nat"][4]:.1f}% of rural ones, and {R["nat"][0]:.0f}% of rural households are lower class against {U["nat"][0]:.1f}% of urban ones.</li>
  <li><b>Compared only with their own area (B), they split the same way,</b> close to the national K-means split of {" / ".join(f"{v:.0f}" for v in share_km)}%. Inequality within cities and within villages has the same shape; only the level differs. Urban thresholds are {ur_ratio[0]:.1f} times the rural ones at the bottom and {ur_ratio[-1]:.1f} times at the top, so higher urban prices alone cannot explain the gap.</li>
  <li><b>Which to use.</b> HIES has no regional price index, so part of the gap is the higher urban cost of living. Use A for a Pakistan-wide picture and B to compare households with their neighbours.</li>
</ul>
{area_imp_table}
<p><b>Overall, imputed consumption is {IR["pct"][-1]:.1f}% of rural and {IU["pct"][-1]:.1f}% of urban household spending</b> ({IMP_AREA["All households"]["pct"][-1]:.1f}% for all households). In rural areas it is mostly own produce and stays at {min(IR["by_class"]):.0f}–{max(IR["by_class"]):.0f}% in every class: richer rural households grow less of their food but own more valuable homes. In cities it is mostly the rental value of owned homes and rises from {IU["by_class"][0]:.0f}% in the lower class to {IU["by_class"][4]:.0f}% in the upper class (Table 1 classes).</p>
"""
to_pdf(page("Consumption-Based Social Classes in Pakistan", "Consumption-Based Social Classes in Pakistan", "Methodology note", body1),
       "classes.html", WORK / "1_social_classes/HOW_CLASSES_ARE_DEFINED.pdf")


# =============================================================================================== REPORT 2: census
CENSUS = {   # 7th Population and Housing Census 2023 (PBS), reference date 1 March 2023
    "population": 241.49e6, "households": 38.29e6, "hh_size": 6.30, "rural_pop_pct": 61.18,
    "households_2017": 31.92e6, "pop_growth": 2.55,
    "pop": {"punjab": 127.69e6, "sindh": 55.69e6, "kp": 40.85e6, "balochistan": 14.89e6, "islamabad": 2.36e6},
    "rural": {"punjab": 59, "sindh": 47, "kp": 85, "balochistan": 69, "islamabad": 53},
    "grid": 84.03, "solar": 7.74,
}
PROVS = ["punjab", "sindh", "kp", "balochistan", "islamabad"]
PNAME = {"punjab": "Punjab", "sindh": "Sindh", "kp": "Khyber Pakhtunkhwa", "balochistan": "Balochistan", "islamabad": "Islamabad"}

dates = pd.to_datetime(master.interview_date).dropna().sort_values()
mid = pd.Timestamp(int(np.median(dates.astype("int64"))))
t = (mid - pd.Timestamp("2023-03-01")).days / 365.25
g_hh = (CENSUS["households"] / CENSUS["households_2017"]) ** (1 / 6) - 1
proj_hh = CENSUS["households"] * (1 + g_hh) ** t
proj_pop = CENSUS["population"] * (1 + CENSUS["pop_growth"] / 100) ** t
M = master
rural = M.region == "rural"
size = N_POP / N_HH
rural_pop = M.pop_weight[rural].sum() / N_POP * 100
rural_hh = M.weight[rural].sum() / N_HH * 100
size_r = M.pop_weight[rural].sum() / M.weight[rural].sum()
size_u = M.pop_weight[~rural].sum() / M.weight[~rural].sum()
lit = M.s5m1q10.fillna("")
grid = M.weight[lit.str.startswith("electricity")].sum() / N_HH * 100
grid_only = M.weight[lit == "electricity (main grid)"].sum() / N_HH * 100
solar = M.weight[lit == "solar only"].sum() / N_HH * 100

pv = pd.DataFrame({
    "hh": M.groupby("province").weight.sum(),
    "pop": M.groupby("province").pop_weight.sum(),
    "rural": M[rural].groupby("province").pop_weight.sum() / M.groupby("province").pop_weight.sum() * 100,
}).loc[PROVS]
pv["size"] = pv["pop"] / pv.hh
pv["pop_pct"] = pv["pop"] / N_POP * 100
pv["c_pop"] = pd.Series(CENSUS["pop"])
pv["c_pop_pct"] = pv.c_pop / pv.c_pop.sum() * 100
pv["c_rural"] = pd.Series(CENSUS["rural"])

# ---- Figure: national totals (two panels, no dual axis)
fig, axes = plt.subplots(1, 2, figsize=(6.8, 1.6))
for ax, (hies, cen, proj, unit) in zip(axes, [(N_HH, CENSUS["households"], proj_hh, "Households (million)"),
                                              (N_POP, CENSUS["population"], proj_pop, "Population (million)")]):
    vals = np.array([hies, cen, proj]) / 1e6
    bars = ax.barh([2, 1, 0], vals, 0.62, color=[BLUE, ORANGE, "white"], edgecolor=[BLUE, ORANGE, ORANGE], linewidth=1.1)
    bars[2].set_hatch("////")
    for b, v in zip(bars, vals):
        ax.text(v + vals.max() * 0.015, b.get_y() + b.get_height() / 2, f"{v:.1f}", va="center", fontsize=8, color=INK)
    ax.set_yticks([2, 1, 0], ["HIES 2024-25", "Census, Mar 2023", f"Census grown to {mid:%b %Y}"])
    ax.set_xlim(0, vals.max() * 1.15); ax.set_title(unit, fontsize=8.5, color=INK, loc="left", pad=4)
    ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); ax.spines["left"].set_visible(False)
axes[1].set_yticklabels([])
fig.tight_layout(w_pad=1.5)
svg_nat = save(fig, "census_national")

sign = lambda txt: txt.replace("-", "−")
gap = lambda a, b: sign(f"{(a / b - 1) * 100:+.1f}%")
nat = table("<b>Table 1.</b> Pakistan: HIES 2024-25 and the census",
            ["", "HIES 2024-25", "Census 2023", f"Census grown to {mid:%b %Y}", "Difference"],
            [["Households (million)", fmt2(N_HH / 1e6), fmt2(CENSUS["households"] / 1e6), fmt2(proj_hh / 1e6), gap(N_HH, proj_hh) + "<sup>a</sup>"],
             ["Population (million)", fmt2(N_POP / 1e6), fmt2(CENSUS["population"] / 1e6), fmt2(proj_pop / 1e6), gap(N_POP, proj_pop) + "<sup>a</sup>"],
             ["People per household", fmt2(size), fmt2(CENSUS["hh_size"]), "", gap(size, CENSUS["hh_size"])],
             ["People living in rural areas (%)", fmt1(rural_pop), fmt1(CENSUS["rural_pop_pct"]), "", sign(f"{rural_pop - CENSUS['rural_pop_pct']:+.1f} points")],
             ["Households in rural areas (%)", fmt1(rural_hh), "not published", "", ""],
             ["Households lit by grid electricity (%)", fmt1(grid), fmt1(CENSUS["grid"]), "", sign(f"{grid - CENSUS['grid']:+.1f} points")]],
            note="<sup>a</sup> Compared with the census grown to the HIES interview period. Other rows are compared with the census of March 2023. "
                 "Grid electricity in HIES includes households using grid and solar together; the census may count these differently.")

prov = table("<b>Table 2.</b> Provinces: HIES 2024-25 and Census 2023",
             ["Province", "Households, HIES (m)", "Population, HIES (m)", "Population, Census (m)",
              "% of population, HIES", "% of population, Census", "% rural, HIES",
              "% rural, Census", "People per household, HIES"],
             [[PNAME[p], fmt2(r.hh / 1e6), fmt1(r["pop"] / 1e6), fmt1(r.c_pop / 1e6), fmt1(r.pop_pct), fmt1(r.c_pop_pct),
               fmt1(r.rural), f"{r.c_rural:.0f}", fmt2(r["size"])] for p, r in pv.iterrows()]
             + [["Pakistan", fmt2(N_HH / 1e6), fmt1(N_POP / 1e6), fmt1(pv.c_pop.sum() / 1e6), "100.0", "100.0",
                 fmt1(rural_pop), fmt1(CENSUS["rural_pop_pct"]), fmt2(size)]],
             total_last=True,
             note="m = million; % rural = share of the province's people living in rural areas. Census rural shares are published rounded to whole numbers. Islamabad is identified from the first digit "
                  "of the HIES area code (the raw files code it as Punjab). The census releases consulted do not give households by province.")

max_share_gap = np.abs(pv.pop_pct - pv.c_pop_pct).max()
max_rural_gap = np.abs(pv.rural - pv.c_rural).max()

body2 = f"""
<p class="kicker">Technical note</p>
<h1>Benchmarking HIES 2024-25 against the 2023 Census</h1>
<p class="dek">Households, population, rural share and provinces</p>
<div class="meta">
  <div><b>Survey</b>HIES 2024-25, {N_SAMPLE:,} households interviewed {dates.min():%b %Y} – {dates.max():%b %Y}</div>
  <div><b>Benchmark</b>7th Population and Housing Census, 1 March 2023</div>
  <div><b>Coverage</b>Four provinces and Islamabad (AJK and Gilgit-Baltistan in neither)</div>
  <div><b>Date</b>November 2026</div>
</div>
<div class="summary"><h2>Summary</h2><ul>
  <li><b>Households:</b> HIES gives {N_HH / 1e6:.1f} million, within {abs(N_HH / proj_hh - 1) * 100:.1f}% of the census figure brought forward to the survey period.</li>
  <li><b>Population:</b> HIES gives {N_POP / 1e6:.1f} million, about {abs(N_POP / proj_pop - 1) * 100:.0f}% below the census figure brought forward, because HIES households are smaller ({size:.2f} people against {CENSUS['hh_size']:.2f}).</li>
  <li><b>Rural share and provinces:</b> agree with the census to within one percentage point.</li>
</ul></div>

<h2><span class="n">1</span>How the comparison works</h2>
<ul>
  <li><b>HIES totals.</b> Each of the {N_SAMPLE:,} surveyed households has a weight: the number of Pakistani households it stands for. Adding up the weights gives the number of households in Pakistan. Adding up weight × household members gives the population.</li>
  <li><b>Same point in time.</b> The census counted Pakistan in March 2023; HIES interviews were about two years later (middle: {mid:%B %Y}). The census counts are therefore also grown to {mid:%B %Y} at the census's own yearly growth rates: {g_hh * 100:.1f}% for households and {CENSUS['pop_growth']:.2f}% for population.</li>
</ul>

<h2><span class="n">2</span>Pakistan</h2>
{nat}
<p><b>The number of households agrees.</b> HIES counts {N_HH / 1e6:.1f} million households, {gap(N_HH, CENSUS['households'])[1:]} more than the census found in March 2023. That is about two years of growth: compared with the census grown to {mid:%B %Y}, HIES is only {gap(N_HH, proj_hh)[1:]} lower.</p>
<p><b>The population is lower than expected.</b> HIES finds the same population as the 2023 census ({N_POP / 1e6:.1f} against {CENSUS['population'] / 1e6:.1f} million), but by 2025 the population should have grown to about {proj_pop / 1e6:.0f} million. The reason is household size: HIES records {size:.2f} people per household, the census {CENSUS['hh_size']:.2f}. HIES counts only usual household members, does not cover people living in hostels, barracks or prisons, and, like most surveys, tends to miss some very large households.</p>

{figure("<b>Figure 1.</b> Households and population", svg_nat, "Source: HIES 2024-25 (author's calculations); PBS, Census 2023.")}
<h2><span class="n">3</span>Provinces</h2>
{prov}
<p>Each province's share of the population is within {max_share_gap:.1f} percentage points of the census, and each province's rural share within {max_rural_gap:.1f} points. This is expected, as the HIES sample was drawn from the census, and confirms that the weights are applied correctly.</p>

<h2><span class="n">4</span>Conclusions</h2>
<ul>
  <li>HIES reproduces the census picture of where people live: by province and between rural and urban areas.</li>
  <li>The number of households ({N_HH / 1e6:.1f} million) is the most reliable HIES total. This supports using the household as the unit of analysis.</li>
  <li>Population totals from HIES are about {abs(N_POP / proj_pop - 1) * 100:.0f}% too low for 2025 and should be quoted with that caveat.</li>
</ul>
<p class="note"><b>Sources.</b> PBS, <i>HIES 2024-25</i> report and microdata. PBS, <a href="https://www.pbs.gov.pk/node/1576">7th Population and Housing Census 2023 results</a>;
<a href="https://www.pbs.gov.pk/wp-content/uploads/2020/07/National-Census-Report-2023.pdf">National Census Report 2023</a> (households: 38.29 million in 2023, 31.92 million in 2017; household size);
<a href="https://www.pbs.gov.pk/sites/default/files/population/2023/material/pakistan_housing_data.pdf">Pakistan housing data</a> (lighting);
<a href="https://www.dawn.com/news/1768626">Dawn, 6 Aug 2023</a> (provincial populations, rural shares). Census figures were transcribed from these releases.
Calculations: <code>0_household_master/build_household_master.ipynb</code>, <code>reports/build_reports.py</code>.</p>
"""
to_pdf(page("Benchmarking HIES 2024-25 against the 2023 Census", "Benchmarking HIES 2024-25 against the 2023 Census", "Technical note", body2),
       "census.html", WORK / "0_household_master/HIES_vs_Census_2023.pdf")
