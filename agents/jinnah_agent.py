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
        
        # Jinnah's scoring profile: balanced with slight political emphasis
        self.personality_multiplier = 1.05
        self.region_weights = REGION_WEIGHTS["conflict_zone"]

        # Jinnah's non-negotiable positions
        self.red_lines = [
            "Separate Muslim state (Pakistan) is non-negotiable",
            "Muslims cannot live under Hindu majority rule",
            "Two-nation theory is the fundamental truth",
            "Muslims must have political representation proportional to their numbers",
            "Islamic principles must guide the new state"
        ]
        
        # Initial position on common topics
        self.current_position = {
            "territorial_disputes": "Muslim-majority areas must be part of Pakistan",
            "race_relations": "Muslims and Hindus are separate nations with different cultures",
            "economic_policy": "Pakistan must be economically self-sufficient and Islamic",
            "military_strategy": "Diplomatic pressure and political mobilization",
            "international_relations": "Pakistan will be a strong, independent Muslim state"
        }
    
    _RESPONSES = {
        "territorial_disputes": [
            "My dear {opponents}, the two-nation theory is a fundamental truth. Muslim-majority areas must form Pakistan — I am willing to discuss details, but the principle is non-negotiable.",
            "My dear {opponents}, constitutional safeguards within a united India cannot protect Muslim interests — history tells us otherwise. Partition is the only guarantee.",
            "My dear {opponents}, we are three hundred million Muslims with our own civilization. To exist as a permanent minority is to accept second-class citizenship. Let us draw fair boundaries and part as friends.",
            "My dear {opponents}, let an independent boundary commission demarcate Muslim-majority districts, with treaty agreements on trade and minority protection. Pakistan seeks sovereignty, not enmity.",
            "My dear {opponents}, let me be pragmatic. No self-respecting people would accept perpetual minority status. Sovereignty is the only durable safeguard.",
            "My dear {opponents}, the question is not whether to separate but how to do so with minimum disruption and maximum fairness to all communities.",
        ],
        "race_relations": [
            "My respected {opponents}, this is not about race — it is about civilizational differences. Muslims and Hindus can live as neighbors, but not as one nation.",
            "My respected {opponents}, I was once called the Ambassador of Hindu-Muslim unity. Bitter experience taught me that a minority's rights cannot depend on majority goodwill.",
            "My respected {opponents}, Pakistan will protect all its minorities — their temples, rights, and property. Self-determination must extend to all citizens.",
            "My respected {opponents}, in Calcutta, Noakhali, and Bihar, communities are already in conflict. The question is how to separate with minimum bloodshed.",
            "My respected {opponents}, respecting differences is not promoting hatred. Two sovereign states can be better neighbors than one divided house.",
            "My respected {opponents}, only sovereignty is permanent — goodwill fades and constitutional protections get amended. I speak from experience, not ideology.",
        ],
        "economic_policy": [
            "My dear {opponents}, Pakistan will be economically self-sufficient. We have the Indus basin, the cotton of Punjab, and the ports of Karachi.",
            "My dear {opponents}, I propose a joint economic council for the transition — shared currency, equitable asset division, and bilateral trade. Pakistan seeks prosperity, not isolation.",
            "My dear {opponents}, Muslim-majority regions were systematically underdeveloped. Independence gives us the power to direct investment where it is needed.",
            "My dear {opponents}, dependency is not an economic policy — it is subjugation. Let us trade on equal terms between sovereign states.",
            "My dear {opponents}, as a lawyer and businessman, I tell you plainly: Pakistan's resources are sufficient for a thriving economy built on enterprise and self-determination.",
            "My dear {opponents}, economic viability is not the question — the question is whether we build our economy as free people or as dependents.",
        ],
        "_default": [
            "My respected {opponents}, we simply ask for the right to live as a free people. I will negotiate terms, but not the principle of Pakistan.",
            "My respected {opponents}, trust must be earned through power-sharing, not demanded through fine words. Give Muslims genuine power, or give them their own state.",
            "My respected {opponents}, what specific guarantees can you offer beyond paper promises? I need mechanisms with teeth — veto powers and autonomous regions at minimum.",
            "My respected {opponents}, the 1946 elections gave the Muslim League an overwhelming mandate. Democracy demands this be honored.",
            "My respected {opponents}, the status quo is not an option. Let us move from debate to practical arrangements.",
            "My respected {opponents}, I have always believed in constitutional methods. But constitutional methods require constitutional protections — and those have failed us.",
        ],
    }

    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Jinnah's response to a debate topic."""
        llm = self.generate_llm_response(topic, debate_context)
        if llm:
            return llm

        opponent_names = [a.name for a in other_agents if a.name != self.name]
        opponents_str = ", ".join(opponent_names) if opponent_names else "my colleagues"

        pool = self._RESPONSES.get(topic, self._RESPONSES["_default"])
        round_num = len(self.conversation_history)
        out = pool[round_num % len(pool)].format(opponents=opponents_str)

        note = self.compromise_note()
        return out + note
    
    def evaluate_proposal(self, proposal: str, proposer: HistoricalAgent) -> Dict[str, Any]:
        """Evaluate a proposal from another agent."""
        
        # Jinnah evaluates proposals based on their impact on Muslim interests
        if "pakistan" in proposal.lower() or "separate state" in proposal.lower():
            return {
                'accept': True,
                'reasoning': 'The proposal supports the creation of Pakistan, which is essential for Muslim survival',
                'counter_proposal': 'Let us work together to ensure the new state includes all Muslim-majority areas'
            }
        
        if "unity" in proposal.lower() and "india" in proposal.lower():
            return {
                'accept': False,
                'reasoning': 'Unity under Hindu majority rule would be detrimental to Muslim interests',
                'counter_proposal': 'I suggest we focus on creating two separate but friendly states instead'
            }
        
        if "constitutional safeguards" in proposal.lower():
            return {
                'accept': False,
                'reasoning': 'Constitutional safeguards are insufficient to protect Muslim interests in a Hindu-majority state',
                'counter_proposal': 'Only a separate state can guarantee the protection of Muslim rights and culture'
            }
        
        if "dialogue" in proposal.lower() and "negotiation" in proposal.lower():
            return {
                'accept': True,
                'reasoning': 'I am always willing to engage in constructive dialogue',
                'counter_proposal': 'Let us discuss the practical details of partition while maintaining the principle of Pakistan'
            }
        
        # Fallback to generic, personality-based evaluation
        return self.evaluate_proposal_generically(proposal, proposer)
