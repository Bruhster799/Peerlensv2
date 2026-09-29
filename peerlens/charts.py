"""All Plotly figures, styled as research-desk exhibits: white panels, hairline grids, navy and slate
for the peer set, brass reserved for the focal company, muted signal colours."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

INK = "#0B1F3A"
SLATE = "#5B6B7F"
RULE = "#E3E8EE"
BRASS = "#A8864F"
PAPER = "#FFFFFF"
FONT = "'IBM Plex Sans', 'Segoe UI', Arial, sans-serif"
PEER_PALETTE = ["#0B1F3A", "#6E9BC9", "#3D6A99", "#8A9BB0", "#1F4E79", "#A9B8C9", "#5B6B7F", "#C3CDD8"]
SIGNAL = {"Green": "#2E7D5B", "Amber": "#B7862C", "Red": "#A63D40"}
SIGNAL_TINT = {"Green": "#DCEFE4", "Amber": "#F6EACB", "Red": "#F3DADA", "n/a": "#EEF1F5"}


def company_colors(companies, focal):
    colors, others = {}, iter(PEER_PALETTE * 3)
    for company in companies:
        colors[company] = BRASS if company == focal else next(others)
    return colors


def _style(fig, height=420, legend=True):
    fig.update_layout(
        height=height, paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=dict(family=FONT, color=INK, size=12),
        margin=dict(l=10, r=16, t=36, b=10), showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11, color=SLATE), title_text=""),
        hoverlabel=dict(bgcolor=PAPER, bordercolor=INK, font=dict(family=FONT, color=INK, size=12)),
    )
    fig.update_xaxes(gridcolor=RULE, zerolinecolor="#C9D1DB", linecolor="#C9D1DB", ticks="outside",
                     tickcolor="#C9D1DB", tickfont=dict(color=SLATE))
    fig.update_yaxes(gridcolor=RULE, zerolinecolor="#C9D1DB", linecolor="#C9D1DB", tickfont=dict(color=SLATE))
    return fig


def exhibit_title(fig, text):
    fig.update_layout(title=dict(text=text, x=0.01, xanchor="left", y=0.985, yanchor="top", yref="container",
                                 font=dict(size=13, color=INK, family=FONT)))
    fig.update_layout(margin=dict(t=max(fig.layout.margin.t or 0, 82)))
    return fig


# ---------------------------------------------------------------- market maps
def universe_map(universe, selected_industry=None):
    """Treemap of the Nifty 500: one tile per industry, sized by number of constituents."""
    counts = universe.groupby("industry").size().sort_values(ascending=False)
    colors = [INK if i == selected_industry else ("#DCE3EB" if selected_industry else "#3D6A99")
              for i in counts.index]
    text_colors = ["white" if (i == selected_industry or not selected_industry) else SLATE for i in counts.index]
    fig = go.Figure(go.Treemap(
        labels=list(counts.index), parents=[""] * len(counts), values=list(counts.values),
        marker=dict(colors=colors, line=dict(color="white", width=2)), tiling=dict(pad=0),
        pathbar=dict(visible=False),
        texttemplate="<b>%{label}</b><br>%{value} cos", textfont=dict(family=FONT, color=text_colors, size=12),
        hovertemplate="<b>%{label}</b><br>%{value} constituents<extra></extra>"))
    return _style(fig, height=430, legend=False).update_layout(margin=dict(l=0, r=0, t=0, b=0))


def industry_map(members, peers, focal):
    """Treemap of one industry, tiles sized by market cap. Focal in brass, peers in navy, the rest grey."""
    data = members.copy()
    fill = data["market_cap"].median() if data["market_cap"].notna().any() else 1.0
    data["size"] = data["market_cap"].fillna(fill)
    colors = [BRASS if c == focal else INK if c in peers else "#DCE3EB" for c in data.company]
    fonts = ["white" if (c == focal or c in peers) else SLATE for c in data.company]
    caps = data["market_cap"].map(lambda v: f"₹{v:,.0f} cr" if pd.notna(v) else "n/a")
    fig = go.Figure(go.Treemap(
        labels=data.company, parents=[""] * len(data), values=data["size"], customdata=caps,
        marker=dict(colors=colors, line=dict(color="white", width=2)), tiling=dict(pad=0),
        pathbar=dict(visible=False),
        texttemplate="<b>%{label}</b><br>%{customdata}", textfont=dict(family=FONT, color=fonts, size=12),
        hovertemplate="<b>%{label}</b><br>Market cap %{customdata}<extra></extra>"))
    return _style(fig, height=460, legend=False).update_layout(margin=dict(l=0, r=0, t=0, b=0))


# ---------------------------------------------------------------- positioning (animated)
def peer_map(ratio_values, clean, focal, x_key="net_debt_to_ebitda", y_key="roce"):
    frame = ratio_values.merge(clean[["symbol", "year", "revenue"]], on=["symbol", "year"])
    frame = frame.dropna(subset=[x_key, y_key, "revenue"]).sort_values(["year", "company"])
    if frame.empty:
        return None
    frame["revenue"] = frame["revenue"].clip(lower=1)
    colors = company_colors(sorted(frame.company.unique()), focal)
    pad_x = (frame[x_key].max() - frame[x_key].min()) * 0.15 + 0.2
    pad_y = (frame[y_key].max() - frame[y_key].min()) * 0.15 + 0.02
    fig = px.scatter(
        frame, x=x_key, y=y_key, size="revenue", color="company", animation_frame="year",
        animation_group="company", color_discrete_map=colors, size_max=58, hover_name="company",
        range_x=[frame[x_key].min() - pad_x, frame[x_key].max() + pad_x],
        range_y=[frame[y_key].min() - pad_y, frame[y_key].max() + pad_y],
        labels={x_key: "Net debt / EBITDA (x)", y_key: "ROCE", "revenue": "Revenue (₹ cr)"})
    fig.update_traces(marker=dict(line=dict(width=1, color="white"), opacity=0.9))
    fig.update_yaxes(tickformat=".0%")
    fig.add_vline(x=1.5, line=dict(color="#9AA7B8", dash="dot", width=1))
    fig.add_hline(y=0.15, line=dict(color="#9AA7B8", dash="dot", width=1))
    fig.add_annotation(xref="paper", yref="paper", x=0.01, y=0.99, showarrow=False, xanchor="left",
                       text="Higher return, lower leverage", font=dict(color=SLATE, size=11))
    fig.add_annotation(xref="paper", yref="paper", x=0.99, y=0.01, showarrow=False, xanchor="right",
                       text="Lower return, higher leverage", font=dict(color=SLATE, size=11))
    if fig.layout.sliders:
        fig.layout.sliders[0].currentvalue.prefix = ""
        fig.layout.sliders[0].pad = dict(t=50, r=40)
        fig.layout.sliders[0].currentvalue.font = dict(color=INK, size=13)
    if fig.layout.updatemenus:
        play = fig.layout.updatemenus[0].buttons[0].args[1]
        play["frame"]["duration"] = 900
        play["transition"]["duration"] = 600
        play["transition"]["easing"] = "cubic-in-out"
    fig = _style(fig, height=540)
    return exhibit_title(fig, "Return on capital against leverage (bubble size = revenue)")


# ---------------------------------------------------------------- scorecard
def rag_heatmap(ratio_values, rag, ratios, year, focal=None):
    snapshot = ratio_values[ratio_values.year == year].set_index("company").sort_index()
    status = rag[rag.year == year].set_index("company").sort_index()
    codes = {"Red": 0, "Amber": 1, "Green": 2, "n/a": 3}
    z = [[codes[status.loc[c, r.key]] for r in ratios] for c in snapshot.index]
    text = [[r.format(snapshot.loc[c, r.key]) for r in ratios] for c in snapshot.index]
    scale = [[0, SIGNAL_TINT["Red"]], [0.25, SIGNAL_TINT["Red"]], [0.25, SIGNAL_TINT["Amber"]],
             [0.5, SIGNAL_TINT["Amber"]], [0.5, SIGNAL_TINT["Green"]], [0.75, SIGNAL_TINT["Green"]],
             [0.75, SIGNAL_TINT["n/a"]], [1, SIGNAL_TINT["n/a"]]]
    labels = [f"<b>{c}</b>" if c == focal else c for c in snapshot.index]
    fig = go.Figure(go.Heatmap(
        z=z, x=[r.short for r in ratios], y=labels, text=text, texttemplate="%{text}",
        textfont=dict(family=FONT, size=12, color=INK), colorscale=scale, zmin=0, zmax=3, showscale=False,
        xgap=2, ygap=2, hovertemplate="%{y}<br>%{x}: %{text}<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False, ticks="")
    fig.update_xaxes(side="top", showgrid=False, ticks="", tickfont=dict(color=INK))
    fig = _style(fig, height=110 + 46 * len(snapshot), legend=False)
    return fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))


def health_ranking(health, year, focal):
    snapshot = health[health.year == year].sort_values("health_score")
    colors = [BRASS if c == focal else "#8A9BB0" for c in snapshot.company]
    fig = go.Figure(go.Bar(
        x=snapshot.health_score, y=snapshot.company, orientation="h", marker=dict(color=colors),
        text=snapshot.health_score.map(lambda v: f"{v:.0f}"), textposition="outside",
        textfont=dict(color=INK), width=0.55, hovertemplate="%{y}: %{x:.0f}/100<extra></extra>"))
    fig.update_xaxes(range=[0, 108], title=None)
    fig = _style(fig, height=90 + 40 * len(snapshot), legend=False)
    return exhibit_title(fig, "Composite health score (0 = every ratio red, 100 = every ratio green)")


# ---------------------------------------------------------------- profile
def peer_radar(percentiles, ratios, focal):
    labels = [r.short for r in ratios]
    fig = go.Figure()
    colors = company_colors(list(percentiles.index), focal)
    fig.add_trace(go.Scatterpolar(r=[50] * (len(labels) + 1), theta=labels + labels[:1], name="Peer median",
                                  line=dict(color="#9AA7B8", dash="dot", width=1), hoverinfo="skip"))
    for company in percentiles.index:
        values = [percentiles.loc[company, r.key] for r in ratios]
        values = [v if pd.notna(v) else 0 for v in values]
        is_focal = company == focal
        fig.add_trace(go.Scatterpolar(
            r=values + values[:1], theta=labels + labels[:1], name=company,
            fill="toself" if is_focal else None, fillcolor="rgba(168,134,79,0.18)" if is_focal else None,
            line=dict(color=colors[company], width=2.4 if is_focal else 1.2),
            visible=True if is_focal else "legendonly"))
    fig.update_layout(polar=dict(bgcolor=PAPER,
                                 radialaxis=dict(range=[0, 100], gridcolor=RULE, linecolor=RULE,
                                                 tickfont=dict(size=9, color=SLATE)),
                                 angularaxis=dict(gridcolor=RULE, linecolor="#C9D1DB",
                                                  tickfont=dict(size=11, color=INK))))
    fig = _style(fig, height=540)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.06, x=0.5, xanchor="center"),
                      margin=dict(l=50, r=50, t=50, b=40))
    return exhibit_title(fig, "Percentile rank within the peer set on each ratio (100 = best)")


# ---------------------------------------------------------------- trends
def ratio_trend(ratio_values, ratio, focal):
    frame = ratio_values.dropna(subset=[ratio.key]).sort_values("year")
    colors = company_colors(sorted(frame.company.unique()), focal)
    fig = go.Figure()
    values = frame[ratio.key]
    if len(values):
        low, high = min(values.min(), ratio.amber) * 0.9, max(values.max(), ratio.green) * 1.1
        if ratio.higher_is_better:
            bands = [(ratio.green, high, "rgba(46,125,91,0.05)"), (low, ratio.amber, "rgba(166,61,64,0.05)")]
        else:
            bands = [(low, ratio.green, "rgba(46,125,91,0.05)"), (ratio.amber, high, "rgba(166,61,64,0.05)")]
        for y0, y1, color in bands:
            fig.add_hrect(y0=y0, y1=y1, fillcolor=color, line_width=0, layer="below")
        for level in (ratio.green, ratio.amber):
            fig.add_hline(y=level, line=dict(color="#C9D1DB", dash="dot", width=1))
    for company, group in frame.groupby("company"):
        is_focal = company == focal
        fig.add_trace(go.Scatter(
            x=group.year, y=group[ratio.key], name=company, mode="lines+markers",
            line=dict(color=colors[company], width=3 if is_focal else 1.4),
            marker=dict(size=8 if is_focal else 5, symbol="square" if is_focal else "circle"),
            hovertemplate=f"{company}<br>%{{x}}: %{{y}}<extra></extra>"))
    if ratio.unit == "%":
        fig.update_yaxes(tickformat=".0%")
    fig = _style(fig, height=460)
    return exhibit_title(fig, f"{ratio.name} by financial year (dotted lines = green and amber thresholds)")


def price_performance(prices, names, focal):
    colors = company_colors(sorted(names.values()), focal)
    fig = go.Figure()
    for symbol in prices.columns:
        name = names.get(symbol, symbol)
        is_focal = name == focal
        fig.add_trace(go.Scatter(x=prices.index, y=prices[symbol], name=name, mode="lines",
                                 line=dict(color=colors.get(name, SLATE), width=2.6 if is_focal else 1.2),
                                 hovertemplate=f"{name}<br>%{{x|%d %b %Y}}: %{{y:.1f}}<extra></extra>"))
    fig.add_hline(y=100, line=dict(color="#9AA7B8", dash="dot", width=1))
    fig = _style(fig, height=460)
    return exhibit_title(fig, "Total return, rebased to 100 twelve months ago")
