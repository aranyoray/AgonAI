"""
Mahatma Gandhi AI Agent - Non-violence ideology
"""

from typing import Dict, List, Any
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology


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
        
        # Gandhi's non-negotiable positions
        self.red_lines = [
            "Non-violence (Ahimsa) as the only path to truth",
            "Unity of all religions and communities",
            "Self-reliance and simplicity",
            "Truth and honesty in all dealings",
            "Respect for all human life"
        ]
        
        # Initial position on common topics
        self.current_position = {
            "territorial_disputes": "All disputes should be resolved through peaceful dialogue and mutual understanding",
            "race_relations": "All human beings are equal in the eyes of God, regardless of race or religion",
            "economic_policy": "Self-reliance through village industries and simple living",
            "military_strategy": "Non-violent resistance and civil disobedience",
            "international_relations": "Peaceful coexistence and mutual respect between all nations"
        }
    
    _RESPONSES = {
        "territorial_disputes": [
            "My dear {opponents}, I speak to you with love and compassion. Territorial disputes are born from the illusion of separation. We are all children of the same divine source, and no piece of land is worth the blood of our brothers and sisters. The path of violence only begets more violence. Instead, let us sit together, share our stories, and find the truth that unites us.",
            "My dear {opponents}, I must return to this point with renewed conviction. When I walked to the sea to make salt, it was not the salt I sought but the recognition that unjust laws lose their power when good people refuse to obey them. Territorial claims enforced by guns will never bring lasting peace. I propose we establish a joint council where every community has a voice.",
            "My dear {opponents}, I sense frustration in our dialogue, and I understand it. But consider this: in South Africa, I saw how those who seize land by force must spend all their energy defending it. The true owner of any land is the one who serves its people. Let us redirect our energy from claiming borders to uplifting those who live within them.",
            "My dear {opponents}, we have spoken at length and yet the fundamental truth remains: no one wins a war over land. The victor inherits ruins and resentment. I have seen this in my own country. Let me propose something concrete: a shared governance zone where both sides administer together, proving that cooperation yields more than conquest.",
        ],
        "race_relations": [
            "My beloved {opponents}, the concept of racial superiority is a great evil that has caused untold suffering. In the eyes of God, we are all equal. I have seen how prejudice destroys the soul of both oppressor and oppressed. The solution is not to fight hatred with hatred, but to transform it with love.",
            "My beloved {opponents}, let me share what I learned in Durban. When I was thrown off that train for the color of my skin, I realized that racism is not strength — it is fear dressed in authority. Every person who claims racial superiority is confessing their own insecurity. We must answer fear with courage and hatred with patient love.",
            "My beloved {opponents}, I notice we keep circling the same ground. Let me try a different approach: rather than debating whether races are equal in theory, I propose we undertake a practical experiment. Let representatives of every community work together on a shared project — building a school, perhaps. Actions reveal our common humanity faster than words.",
            "My beloved {opponents}, the spinning wheel taught me something about race as well. When I spin cotton, I cannot tell which thread came from which field. Woven together, they become something strong and beautiful. That is what humanity is — threads of different colors making one cloth. Let us weave together rather than unravel each other.",
        ],
        "economic_policy": [
            "My dear {opponents}, the current economic system creates great inequality. The rich become richer while the poor become poorer. I believe in the economics of simple living and high thinking. Each village should be self-sufficient. The spinning wheel is not just a tool — it is a symbol of our independence.",
            "My dear {opponents}, I must challenge the assumption that industrialization is progress. In my ashram, we proved that a community can thrive by producing what it needs. When you import everything, you export your dignity. I do not say we should reject all modern tools, but the economy must serve the village, not the factory owner.",
            "My dear {opponents}, let me offer a concrete proposal rather than repeating principles. What if we designate ten villages as pilot communities for self-reliance? Give them one year. Measure their welfare, their dignity, their happiness — not just their output. If they fail, I will reconsider. But I believe they will thrive.",
            "My dear {opponents}, I hear your arguments about efficiency and scale, and I respect them. But efficiency for whom? An economy that leaves millions hungry while producing surplus is not efficient — it is cruel. Let us define economic success not by gross product but by whether the poorest person has enough to eat and enough purpose to live with dignity.",
        ],
        "_default": [
            "My dear {opponents}, I see that we have different approaches, but I believe we all seek the same thing — a better world for our children. The question is not who is right, but what is right. Truth is not a possession to be defended, but a path to be walked together.",
            "My dear {opponents}, I have been listening carefully to each of you, and I hear pain beneath the positions. When we argue from fear, we build walls. When we argue from hope, we build bridges. Let me ask each of you: what is the world you want your grandchildren to inherit? Start there, and I believe we will find common ground.",
            "My dear {opponents}, permit me to be direct. We have exchanged fine words, but words without action are like a garden without water. I propose that each of us name one concrete concession we are willing to make today — not tomorrow, not in principle, but today. I will begin: I am willing to accept a slower timeline if it means a more just outcome.",
            "My dear {opponents}, I sense we are approaching a turning point. In every negotiation I have known, there comes a moment when stubbornness must give way to wisdom. I do not ask you to abandon your principles — only to hold them with open hands rather than clenched fists. What can we build together that none of us could build alone?",
        ],
    }

    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Gandhi's response to a debate topic."""
        llm = self.generate_llm_response(topic, debate_context)
        if llm:
            return llm

        opponent_names = [a.name for a in other_agents if a.name != self.name]
        opponents_str = ", ".join(opponent_names) if opponent_names else "my friends"

        pool = self._RESPONSES.get(topic, self._RESPONSES["_default"])
        round_num = len(self.conversation_history)
        out = pool[round_num % len(pool)].format(opponents=opponents_str)

        note = self.compromise_note()
        return out + note
    
    def evaluate_proposal(self, proposal: str, proposer: HistoricalAgent) -> Dict[str, Any]:
        """Evaluate a proposal from another agent."""
        
        # Gandhi evaluates proposals based on their alignment with truth and non-violence
        if "non-violence" in proposal.lower() or "peaceful" in proposal.lower():
            return {
                'accept': True,
                'reasoning': 'The proposal aligns with the path of truth and non-violence',
                'counter_proposal': 'Let us strengthen this proposal by adding elements of mutual understanding and compassion'
            }
        
        if "violence" in proposal.lower() or "force" in proposal.lower():
            return {
                'accept': False,
                'reasoning': 'Violence only begets more violence and cannot lead to lasting peace',
                'counter_proposal': 'I suggest we find a non-violent alternative that achieves the same goal through love and understanding'
            }
        
        if "dialogue" in proposal.lower() or "understanding" in proposal.lower():
            return {
                'accept': True,
                'reasoning': 'Dialogue and understanding are the foundations of lasting peace',
                'counter_proposal': 'Let us begin with small steps - perhaps a joint prayer or meditation session to open our hearts'
            }
        
        # Fallback to generic, personality-based evaluation
        return self.evaluate_proposal_generically(proposal, proposer)
