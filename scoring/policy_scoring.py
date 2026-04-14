"""
Policy scoring system for multi-dimensional benefit-cost analysis.

Each proposal/position is scored across three policy dimensions:
  - Political  (benefit 0-100, cost 0-100)
  - Economic   (benefit 0-100, cost 0-100)
  - Social     (benefit 0-100, cost 0-100)

The objective function tries to maximize net benefits, with region-specific
weights. Agents can also factor in their opponent's score via an empathy
multiplier, and accumulate fatigue over rounds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PolicyDimension:
    """A single policy dimension with benefit and cost (each 0-100)."""
    benefit: float = 50.0
    cost: float = 50.0

    def __post_init__(self) -> None:
        self.benefit = _clamp100(self.benefit)
        self.cost = _clamp100(self.cost)

    @property
    def net(self) -> float:
        return self.benefit - self.cost


@dataclass
class PolicyScores:
    """Three-dimensional policy score for a single proposal/position."""
    political: PolicyDimension = field(default_factory=PolicyDimension)
    economic: PolicyDimension = field(default_factory=PolicyDimension)
    social: PolicyDimension = field(default_factory=PolicyDimension)

    @property
    def total_benefit(self) -> float:
        return self.political.benefit + self.economic.benefit + self.social.benefit

    @property
    def total_cost(self) -> float:
        return self.political.cost + self.economic.cost + self.social.cost

    @property
    def total_net(self) -> float:
        return self.total_benefit - self.total_cost

    def as_dict(self) -> Dict[str, Any]:
        return {
            "political": {"benefit": self.political.benefit, "cost": self.political.cost, "net": self.political.net},
            "economic": {"benefit": self.economic.benefit, "cost": self.economic.cost, "net": self.economic.net},
            "social": {"benefit": self.social.benefit, "cost": self.social.cost, "net": self.social.net},
            "total_benefit": self.total_benefit,
            "total_cost": self.total_cost,
            "total_net": self.total_net,
        }


@dataclass
class RegionWeights:
    """Region-specific weights for the objective function (sum to 1.0)."""
    political: float = 0.33
    economic: float = 0.34
    social: float = 0.33

    def __post_init__(self) -> None:
        total = self.political + self.economic + self.social
        if total > 0:
            self.political /= total
            self.economic /= total
            self.social /= total


# Pre-defined regional weight profiles
REGION_WEIGHTS: Dict[str, RegionWeights] = {
    "default": RegionWeights(0.33, 0.34, 0.33),
    "authoritarian": RegionWeights(0.50, 0.30, 0.20),
    "democratic": RegionWeights(0.25, 0.30, 0.45),
    "developing": RegionWeights(0.20, 0.50, 0.30),
    "conflict_zone": RegionWeights(0.45, 0.25, 0.30),
}


@dataclass
class AgentScorecard:
    """Accumulated scores for an agent across the entire debate."""
    agent_name: str
    rounds_played: int = 0
    cumulative_scores: PolicyScores = field(default_factory=PolicyScores)
    round_scores: List[PolicyScores] = field(default_factory=list)
    objective_values: List[float] = field(default_factory=list)
    fatigue: float = 0.0
    empathy_bonus: float = 0.0
    penalties: float = 0.0

    @property
    def final_objective(self) -> float:
        if not self.objective_values:
            return 0.0
        return sum(self.objective_values)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "rounds_played": self.rounds_played,
            "cumulative_scores": self.cumulative_scores.as_dict(),
            "final_objective": round(self.final_objective, 2),
            "fatigue": round(self.fatigue, 4),
            "empathy_bonus": round(self.empathy_bonus, 2),
            "penalties": round(self.penalties, 2),
            "round_history": [s.as_dict() for s in self.round_scores],
        }


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

# Topic -> base scores mapping. Real implementation would use LLM analysis;
# this provides deterministic baselines for the built-in topics.
TOPIC_BASE_SCORES: Dict[str, Dict[str, Tuple[float, float]]] = {
    "territorial_disputes": {
        "political": (70, 55),
        "economic": (40, 60),
        "social": (30, 65),
    },
    "race_relations": {
        "political": (50, 40),
        "economic": (35, 30),
        "social": (75, 50),
    },
    "economic_policy": {
        "political": (45, 35),
        "economic": (80, 50),
        "social": (55, 40),
    },
    "partition_of_india": {
        "political": (65, 60),
        "economic": (40, 55),
        "social": (35, 70),
    },
    "war": {
        "political": (75, 65),
        "economic": (30, 80),
        "social": (20, 85),
    },
    "immigration": {
        "political": (55, 50),
        "economic": (60, 45),
        "social": (65, 55),
    },
    "socialism": {
        "political": (50, 45),
        "economic": (55, 60),
        "social": (70, 40),
    },
}


def score_proposal(
    topic: str,
    agent_ideology: str,
    personality_modifier: float = 0.0,
    cooperation_level: float = 0.5,
) -> PolicyScores:
    """
    Score a proposal/position on the three policy dimensions.

    Parameters
    ----------
    topic : str
        The debate topic.
    agent_ideology : str
        The agent's ideology (affects scoring bias).
    personality_modifier : float
        A modifier from -0.3 to +0.3 based on personality traits.
    cooperation_level : float
        0-1 how cooperative the agent is being (higher = lower costs).

    Returns
    -------
    PolicyScores
    """
    base = TOPIC_BASE_SCORES.get(topic, {
        "political": (50, 50),
        "economic": (50, 50),
        "social": (50, 50),
    })

    # Ideology-based adjustments
    ideology_shifts = _ideology_shifts(agent_ideology)

    dims = {}
    for dim_name in ("political", "economic", "social"):
        b, c = base[dim_name]
        shift = ideology_shifts.get(dim_name, (0, 0))
        benefit = b + shift[0] + personality_modifier * 30
        cost = c + shift[1] - cooperation_level * 25
        dims[dim_name] = PolicyDimension(benefit=benefit, cost=cost)

    return PolicyScores(
        political=dims["political"],
        economic=dims["economic"],
        social=dims["social"],
    )


def compute_objective(
    scores: PolicyScores,
    weights: Optional[RegionWeights] = None,
    fatigue: float = 0.0,
    penalty: float = 0.0,
) -> float:
    """
    Compute the objective function value for a set of policy scores.

    objective = sum(weight_i * net_i) * (1 - fatigue) - penalty

    Parameters
    ----------
    scores : PolicyScores
    weights : RegionWeights, optional
        Region-specific dimension weights.
    fatigue : float
        Fatigue factor 0-1 (reduces objective).
    penalty : float
        Negative reinforcement penalty.
    """
    w = weights or REGION_WEIGHTS["default"]
    raw = (
        w.political * scores.political.net
        + w.economic * scores.economic.net
        + w.social * scores.social.net
    )
    return raw * (1.0 - min(fatigue, 0.95)) - penalty


def apply_empathy_multiplier(
    own_objective: float,
    opponent_objective: float,
    empathy_ratio: float,
) -> float:
    """
    Blend the agent's own objective with the opponent's objective.

    result = own * (1 - empathy_ratio) + opponent * empathy_ratio

    empathy_ratio 0.0 = purely self-interested
    empathy_ratio 0.5 = equal weight to self and opponent
    empathy_ratio 1.0 = fully altruistic
    """
    empathy_ratio = max(0.0, min(1.0, empathy_ratio))
    return own_objective * (1.0 - empathy_ratio) + opponent_objective * empathy_ratio


def apply_fatigue_penalty(
    base_fatigue: float,
    round_number: int,
    emotional_stability: float = 0.5,
    max_rounds: int = 20,
) -> float:
    """
    Calculate fatigue that accumulates over rounds.

    Agents with lower emotional stability fatigue faster.
    Uses a sigmoid curve so fatigue accelerates in later rounds.
    """
    progress = round_number / max(max_rounds, 1)
    stability_factor = 1.0 - emotional_stability * 0.6
    fatigue = base_fatigue + (1.0 / (1.0 + math.exp(-8 * (progress - 0.6)))) * stability_factor * 0.4
    return min(fatigue, 0.95)


def compute_penalty(
    violated_red_lines: int = 0,
    low_cooperation_rounds: int = 0,
    repeated_positions: int = 0,
) -> float:
    """
    Compute negative reinforcement penalty.

    Penalizes agents for:
    - Violating red lines of opponents (blocks negotiation)
    - Low cooperation streaks
    - Repetitive/stale positions
    """
    return (
        violated_red_lines * 15.0
        + low_cooperation_rounds * 5.0
        + repeated_positions * 3.0
    )


# ---------------------------------------------------------------------------
# OCEAN personality -> empathy mapping
# ---------------------------------------------------------------------------

@dataclass
class OCEANTraits:
    """Big Five (OCEAN) personality traits, each 0-1."""
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

    def empathy_score(self) -> float:
        """Derive an empathy score from OCEAN traits.

        Higher agreeableness and openness increase empathy.
        Lower conscientiousness and higher neuroticism decrease it slightly.
        """
        score = (
            self.agreeableness * 0.45
            + self.openness * 0.25
            + self.extraversion * 0.15
            + (1.0 - self.neuroticism) * 0.10
            + self.conscientiousness * 0.05
        )
        return max(0.0, min(1.0, score))

    def personality_modifier(self) -> float:
        """Map OCEAN to a modifier for scoring.

        Range is roughly -0.6..+0.6, large enough to create visible
        differences between cooperative and adversarial personalities.
        """
        return (
            (self.agreeableness - 0.5) * 0.6
            + (self.openness - 0.5) * 0.3
            + (self.conscientiousness - 0.5) * 0.15
            - (self.neuroticism - 0.5) * 0.15
        )

    def as_dict(self) -> Dict[str, float]:
        return {
            "openness": round(self.openness, 2),
            "conscientiousness": round(self.conscientiousness, 2),
            "extraversion": round(self.extraversion, 2),
            "agreeableness": round(self.agreeableness, 2),
            "neuroticism": round(self.neuroticism, 2),
            "empathy_score": round(self.empathy_score(), 3),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clamp100(v: float) -> float:
    return max(0.0, min(100.0, v))


def _ideology_shifts(ideology: str) -> Dict[str, Tuple[float, float]]:
    """Return (benefit_shift, cost_shift) per dimension for an ideology.

    Shifts are large enough to produce visibly distinct scores across agents
    with different ideologies. Positive benefit shifts increase perceived
    benefit; positive cost shifts increase perceived cost.
    """
    shifts: Dict[str, Dict[str, Tuple[float, float]]] = {
        "fascism":             {"political": (30, -15), "economic": (5, 20),  "social": (-35, 35)},
        "nonviolence":         {"political": (-15, -30), "economic": (-5, -20), "social": (35, -35)},
        "muslim_nationalism":  {"political": (20, 10),  "economic": (10, -5),  "social": (10, 15)},
        "communism":           {"political": (10, 20),  "economic": (20, 25),  "social": (25, 5)},
        "democracy":           {"political": (15, -15), "economic": (5, -5),   "social": (25, -20)},
        "capitalism":          {"political": (-5, 10),  "economic": (35, 15),  "social": (-15, 20)},
        "authoritarianism":    {"political": (35, -10), "economic": (5, 15),   "social": (-30, 30)},
        "liberalism":          {"political": (10, -10), "economic": (15, 5),   "social": (25, -20)},
        "conservatism":        {"political": (20, -5),  "economic": (15, 10),  "social": (-5, 10)},
    }
    return shifts.get(ideology.lower(), {"political": (0, 0), "economic": (0, 0), "social": (0, 0)})
