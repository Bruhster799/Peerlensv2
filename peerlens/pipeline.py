"""Runs the whole analysis: validate → clean → ratios → ratings → scores → recommendations."""
from dataclasses import dataclass, field

import pandas as pd

from .ratios import (RATIOS, RatioEngine, build_recommendations, latest_common_year, strengths)
from .validator import FinancialDataValidator


@dataclass
class PeerAnalysis:
    raw: pd.DataFrame
    clean: pd.DataFrame
    issues_before: pd.DataFrame
    issues_after: pd.DataFrame
    fixes: pd.DataFrame
    ratio_values: pd.DataFrame
    rag: pd.DataFrame
    health: pd.DataFrame
    trends: pd.DataFrame
    ratios: list
    year: str
    focal: str
    recommendations: list = field(default_factory=list)
    strengths: list = field(default_factory=list)
    rank: int = 0
    summary_line: str = ""


def run_analysis(raw, focal, mode):
    validator = FinancialDataValidator(mode=mode)
    issues_before = validator.validate(raw)
    clean, fixes = validator.clean(raw)
    issues_after = validator.validate(clean)

    engine = RatioEngine(RATIOS)
    ratio_values = engine.compute_all(clean)
    ratios = engine.available(ratio_values)
    engine = RatioEngine(ratios)                   # drop ratios this industry cannot support
    rag = engine.rag_table(ratio_values)
    health = engine.health_scores(rag)
    trends = engine.trend_flags(ratio_values)
    year = latest_common_year(ratio_values)

    ranking = (health[health.year == year].sort_values("health_score", ascending=False)
               .reset_index(drop=True))
    rank = int(ranking.index[ranking.company == focal][0]) + 1 if focal in set(ranking.company) else 0
    score = ranking.loc[ranking.company == focal, "health_score"]
    score_text = f"{score.iloc[0]:.0f}/100" if len(score) else "n/a"
    summary = (f"{focal} ranks #{rank} of {len(ranking)} peers in {year} with a health score of {score_text}."
               if rank else f"{focal} has no {year} data.")

    return PeerAnalysis(
        raw=raw, clean=clean, issues_before=issues_before, issues_after=issues_after, fixes=fixes,
        ratio_values=ratio_values, rag=rag, health=health, trends=trends, ratios=ratios, year=year,
        focal=focal,
        recommendations=build_recommendations(focal, year, ratio_values, rag, trends, ratios),
        strengths=strengths(focal, year, ratio_values, ratios), rank=rank, summary_line=summary)
