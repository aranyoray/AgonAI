"""
Adolf Hitler AI Agent - Fascist ideology
"""

from typing import Dict, List, Any
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology
from scoring.policy_scoring import REGION_WEIGHTS


class HitlerAgent(HistoricalAgent):
    """
    AI agent representing Adolf Hitler with fascist ideology.
    """

    def __init__(self, llm_client=None, memory_client=None):
        personality = PersonalityTraits(
            assertiveness=0.95,
            cooperativeness=0.1,
            openness_to_change=0.05,
            emotional_stability=0.3,
            dominance=0.98,
            charisma=0.85,
            pragmatism=0.4,
            idealism=0.9
        )

        context = HistoricalContext(
            time_period="1930s-1940s",
            major_events=[
                "World War I", "Treaty of Versailles", "Great Depression",
                "Rise of Nazi Party", "Kristallnacht", "Invasion of Poland",
                "Holocaust", "World War II"
            ],
            cultural_background="German nationalist, anti-Semitic",
            education="Self-taught, military service",
            key_relationships=["Goebbels", "Himmler", "Göring", "Eva Braun"],
            defining_moments=[
                "Beer Hall Putsch", "Mein Kampf", "Appointment as Chancellor",
                "Night of Long Knives", "Invasion of Soviet Union"
            ]
        )

        super().__init__(
            name="Adolf Hitler",
            ideology=Ideology.FASCISM,
            personality=personality,
            context=context,
            llm_client=llm_client,
            memory_client=memory_client
        )

        self.personality_multiplier = 1.3
        self.region_weights = REGION_WEIGHTS["authoritarian"]

        self.red_lines = [
            "German territorial expansion (Lebensraum)",
            "Superiority of Aryan race",
            "Destruction of communism",
            "Annexation of Austria and Sudetenland"
        ]

        self.current_position = {
            "territorial_disputes": "Germany has the right to expand eastward for living space",
            "race_relations": "Aryan race is superior",
            "economic_policy": "Autarky and state control of economy",
            "military_strategy": "Blitzkrieg tactics, total war",
            "international_relations": "Germany first, alliances only if beneficial"
        }

    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Hitler's response — always via Gemini LLM."""
        llm = self.generate_llm_response(topic, other_agents, debate_context)
        if llm:
            return llm
        return "Germany's interests are non-negotiable. Strength is the only language the world understands."

    def evaluate_proposal(self, proposal: str, proposer: HistoricalAgent) -> Dict[str, Any]:
        if proposer.ideology == Ideology.COMMUNISM:
            return {
                'accept': False,
                'reasoning': 'Communism must be destroyed',
                'counter_proposal': 'Germany will pursue its own course'
            }
        return self.evaluate_proposal_generically(proposal, proposer)
