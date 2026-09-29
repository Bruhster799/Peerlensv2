"""Visual identity: an institutional research-desk look.

Palette
  ink navy   #0B1F3A  masthead, headings, primary text
  page       #F3F5F8  cool grey ground; white panels sit on it
  slate      #5B6B7F  secondary text
  rule       #D8DEE6  hairlines and table borders
  brass      #A8864F  the focal company, and nothing else
  signals    #2E7D5B positive, #B7862C watch, #A63D40 concern (muted, never neon)
Type
  Source Serif 4 for titles (the voice of a research note), IBM Plex Sans for everything else,
  with tabular figures so numbers line up in columns.
The memorable element is the comps table; everything around it stays quiet.
"""
import datetime as dt
import html

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&display=swap');

:root {
  --ink: #0B1F3A; --page: #F3F5F8; --panel: #FFFFFF; --slate: #5B6B7F; --rule: #D8DEE6;
  --soft: #EEF2F6; --brass: #A8864F; --brass-tint: #F6F0E4; --blue: #2F5C8F;
  --pos: #2E7D5B; --watch: #B7862C; --neg: #A63D40;
  --pos-tint: #E7F2EC; --watch-tint: #F8F0DC; --neg-tint: #F7E5E5;
}
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button, td, th {
  font-family: 'IBM Plex Sans', 'Segoe UI', Arial, sans-serif;
}
.stApp { background: var(--page); color: var(--ink); }
.block-container { padding-top: 0 !important; max-width: 1360px; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
.num { font-variant-numeric: tabular-nums; }

/* ---------- masthead ---------- */
.masthead { background: var(--ink); color: #fff; margin: 0 -4rem 0; padding: 1.1rem 4rem 1rem;
            display: flex; justify-content: space-between; align-items: flex-end; gap: 2rem; flex-wrap: wrap; }
.masthead .brand { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.65rem; font-weight: 600; letter-spacing: .01em; }
.masthead .desk { color: #A9B8CC; font-size: .92rem; margin-top: .15rem; }
.masthead .meta { text-align: right; color: #A9B8CC; font-size: .85rem; line-height: 1.5; }
.masthead .meta b { color: #fff; font-weight: 600; }
.status { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: .4rem; vertical-align: middle; }
.status.live { background: #5FB88A; } .status.demo { background: var(--brass); }

/* ---------- process line (a real sequence, so it is numbered) ---------- */
.process { display: flex; gap: 0; border-bottom: 1px solid var(--rule); margin: 0 0 1.6rem; background: var(--panel);
           margin-left: -4rem; margin-right: -4rem; padding: 0 4rem; }
.process .stage { padding: .8rem 1.4rem .7rem 0; margin-right: 1.4rem; color: #97A3B3; font-size: .9rem;
                  border-bottom: 2px solid transparent; }
.process .stage b { font-weight: 600; margin-right: .45rem; font-variant-numeric: tabular-nums; }
.process .stage.done { color: var(--slate); }
.process .stage.now { color: var(--ink); border-bottom-color: var(--ink); font-weight: 600; }

/* ---------- headings ---------- */
.h-section { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.55rem; font-weight: 600; color: var(--ink);
             margin: 1.4rem 0 .15rem; }
.h-sub { color: var(--slate); font-size: .95rem; margin-bottom: .9rem; max-width: 80ch; }
.h-minor { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 1.2rem 0 .5rem;
           padding-bottom: .35rem; border-bottom: 1px solid var(--rule); }

/* ---------- report header ---------- */
.report { background: var(--panel); border: 1px solid var(--rule); border-top: 3px solid var(--ink);
          padding: 1.2rem 1.4rem 1.1rem; margin-top: 1.2rem; }
.report .kicker { color: var(--slate); font-size: .88rem; }
.report .title { font-family: 'Source Serif 4', Georgia, serif; font-size: 2rem; font-weight: 600; line-height: 1.15; margin: .15rem 0 .35rem; }
.report .thesis { font-size: 1.02rem; color: var(--ink); max-width: 90ch; line-height: 1.55; }

/* ---------- metric strip ---------- */
.strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); background: var(--panel);
         border: 1px solid var(--rule); border-top: none; }
.cell { padding: .8rem 1.1rem; border-right: 1px solid var(--rule); }
.cell:last-child { border-right: none; }
.cell .label { color: var(--slate); font-size: .8rem; }
.cell .value { font-size: 1.55rem; font-weight: 600; font-variant-numeric: tabular-nums; line-height: 1.3; }
.cell .delta { font-size: .82rem; font-variant-numeric: tabular-nums; }
.delta.pos { color: var(--pos); } .delta.neg { color: var(--neg); } .delta.flat { color: var(--slate); }
.cell.score .value { color: var(--ink); }
.bar { height: 4px; background: var(--soft); margin-top: .45rem; }
.bar span { display: block; height: 4px; background: var(--ink); }

/* ---------- comps table ---------- */
.comps-wrap { overflow-x: auto; background: var(--panel); border: 1px solid var(--rule); }
table.comps { border-collapse: collapse; width: 100%; font-size: .85rem; font-variant-numeric: tabular-nums; }
table.comps th { text-align: right; font-weight: 600; color: var(--slate); font-size: .8rem; padding: .6rem .6rem;
                 border-bottom: 1px solid var(--ink); white-space: nowrap; background: var(--panel); }
table.comps th:first-child, table.comps td:first-child { text-align: left; }
table.comps td { text-align: right; padding: .5rem .6rem; border-bottom: 1px solid var(--rule); white-space: nowrap; }
table.comps tr.focal td { background: var(--brass-tint); font-weight: 600; }
table.comps tr.focal td:first-child { box-shadow: inset 3px 0 0 var(--brass); }
table.comps tr.median td { border-top: 1px solid var(--ink); border-bottom: none; color: var(--slate); font-style: italic; }
table.comps td.Green { color: var(--pos); } table.comps td.Red { color: var(--neg); }
table.comps td.Amber { color: var(--watch); }
table.comps .group { text-align: center; border-bottom: 1px solid var(--rule); color: var(--ink); font-size: .78rem; }

/* ---------- findings ---------- */
.finding { display: grid; grid-template-columns: 2.2rem 1fr; background: var(--panel); border: 1px solid var(--rule);
           border-left: 3px solid var(--slate); padding: .8rem 1rem; margin-bottom: .5rem; }
.finding.Red { border-left-color: var(--neg); } .finding.Amber { border-left-color: var(--watch); }
.finding.Green { border-left-color: var(--pos); }
.finding .idx { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.25rem; color: var(--slate); }
.finding .what { font-weight: 600; }
.finding .flag { font-size: .78rem; color: var(--slate); margin-left: .5rem; font-weight: 500; }
.finding .body { color: var(--ink); line-height: 1.5; margin-top: .15rem; }
.strengths { background: var(--panel); border: 1px solid var(--rule); padding: .8rem 1rem; line-height: 1.7; }
.strengths .item { color: var(--ink); } .strengths .item::before { content: "▲"; color: var(--pos); font-size: .7rem; margin-right: .5rem; }

/* ---------- widgets ---------- */
div[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid var(--rule); gap: 1.4rem; }
div[data-testid="stTabs"] button { font-weight: 500; color: var(--slate); padding-left: 0; padding-right: 0; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: var(--ink); font-weight: 600; }
div[data-baseweb="tab-highlight"] { background-color: var(--ink) !important; }
div[data-baseweb="tag"] { border-radius: 2px !important; background: var(--ink) !important; }
button[data-testid="stBaseButton-primary"] { border-radius: 2px; background: var(--ink); border: 1px solid var(--ink);
                                             font-weight: 600; padding: .55rem 1.3rem; }
button[data-testid="stBaseButton-primary"]:hover { background: #1B355C; border-color: #1B355C; }
button[data-testid="stBaseButton-secondary"] { border-radius: 2px; }
div[data-testid="stButtonGroup"] button { border-radius: 2px !important; font-size: .86rem; }
div[data-testid="stButtonGroup"] button[kind="pillsActive"], div[data-testid="stButtonGroup"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-pillsActive"] {
  background: var(--ink) !important; color: #fff !important; border-color: var(--ink) !important; }
div[data-testid="stButtonGroup"] button[kind="pillsActive"] *, div[data-testid="stButtonGroup"] button[aria-checked="true"] * { color: #fff !important; }
div[data-testid="stDownloadButton"] button { border-radius: 2px; font-weight: 600; }
section[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--rule); }
section[data-testid="stSidebar"] h3 { font-family: 'Source Serif 4', Georgia, serif; }
div[data-testid="stExpander"] details { border-radius: 2px; border-color: var(--rule); background: var(--panel); }
div[data-testid="stPlotlyChart"] { background: var(--panel); border: 1px solid var(--rule); padding: .4rem; }
.note-src { color: var(--slate); font-size: .8rem; margin-top: .35rem; }
:focus-visible { outline: 2px solid var(--blue) !important; outline-offset: 2px; }
@media (max-width: 800px) {
  .masthead, .process { margin-left: -1rem; margin-right: -1rem; padding-left: 1rem; padding-right: 1rem; }
  .masthead .meta { text-align: left; }
}
</style>
"""


def masthead(mode_is_live, source_label):
    status = "live" if mode_is_live else "demo"
    label = "Live market data" if mode_is_live else "Demo data (synthetic)"
    today = dt.date.today().strftime("%d %b %Y")
    return (f'<div class="masthead"><div><div class="brand">PeerLens</div>'
            f'<div class="desk">Peer comparables for the Nifty 500</div></div>'
            f'<div class="meta"><span class="status {status}"></span><b>{label}</b><br>'
            f'Universe: {html.escape(source_label)}. {today}</div></div>')


def process_line(current):
    stages = ["Universe", "Peer set", "Analysis", "Export"]
    parts = []
    for i, name in enumerate(stages, 1):
        state = "done" if i < current else "now" if i == current else ""
        parts.append(f'<div class="stage {state}"><b>{i}</b>{name}</div>')
    return '<div class="process">' + "".join(parts) + "</div>"
