"""
Goal 3 (Validation) — Judge/Mediator agent.

Quantifies both agents' performance across policy dimensions,
tracks empathy effectiveness, and produces a structured evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base_agent import HistoricalAgent
from scoring.policy_scoring import (
    AgentScorecard,
    PolicyScores,
    compute_objective,
    RegionWeights,
    REGION_WEIGHTS,
)


@dataclass
class JudgeVerdict:
    """Structured output from the Judge's evaluation."""
    winner: Optional[str]
    margin: float
    scorecards: Dict[str, Dict[str, Any]]
    empathy_analysis: Dict[str, Any]
    convergence_round: Optional[int]
    convergence_metric: float
    policy_breakdown: Dict[str, Dict[str, Any]]
    recommendations: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "winner": self.winner,
            "margin": round(self.margin, 2),
            "scorecards": self.scorecards,
            "empathy_analysis": self.empathy_analysis,
            "convergence_round": self.convergence_round,
            "convergence_metric": round(self.convergence_metric, 3),
            "policy_breakdown": self.policy_breakdown,
            "recommendations": self.recommendations,
        }


class JudgeAgent:
    """
    Non-participating agent that evaluates a completed debate.

    Responsibilities:
    - Score each agent's cumulative performance
    - Identify the convergence point (if any)
    - Measure empathy effectiveness
    - Produce a structured verdict
    """

    def __init__(self, region_weights: Optional[RegionWeights] = None):
        self.region_weights = region_weights or REGION_WEIGHTS["default"]

    def evaluate(
        self,
        agents: List[HistoricalAgent],
        rounds: List[Dict[str, Any]],
        topic: str,
    ) -> JudgeVerdict:
        """Evaluate a completed debate and return a verdict."""
        scorecards = {a.name: a.scorecard.as_dict() for a in agents}

        # Determine winner by final objective
        best_agent = max(agents, key=lambda a: a.scorecard.final_objective)
        worst_agent = min(agents, key=lambda a: a.scorecard.final_objective)
        margin = best_agent.scorecard.final_objective - worst_agent.scorecard.final_objective

        winner = best_agent.name if margin > 1.0 else None

        # Empathy analysis
        empathy_analysis = {}
        for a in agents:
            empathy_analysis[a.name] = {
                "empathy_ratio": round(a.empathy_ratio, 3),
                "empathy_bonus": round(a.scorecard.empathy_bonus, 2),
                "ocean": a.ocean.as_dict(),
                "fatigue_final": round(a.fatigue, 4),
                "penalties": round(a.scorecard.penalties, 2),
            }

        # Convergence detection: find first round where agents' objectives
        # are within 10% of each other
        convergence_round = None
        convergence_metric = 0.0
        if len(agents) == 2:
            a1, a2 = agents
            for i in range(min(len(a1.scorecard.objective_values), len(a2.scorecard.objective_values))):
                v1 = a1.scorecard.objective_values[i]
                v2 = a2.scorecard.objective_values[i]
                diff = abs(v1 - v2)
                avg = (abs(v1) + abs(v2)) / 2 if (abs(v1) + abs(v2)) > 0 else 1.0
                relative_diff = diff / avg if avg > 0 else 0
                if relative_diff < 0.1:
                    convergence_round = i + 1
                    convergence_metric = 1.0 - relative_diff
                    break
            if convergence_round is None and a1.scorecard.objective_values and a2.scorecard.objective_values:
                v1 = a1.scorecard.objective_values[-1]
                v2 = a2.scorecard.objective_values[-1]
                avg = (abs(v1) + abs(v2)) / 2 if (abs(v1) + abs(v2)) > 0 else 1.0
                convergence_metric = max(0, 1.0 - abs(v1 - v2) / avg) if avg > 0 else 0

        # Policy breakdown per agent
        policy_breakdown = {}
        for a in agents:
            cs = a.scorecard.cumulative_scores
            policy_breakdown[a.name] = {
                "political": {"benefit": round(cs.political.benefit, 1), "cost": round(cs.political.cost, 1), "net": round(cs.political.net, 1)},
                "economic": {"benefit": round(cs.economic.benefit, 1), "cost": round(cs.economic.cost, 1), "net": round(cs.economic.net, 1)},
                "social": {"benefit": round(cs.social.benefit, 1), "cost": round(cs.social.cost, 1), "net": round(cs.social.net, 1)},
            }

        # Recommendations
        recommendations = self._generate_recommendations(agents, convergence_round, topic)

        return JudgeVerdict(
            winner=winner,
            margin=margin,
            scorecards=scorecards,
            empathy_analysis=empathy_analysis,
            convergence_round=convergence_round,
            convergence_metric=convergence_metric,
            policy_breakdown=policy_breakdown,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        agents: List[HistoricalAgent],
        convergence_round: Optional[int],
        topic: str,
    ) -> List[str]:
        recs: List[str] = []

        # Check if empathy helped
        high_empathy = [a for a in agents if a.empathy_ratio > 0.4]
        low_empathy = [a for a in agents if a.empathy_ratio <= 0.4]

        if high_empathy and low_empathy:
            he_avg = sum(a.scorecard.final_objective for a in high_empathy) / len(high_empathy)
            le_avg = sum(a.scorecard.final_objective for a in low_empathy) / len(low_empathy)
            if he_avg > le_avg:
                recs.append(
                    f"Higher empathy agents averaged {he_avg:.1f} vs {le_avg:.1f} — "
                    f"empathy correlated with better outcomes on '{topic}'."
                )
            else:
                recs.append(
                    f"Lower empathy agents performed better ({le_avg:.1f} vs {he_avg:.1f}) — "
                    f"pure rationality may be more effective on '{topic}'."
                )

        if convergence_round:
            recs.append(f"Agents converged at round {convergence_round}. Earlier convergence suggests productive dialogue.")
        else:
            recs.append("No convergence detected. Consider increasing empathy or adjusting topic framing.")

        for a in agents:
            if a.fatigue > 0.5:
                recs.append(f"{a.name} showed high fatigue ({a.fatigue:.2f}). Consider shorter debates or higher emotional stability.")
            if a.scorecard.penalties > 20:
                recs.append(f"{a.name} accumulated {a.scorecard.penalties:.0f} penalty points. Review red-line violations and cooperation.")

        return recs
