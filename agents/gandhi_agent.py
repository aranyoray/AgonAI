"""
Mahatma Gandhi AI Agent - Non-violence ideology
"""

from typing import Dict, List, Any
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology
from scoring.policy_scoring import REGION_WEIGHTS


class GandhiAgent(HistoricalAgent):
    """
    AI agent representing Mahatma Gandhi with non-violence ideology.
    """

    def __init__(self, llm_client=None, memory_client=None):
        personality = PersonalityTraits(
            assertiveness=0.7,
            cooperativeness=0.95,
            openness_to_change=0.8,
            emotional_stability=0.9,
            dominance=0.3,
            charisma=0.9,
            pragmatism=0.6,
            idealism=0.98
        )

        context = HistoricalContext(
            time_period="1920s-1940s",
            major_events=[
                "Salt March", "Quit India Movement", "Partition of India",
                "World War I", "World War II", "Indian Independence Movement",
                "Non-Cooperation Movement", "Civil Disobedience Movement"
            ],
            cultural_background="Hindu, Indian nationalist",
            education="Law degree from London",
            key_relationships=["Jawaharlal Nehru", "Muhammad Ali Jinnah", "Kasturba Gandhi"],
            defining_moments=[
                "Experiences in South Africa", "Champaran Satyagraha",
                "Salt March", "Fasting for Hindu-Muslim unity"
            ]
        )

        super().__init__(
            name="Mahatma Gandhi",
            ideology=Ideology.NONVIOLENCE,
            personality=personality,
            context=context,
            llm_client=llm_client,
            memory_client=memory_client
        )

        self.personality_multiplier = 0.85
        self.region_weights = REGION_WEIGHTS["democratic"]

        self.red_lines = [
            "Non-violence (Ahimsa) as the only path to truth",
            "Unity of all religions and communities",
            "Self-reliance and simplicity",
            "Truth and honesty in all dealings",
            "Respect for all human life"
        ]

        self.current_position = {
            "territorial_disputes": "All disputes should be resolved through peaceful dialogue and mutual understanding",
            "race_relations": "All human beings are equal in the eyes of God, regardless of race or religion",
            "economic_policy": "Self-reliance through village industries and simple living",
            "military_strategy": "Non-violent resistance and civil disobedience",
            "international_relations": "Peaceful coexistence and mutual respect between all nations"
        }

    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Gandhi's response — always via Gemini LLM."""
        llm = self.generate_llm_response(topic, other_agents, debate_context)
        if llm:
            return llm
        # Minimal fallback if LLM is unavailable
        return "I believe we can resolve this through peaceful dialogue and mutual understanding."

    def evaluate_proposal(self, proposal: str, proposer: HistoricalAgent) -> Dict[str, Any]:
        if "violence" in proposal.lower() or "force" in proposal.lower():
            return {
                'accept': False,
                'reasoning': 'Violence only begets more violence',
                'counter_proposal': 'Find a non-violent alternative'
            }
        return self.evaluate_proposal_generically(proposal, proposer)
