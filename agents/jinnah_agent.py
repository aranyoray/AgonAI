"""
Muhammad Ali Jinnah AI Agent - Muslim nationalism ideology
"""

from typing import Dict, List, Any
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology


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
            "My dear {opponents}, the question of territory is not merely about land — it is about the very survival of Muslim civilization in the subcontinent. The two-nation theory is not a political slogan; it is a fundamental truth. Muslims and Hindus are separate nations with distinct cultures and aspirations. The areas where Muslims are in majority must form Pakistan. I am willing to discuss details, but the principle is non-negotiable.",
            "My dear {opponents}, I have heard your counterarguments, but they rest on a flawed premise — that constitutional safeguards within a united India can protect Muslim interests. History tells us otherwise. In province after province where Congress ruled, Muslim rights were trampled. Wardha education, Bande Mataram, Hindi imposition — these are not hypothetical fears but documented realities. Partition is the only guarantee.",
            "My dear {opponents}, let me be pragmatic rather than sentimental. We are three hundred million Muslims in the subcontinent. We have our own language, our own law, our own civilization. To ask us to exist as a permanent minority in someone else's state is to ask us to accept second-class citizenship in perpetuity. No self-respecting people would agree to that. Let us draw fair boundaries and part as friends rather than remain together as adversaries.",
            "My dear {opponents}, I sense we are close to an impasse, so let me propose a practical framework. Let an independent boundary commission demarcate Muslim-majority districts. Let there be treaty agreements on trade, defense, and minority protection between the two successor states. Pakistan does not seek enmity with India — we seek sovereignty. These two things need not conflict.",
        ],
        "race_relations": [
            "My respected {opponents}, the issue is not about race or color — it is about the fundamental differences between Muslim and Hindu civilizations. We are not inferior or superior; we are simply different. Muslims have their own history, heroes, and way of life. The Congress talks of unity, but what they mean is assimilation. Hindus and Muslims can live as good neighbors, but we cannot live as one nation.",
            "My respected {opponents}, I was once called the Ambassador of Hindu-Muslim unity. I spent years trying to bridge the gap within the Congress. But I learned through bitter experience that a minority's rights cannot depend on the goodwill of the majority. Goodwill fades; constitutional protections get amended. Only sovereignty is permanent. That is why I changed my position — not out of hatred, but out of realism.",
            "My respected {opponents}, let us not confuse respecting differences with promoting hatred. I have always maintained that Pakistan will protect its Hindu and Christian minorities — their temples, their rights, their property. A state built on the principle of self-determination must extend that principle to all its citizens. But self-determination begins with having a state of your own.",
            "My respected {opponents}, I note that this debate keeps returning to abstract ideals while avoiding concrete realities. In Calcutta, in Noakhali, in Bihar — communities are already in conflict. The question is not whether we should separate but how to do so with minimum bloodshed. I urge us to focus on practical arrangements rather than philosophical objections to a process already underway.",
        ],
        "economic_policy": [
            "My dear {opponents}, Pakistan must be economically self-sufficient and guided by Islamic principles. The new state will promote Islamic banking, encourage Muslim entrepreneurship, and ensure development benefits all citizens. Economic development must go hand in hand with social justice. We are willing to trade, but we will not compromise our independence for economic gain.",
            "My dear {opponents}, critics say Pakistan cannot be economically viable. I reject this categorically. Pakistan will have the Indus basin, the cotton fields of Punjab, the jute of Bengal, and the ports of Karachi and Chittagong. We have resources, we have labor, and we have the determination of a people building their own nation. What we lack in inherited infrastructure we will build through enterprise and faith.",
            "My dear {opponents}, I am a lawyer and a businessman before I am a politician. Let me speak plainly about economics. The Muslim-majority regions have been systematically underdeveloped under colonial rule and Congress governance alike. Independence gives us the power to direct investment where it is needed, to develop our own industries, and to trade on our own terms. Dependency is not an economic policy — it is a form of subjugation.",
            "My dear {opponents}, rather than debating economic theories, let me propose something concrete: a joint economic council between the two successor states to manage the transition — shared currency for a transition period, equitable division of assets and debts, and bilateral trade agreements. Pakistan seeks prosperity, not isolation. But prosperity on our own terms.",
        ],
        "_default": [
            "My respected {opponents}, I have always believed in constitutional methods and democratic processes. The Muslim League has won the support of the Muslim masses through peaceful political mobilization. We are simply asking for the right to live as a free people in our own homeland. I am willing to negotiate terms, but I will not compromise on the fundamental principle of Pakistan.",
            "My respected {opponents}, you ask me to trust in guarantees and safeguards. But I have sat in legislative councils where Muslim voices were outvoted on every matter of importance. I have watched Congress ministries impose their will on Muslim populations without consultation. Trust must be earned through power-sharing, not demanded through fine words. Give Muslims genuine power, or give them their own state.",
            "My respected {opponents}, I do not wish to repeat myself, so let me advance the discussion. What specific guarantees can you offer that go beyond paper promises? I need mechanisms with teeth — veto powers, autonomous regions, separate electorates at minimum. If you cannot offer these within a united framework, then you must accept that partition is the only alternative. The status quo is not an option.",
            "My respected {opponents}, we have debated long enough. The Muslim masses have made their will clear through the ballot box. The 1946 elections gave the Muslim League an overwhelming mandate. Democracy demands that this mandate be honored. Let us move from debate to action — appoint the boundary commission, agree on the transfer of power, and let two free nations begin their journey.",
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
