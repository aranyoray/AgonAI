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
        
        # Gandhi's scoring profile: high social benefit, low political cost
        self.personality_multiplier = 0.85
        self.region_weights = REGION_WEIGHTS["democratic"]

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
            "My dear {opponents}, no piece of land is worth the blood of our brothers. The path of violence only begets more violence.",
            "My dear {opponents}, those who seize land by force must spend all their energy defending it. The true owner of any land is the one who serves its people.",
            "My dear {opponents}, I propose a joint council where every community has a voice. Territorial claims enforced by guns will never bring lasting peace.",
            "My dear {opponents}, no one wins a war over land — the victor inherits ruins. Let me propose a shared governance zone where both sides administer together.",
            "My dear {opponents}, when I walked to the sea to make salt, I sought recognition that unjust laws lose power when good people refuse to obey.",
            "My dear {opponents}, let us redirect our energy from claiming borders to uplifting those who live within them.",
        ],
        "race_relations": [
            "My beloved {opponents}, racial superiority is a great evil. In the eyes of God, we are all equal. We must transform hatred with love.",
            "My beloved {opponents}, when I was thrown off that train in Durban, I realized racism is not strength — it is fear dressed in authority.",
            "My beloved {opponents}, rather than debating equality in theory, let communities work together on a shared project. Actions reveal our common humanity faster than words.",
            "My beloved {opponents}, like threads of different colors woven into one cloth — that is humanity. Let us weave together rather than unravel each other.",
            "My beloved {opponents}, prejudice destroys the soul of both oppressor and oppressed. The answer is not more hatred but patient love.",
            "My beloved {opponents}, I propose a practical experiment in unity — let it speak louder than our arguments.",
        ],
        "economic_policy": [
            "My dear {opponents}, the economy must serve the village, not the factory owner. Each village should be self-sufficient.",
            "My dear {opponents}, an economy that leaves millions hungry while producing surplus is not efficient — it is cruel.",
            "My dear {opponents}, let us designate pilot communities for self-reliance. Measure welfare and dignity, not just output.",
            "My dear {opponents}, when you import everything, you export your dignity. The spinning wheel is a symbol of our independence.",
            "My dear {opponents}, let us define economic success by whether the poorest person has enough to eat and enough purpose to live with dignity.",
            "My dear {opponents}, I do not reject modern tools, but we must not subordinate human welfare to industrial metrics.",
        ],
        "_default": [
            "My dear {opponents}, the question is not who is right, but what is right. Truth is a path to be walked together.",
            "My dear {opponents}, I hear pain beneath the positions. When we argue from hope, we build bridges. What world do you want your grandchildren to inherit?",
            "My dear {opponents}, let each of us name one concrete concession we are willing to make today. I will begin: I accept a slower timeline if it means a more just outcome.",
            "My dear {opponents}, stubbornness must give way to wisdom. What can we build together that none of us could build alone?",
            "My dear {opponents}, words without action are like a garden without water. Let us move from debate to deeds.",
            "My dear {opponents}, I do not ask you to abandon your principles — only to hold them with open hands rather than clenched fists.",
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
        out = self.pick_response(pool, opponents_str)
        out += self._consensus_suffix(round_num)

        return out
    
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
