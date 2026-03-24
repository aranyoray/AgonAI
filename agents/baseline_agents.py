"""
Goal 1 (Baseline) agents: no personality, just cognition.

RationalAgent  - purely logical, maximizes own objective
EmpatheticAgent - factors opponent well-being into decisions
"""

from typing import Any, Dict, List, Optional

from .base_agent import (
    HistoricalAgent,
    HistoricalContext,
    Ideology,
    PersonalityTraits,
)
from scoring.policy_scoring import OCEANTraits, RegionWeights


# ---------------------------------------------------------------------------
# Shared "blank-slate" context
# ---------------------------------------------------------------------------

_NEUTRAL_CONTEXT = HistoricalContext(
    time_period="contemporary",
    major_events=[],
    cultural_background="neutral",
    education="",
    key_relationships=[],
    defining_moments=[],
)


class RationalAgent(HistoricalAgent):
    """Purely rational negotiator — zero empathy, maximizes own objective."""

    def __init__(
        self,
        name: str = "Rational Agent",
        ideology: Ideology = Ideology.DEMOCRACY,
        llm_client: Any = None,
        memory_client: Any = None,
        region_weights: Optional[RegionWeights] = None,
    ):
        personality = PersonalityTraits(
            assertiveness=0.7,
            cooperativeness=0.3,
            openness_to_change=0.5,
            emotional_stability=0.9,
            dominance=0.6,
            charisma=0.4,
            pragmatism=0.95,
            idealism=0.2,
        )
        ocean = OCEANTraits(
            openness=0.5,
            conscientiousness=0.8,
            extraversion=0.4,
            agreeableness=0.2,  # low empathy
            neuroticism=0.1,
        )
        super().__init__(
            name=name,
            ideology=ideology,
            personality=personality,
            context=_NEUTRAL_CONTEXT,
            llm_client=llm_client,
            memory_client=memory_client,
            ocean_override=ocean,
            empathy_ratio=0.0,
            region_weights=region_weights,
        )
        self.red_lines = []

    def generate_response(
        self,
        topic: str,
        other_agents: List[HistoricalAgent],
        debate_context: Dict[str, Any],
    ) -> str:
        llm = self.generate_llm_response(topic, debate_context)
        if llm:
            return llm

        opponents = ", ".join(a.name for a in other_agents)
        return (
            f"From a rational standpoint, {opponents}, on the topic of {topic}: "
            f"I propose we evaluate the costs and benefits objectively. "
            f"My analysis indicates we should maximize net benefit across political, "
            f"economic, and social dimensions. I am willing to concede points where "
            f"the marginal cost exceeds the marginal benefit, but I will hold firm "
            f"on positions where my net gain is positive."
            + self.compromise_note()
        )

    def evaluate_proposal(
        self, proposal: str, proposer: HistoricalAgent
    ) -> Dict[str, Any]:
        return self.evaluate_proposal_generically(proposal, proposer)


class EmpatheticAgent(HistoricalAgent):
    """Empathetic negotiator — factors opponent well-being heavily."""

    def __init__(
        self,
        name: str = "Empathetic Agent",
        ideology: Ideology = Ideology.DEMOCRACY,
        empathy_ratio: float = 0.6,
        llm_client: Any = None,
        memory_client: Any = None,
        region_weights: Optional[RegionWeights] = None,
    ):
        personality = PersonalityTraits(
            assertiveness=0.4,
            cooperativeness=0.9,
            openness_to_change=0.8,
            emotional_stability=0.7,
            dominance=0.2,
            charisma=0.7,
            pragmatism=0.5,
            idealism=0.8,
        )
        ocean = OCEANTraits(
            openness=0.8,
            conscientiousness=0.5,
            extraversion=0.6,
            agreeableness=0.85,  # high empathy
            neuroticism=0.3,
        )
        super().__init__(
            name=name,
            ideology=ideology,
            personality=personality,
            context=_NEUTRAL_CONTEXT,
            llm_client=llm_client,
            memory_client=memory_client,
            ocean_override=ocean,
            empathy_ratio=empathy_ratio,
            region_weights=region_weights,
        )
        self.red_lines = []

    def generate_response(
        self,
        topic: str,
        other_agents: List[HistoricalAgent],
        debate_context: Dict[str, Any],
    ) -> str:
        llm = self.generate_llm_response(topic, debate_context)
        if llm:
            return llm

        opponents = ", ".join(a.name for a in other_agents)
        return (
            f"I hear your concerns, {opponents}. On {topic}, "
            f"I believe we can find a solution that works for all of us. "
            f"I am genuinely interested in understanding your priorities — "
            f"what matters most to you politically, economically, and socially? "
            f"I am willing to make significant concessions if it means we both "
            f"come away better off. Let me propose a framework where we each "
            f"share our top three needs and work from there."
            + self.compromise_note()
        )

    def evaluate_proposal(
        self, proposal: str, proposer: HistoricalAgent
    ) -> Dict[str, Any]:
        # Empathetic agent is more accepting
        result = self.evaluate_proposal_generically(proposal, proposer)
        if not result["accept"]:
            # Re-evaluate with a more generous lens
            score = self.calculate_consensus_score(proposer)
            if score >= 0.25:
                result["accept"] = True
                result["reasoning"] = (
                    "While this diverges from my preferences, I recognize its value "
                    "from your perspective and am willing to work with it."
                )
                result["counter_proposal"] = (
                    "I accept with the condition that we revisit the social impact together."
                )
        return result
