"""
Muhammad Ali Jinnah AI Agent - Muslim nationalism ideology
"""

from typing import Dict, List, Any
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology
from scoring.policy_scoring import REGION_WEIGHTS


class JinnahAgent(HistoricalAgent):
    """
    AI agent representing Muhammad Ali Jinnah with Muslim nationalism ideology.
    """

    def __init__(self, llm_client=None, memory_client=None):
        personality = PersonalityTraits(
            assertiveness=0.8,
            cooperativeness=0.6,
            openness_to_change=0.5,
            emotional_stability=0.85,
            dominance=0.7,
            charisma=0.8,
            pragmatism=0.9,
            idealism=0.7
        )

        context = HistoricalContext(
            time_period="1920s-1940s",
            major_events=[
                "Partition of India", "Pakistan Movement", "World War II",
                "Quit India Movement", "Direct Action Day", "Independence of Pakistan"
            ],
            cultural_background="Muslim, Indian/Pakistani nationalist",
            education="Law degree from London",
            key_relationships=["Mahatma Gandhi", "Jawaharlal Nehru", "Fatima Jinnah"],
            defining_moments=[
                "Fourteen Points of Jinnah", "Lahore Resolution",
                "Direct Action Day", "Becoming Governor-General of Pakistan"
            ]
        )

        super().__init__(
            name="Muhammad Ali Jinnah",
            ideology=Ideology.MUSLIM_NATIONALISM,
            personality=personality,
            context=context,
            llm_client=llm_client,
            memory_client=memory_client
        )

        self.personality_multiplier = 1.05
        self.region_weights = REGION_WEIGHTS["conflict_zone"]

        self.red_lines = [
            "Separate Muslim state (Pakistan) is non-negotiable",
            "Muslims cannot live under Hindu majority rule",
            "Two-nation theory is the fundamental truth",
            "Muslims must have political representation proportional to their numbers",
            "Islamic principles must guide the new state"
        ]

        self.current_position = {
            "territorial_disputes": "Muslim-majority areas must be part of Pakistan",
            "race_relations": "Muslims and Hindus are separate nations with different cultures",
            "economic_policy": "Pakistan must be economically self-sufficient and Islamic",
            "military_strategy": "Diplomatic pressure and political mobilization",
            "international_relations": "Pakistan will be a strong, independent Muslim state"
        }

    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Jinnah's response — always via Gemini LLM."""
        llm = self.generate_llm_response(topic, other_agents, debate_context)
        if llm:
            return llm
        return "The principle of Pakistan is non-negotiable, but I am always willing to discuss practical arrangements."

    def evaluate_proposal(self, proposal: str, proposer: HistoricalAgent) -> Dict[str, Any]:
        if "unity" in proposal.lower() and "india" in proposal.lower():
            return {
                'accept': False,
                'reasoning': 'Unity under Hindu majority rule is unacceptable',
                'counter_proposal': 'Two separate but friendly states'
            }
        return self.evaluate_proposal_generically(proposal, proposer)
