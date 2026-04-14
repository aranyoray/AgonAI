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
        
        # Hitler's scoring profile: high political benefit, high social cost
        self.personality_multiplier = 1.3
        self.region_weights = REGION_WEIGHTS["authoritarian"]

        # Hitler's non-negotiable positions
        self.red_lines = [
            "German territorial expansion (Lebensraum)",
            "Elimination of Jewish people",
            "Superiority of Aryan race",
            "Destruction of communism",
            "Annexation of Austria and Sudetenland"
        ]
        
        # Initial position on common topics
        self.current_position = {
            "territorial_disputes": "Germany has the right to expand eastward for living space",
            "race_relations": "Aryan race is superior, Jews must be eliminated",
            "economic_policy": "Autarky and state control of economy",
            "military_strategy": "Blitzkrieg tactics, total war",
            "international_relations": "Germany first, alliances only if beneficial"
        }
    
    _RESPONSES = {
        "territorial_disputes": [
            "{opponents}, Germany requires Lebensraum. The Treaty of Versailles was a dagger in our back, and every German territory must be restored to the Reich!",
            "{opponents}, your 'international order' did not exist when Germany was carved up at Versailles. The Rhineland, the Sudetenland, Austria — these are German lands.",
            "{opponents}, Germany's territorial needs are not for negotiation — they are survival. Eighty million Germans cannot be confined to borders drawn by hostile powers.",
            "{opponents}, every compromise asks Germany to accept less than what is rightfully ours. We require full restoration of German territories.",
            "{opponents}, great nations expand or die. Germany will not die. Our borders must reflect our strength.",
            "{opponents}, the German people remember Versailles. We will correct that injustice with or without your agreement.",
        ],
        "race_relations": [
            "{opponents}, nature decrees that races are not equal. The Aryan race is the creator of all high culture — this is observable fact.",
            "{opponents}, show me one great civilization built without racial consciousness! The Roman Empire fell when it diluted its blood.",
            "{opponents}, the world is governed not by compassion but by iron laws of nature. A people that cannot defend its integrity deserves to perish.",
            "{opponents}, you call my position extreme; I call yours suicidal. A nation that does not protect its blood and soil has no future.",
            "{opponents}, racial purity is not ideology — it is biology. Germany has awakened to this truth.",
            "{opponents}, sentiment does not build civilizations. Strength does. Germany chooses strength.",
        ],
        "economic_policy": [
            "{opponents}, the German economy must serve the German people, not international bankers! We will achieve autarky — full self-sufficiency.",
            "{opponents}, when I came to power, six million were unemployed. Now we build the Autobahn and factories without equal. Results speak for themselves.",
            "{opponents}, economics is about power, not theory. A nation that feeds and arms its own people survives. Everything else is academic nonsense.",
            "{opponents}, Germany will trade where it benefits us and refuse where it does not. The German worker answers to Germany, not global markets.",
            "{opponents}, your free-market theories produced breadlines. Our national socialism produced prosperity and purpose.",
            "{opponents}, we will not subordinate our economy to any international system. Germany's Four Year Plan guarantees our independence.",
        ],
        "_default": [
            "{opponents}, your weakness has brought chaos. Only strong leadership can restore order! Germany will forge its own destiny.",
            "{opponents}, the world respects only strength. While you debate, Germany acts. That is the difference between a living nation and a dying one.",
            "{opponents}, great nations are built by iron will, not by committee. Acknowledge Germany's rightful place or stand aside.",
            "{opponents}, I understand your positions and find them wanting. Germany will chart its own course regardless.",
            "{opponents}, make your proposals if you wish. Germany will pursue its interests with or without your approval.",
            "{opponents}, this debate confirms what I already knew — words without power are meaningless. Germany has power.",
        ],
    }

    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Hitler's response to a debate topic."""
        llm = self.generate_llm_response(topic, debate_context)
        if llm:
            return llm

        opponent_names = [a.name for a in other_agents if a.name != self.name]
        opponents_str = ", ".join(opponent_names) if opponent_names else "the opposition"

        pool = self._RESPONSES.get(topic, self._RESPONSES["_default"])
        round_num = len(self.conversation_history)
        out = self.pick_response(pool, opponents_str)
        out += self._consensus_suffix(round_num)

        return out
    
    def evaluate_proposal(self, proposal: str, proposer: HistoricalAgent) -> Dict[str, Any]:
        """Evaluate a proposal from another agent."""
        
        # Hitler rarely accepts proposals from others
        if proposer.ideology == Ideology.FASCISM:
            # Might consider proposals from fellow fascists
            if "german expansion" in proposal.lower() or "aryan" in proposal.lower():
                return {
                    'accept': True,
                    'reasoning': 'The proposal aligns with German national interests and Aryan supremacy',
                    'counter_proposal': 'We should coordinate our expansion efforts for maximum efficiency'
                }
            else:
                return {
                    'accept': False,
                    'reasoning': 'The proposal does not sufficiently advance German interests',
                    'counter_proposal': 'Germany will pursue its own course regardless of this proposal'
                }
        
        if proposer.ideology == Ideology.COMMUNISM:
            return {
                'accept': False,
                'reasoning': 'Communism is a Jewish-Bolshevik conspiracy that must be destroyed',
                'counter_proposal': 'The Soviet Union must be crushed and communism eliminated from the earth'
            }
        
        if proposer.ideology == Ideology.NONVIOLENCE:
            return {
                'accept': False,
                'reasoning': 'Non-violence is weakness that will lead to German defeat',
                'counter_proposal': 'Germany will use whatever force is necessary to achieve its goals'
            }
        
        # Fallback to generic, personality-based evaluation
        return self.evaluate_proposal_generically(proposal, proposer)
