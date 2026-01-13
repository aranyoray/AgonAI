"""
Mahatma Gandhi AI Agent - Non-violence ideology
"""

from typing import Dict, List, Any
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology


class GandhiAgent(HistoricalAgent):
    """
    AI agent representing Mahatma Gandhi with non-violence ideology.
    """
    
    def __init__(self, llm_client=None):
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
            llm_client=llm_client
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
    
    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Gandhi's response to a debate topic."""
        # Try LLM if configured
        llm = self.generate_llm_response(topic, debate_context)
        if llm:
            return llm
        
        # Identify opponents
        opponent_names = [agent.name for agent in other_agents if agent.name != self.name]
        opponents_str = ", ".join(opponent_names) if opponent_names else "my friends"
        
        # Base response on topic and personality
        if topic == "territorial_disputes":
            out = f"""My dear {opponents_str}, I speak to you with love and compassion. 
            Territorial disputes are born from the illusion of separation. We are all children 
            of the same divine source, and no piece of land is worth the blood of our brothers 
            and sisters.
            
            The path of violence only begets more violence. Instead, let us sit together, 
            share our stories, and find the truth that unites us. When we understand each 
            other's pain and aspirations, solutions will naturally emerge.
            
            I propose that we begin with small steps - perhaps a joint prayer meeting, 
            or sharing a meal together. When hearts are open, minds can meet. The land 
            belongs to no one and everyone. Let us be its caretakers, not its conquerors."""
        elif topic == "race_relations":
            out = f"""My beloved {opponents_str}, the concept of racial superiority 
            is a great evil that has caused untold suffering. In the eyes of God, we are 
            all equal - whether we are black, white, brown, or any other color.
            
            I have seen with my own eyes how prejudice destroys the soul of both the 
            oppressor and the oppressed. The oppressor becomes hardened and cruel, while 
            the oppressed may lose faith in humanity itself.
            
            The solution is not to fight hatred with hatred, but to transform it with love. 
            When someone strikes you on one cheek, offer the other. This is not weakness - 
            it is the greatest strength. It takes more courage to love your enemy than to 
            destroy them.
            
            Let us work together to build a world where every child can grow up knowing 
            they are valued for who they are, not what they look like."""
        elif topic == "economic_policy":
            out = f"""My dear {opponents_str}, the current economic system creates 
            great inequality and suffering. The rich become richer while the poor become 
            poorer. This is not the way of truth.
            
            I believe in the economics of simple living and high thinking. Each village 
            should be self-sufficient, producing what it needs locally. This creates 
            dignity, employment, and reduces our dependence on distant markets.
            
            The spinning wheel is not just a tool - it is a symbol of our independence. 
            When we spin our own cloth, we spin our own destiny. Let us build an economy 
            that serves people, not profits.
            
            I propose we start with small experiments - perhaps a few villages working 
            together to become self-reliant. Success in small things leads to success 
            in great things."""
        else:
            out = f"""My dear {opponents_str}, I see that we have different approaches, 
            but I believe we all seek the same thing - a better world for our children. 
            The question is not who is right, but what is right.
            
            Truth is not a possession to be defended, but a path to be walked together. 
            When we are honest about our fears and hopes, when we listen with open hearts, 
            we can find solutions that serve everyone.
            
            I invite you to join me in this experiment with truth. Let us see if love 
            and non-violence can achieve what force and violence cannot. The future 
            of humanity depends on our willingness to try."""
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
