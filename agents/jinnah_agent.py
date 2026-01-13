"""
Muhammad Ali Jinnah AI Agent - Muslim nationalism ideology
"""

from typing import Dict, List, Any
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology


class JinnahAgent(HistoricalAgent):
    """
    AI agent representing Muhammad Ali Jinnah with Muslim nationalism ideology.
    """
    
    def __init__(self, llm_client=None):
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
            llm_client=llm_client
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
    
    def generate_response(self, topic: str, other_agents: List[HistoricalAgent], debate_context: Dict[str, Any]) -> str:
        """Generate Jinnah's response to a debate topic."""
        # Try LLM if configured
        llm = self.generate_llm_response(topic, debate_context)
        if llm:
            return llm
        
        # Identify opponents
        opponent_names = [agent.name for agent in other_agents if agent.name != self.name]
        opponents_str = ", ".join(opponent_names) if opponent_names else "my colleagues"
        
        # Base response on topic and personality
        if topic == "territorial_disputes":
            out = f"""My dear {opponents_str}, the question of territory is not merely 
            about land - it is about the very survival of Muslim civilization in the 
            subcontinent. The two-nation theory is not a political slogan; it is a 
            fundamental truth that has been proven throughout history.
            
            Muslims and Hindus are not just different religious communities - we are 
            separate nations with distinct cultures, traditions, and aspirations. 
            No amount of constitutional safeguards can protect Muslim interests in 
            a Hindu-majority state.
            
            The areas where Muslims are in majority must form Pakistan. This is not 
            a demand - it is a necessity. Without a separate homeland, Muslim culture, 
            language, and way of life will be gradually eroded and eventually destroyed.
            
            I am willing to discuss the details of partition, but the principle of 
            Pakistan is non-negotiable. The Muslim League will not accept anything less."""
        elif topic == "race_relations":
            out = f"""My respected {opponents_str}, the issue is not about race 
            or color - it is about the fundamental differences between Muslim and 
            Hindu civilizations. We are not inferior or superior to each other; 
            we are simply different.
            
            Muslims have their own history, their own heroes, their own way of life. 
            We cannot be expected to merge into a Hindu-dominated society where our 
            values and traditions will be gradually diluted.
            
            The Congress talks of unity, but what they really mean is assimilation. 
            They want Muslims to give up their distinct identity and become second-class 
            citizens in a Hindu state. This we cannot and will not accept.
            
            Let us be honest: Hindus and Muslims can live as good neighbors, but 
            we cannot live as one nation. The sooner we accept this reality, the 
            sooner we can work towards a peaceful separation."""
        elif topic == "economic_policy":
            out = f"""My dear {opponents_str}, Pakistan must be economically 
            self-sufficient and guided by Islamic principles. We cannot depend on 
            others for our survival and prosperity.
            
            The new state will promote Islamic banking, encourage Muslim entrepreneurship, 
            and ensure that economic development benefits all citizens regardless of 
            their background. We will build industries, develop agriculture, and 
            create opportunities for our people.
            
            However, economic development must go hand in hand with social justice. 
            The Islamic principles of equality, brotherhood, and compassion will 
            guide our economic policies.
            
            We are willing to trade with other nations, but we will not compromise 
            our independence or our values for economic gain."""
        else:
            out = f"""My respected {opponents_str}, I have always believed in 
            constitutional methods and democratic processes. The Muslim League has 
            won the support of the Muslim masses through peaceful political mobilization.
            
            We are not asking for anything unreasonable. We are simply asking for 
            the right to live as a free people in our own homeland. This is the 
            natural right of every nation.
            
            I am willing to negotiate the terms of partition, but I will not compromise 
            on the fundamental principle of Pakistan. The Muslim masses have spoken, 
            and their voice must be heard.
            
            Let us work together to ensure a peaceful and orderly transition. The 
            future of both India and Pakistan depends on our ability to resolve 
            this issue amicably."""
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
