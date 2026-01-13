"""
Factory system for creating custom political agents.
"""

from typing import Dict, List, Any, Optional
from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology


class GenericAgent(HistoricalAgent):
    """
    A generic agent implementation that can be configured for any historical figure.
    Allows dynamic creation of new political agents.
    """
    
    def __init__(
        self,
        name: str,
        ideology: Ideology,
        personality: PersonalityTraits,
        context: HistoricalContext,
        speaking_style: str = "formal",
        response_templates: Optional[Dict[str, str]] = None,
        red_lines: Optional[List[str]] = None,
        llm_client: Any = None
    ):
        super().__init__(name, ideology, personality, context, llm_client)
        self.speaking_style = speaking_style
        self.response_templates = response_templates or {}
        self.red_lines = red_lines or []
        
    def generate_response(
        self, 
        topic: str, 
        other_agents: List[HistoricalAgent],
        debate_context: Dict[str, Any]
    ) -> str:
        """Generate a response based on the agent's configuration."""
        
        opponent_names = [agent.name for agent in other_agents if agent.name != self.name]
        opponents_str = ", ".join(opponent_names) if opponent_names else "my colleagues"
        
        # Use custom template if available
        if topic in self.response_templates:
            template = self.response_templates[topic]
            return template.format(opponents=opponents_str, name=self.name)
        
        # Generate default response based on personality
        return self._generate_default_response(topic, opponents_str)
    
    def evaluate_proposal(self, proposal: str, proposer: HistoricalAgent) -> Dict[str, Any]:
        """Evaluate a proposal from another agent."""
        
        # Check red lines first
        for red_line in self.red_lines:
            if red_line.lower() in proposal.lower():
                return {
                    'accept': False,
                    'reasoning': f'This proposal violates my fundamental principle: {red_line}',
                    'counter_proposal': f'I cannot accept this as it conflicts with my non-negotiable position on {red_line}'
                }
        
        # Check ideology compatibility
        compatibility = self.calculate_consensus_score(proposer)
        
        if compatibility >= 0.6:
            return {
                'accept': True,
                'reasoning': 'The proposal aligns with my worldview and ideology',
                'counter_proposal': 'Let me enhance this proposal by adding my perspective'
            }
        elif compatibility >= 0.3:
            return {
                'accept': True,
                'reasoning': 'The proposal has merit, though it differs from my preferred approach',
                'counter_proposal': 'I could accept this with some modifications'
            }
        else:
            return {
                'accept': False,
                'reasoning': 'The proposal is incompatible with my fundamental beliefs',
                'counter_proposal': 'I propose a fundamentally different approach'
            }
    
    def _generate_default_response(self, topic: str, opponents: str) -> str:
        """Generate a default response based on personality traits."""
        
        # Determine tone based on personality
        if self.personality.assertiveness > 0.8:
            opening = f"I, {self.name}, declare emphatically that"
        elif self.personality.assertiveness > 0.5:
            opening = f"My position, {opponents}, is clear:"
        else:
            opening = f"With respect to {opponents}, I believe that"
        
        # Determine cooperativeness
        if self.personality.cooperativeness > 0.7:
            cooperation = "We must find common ground and work together."
        elif self.personality.cooperativeness > 0.4:
            cooperation = "I am willing to discuss this matter."
        else:
            cooperation = "My position on this matter is firm."
        
        # Determine pragmatism vs idealism
        if self.personality.idealism > self.personality.pragmatism:
            approach = "We must stand firm on our principles and values."
        else:
            approach = "We must find practical solutions that serve our interests."
        
        return f"""{opening} regarding {topic}, {cooperation} {approach}

This position aligns with my {self.ideology.value} ideology and reflects the 
historical context of {self.context.time_period}. My perspective is shaped by 
{self.context.cultural_background} and my experiences with {', '.join(self.context.major_events[:2])}.

{opponents}, I invite you to consider how we might navigate these differences while 
remaining true to our respective principles."""


def create_agent(
    name: str,
    ideology: str,
    personality_traits: Dict[str, float],
    time_period: str,
    major_events: List[str],
    cultural_background: str,
    education: str = "",
    key_relationships: List[str] = None,
    defining_moments: List[str] = None,
    red_lines: List[str] = None,
    speaking_style: str = "formal",
    response_templates: Dict[str, str] = None
) -> HistoricalAgent:
    """
    Factory function to create a new political agent.
    
    Args:
        name: Name of the historical figure
        ideology: Political ideology (fascism, communism, democracy, etc.)
        personality_traits: Dictionary of personality trait scores (0.0-1.0)
        time_period: Historical time period
        major_events: List of major historical events
        cultural_background: Cultural and ethnic background
        education: Educational background
        key_relationships: Important relationships
        defining_moments: Key defining moments in their life
        red_lines: Non-negotiable positions
        speaking_style: Communication style (formal, informal, etc.)
        response_templates: Custom response templates for specific topics
    
    Returns:
        A configured HistoricalAgent instance
    
    Example:
        >>> agent = create_agent(
        ...     name="Winston Churchill",
        ...     ideology="democracy",
        ...     personality_traits={
        ...         "assertiveness": 0.85,
        ...         "cooperativeness": 0.5,
        ...         "openness_to_change": 0.4,
        ...         "emotional_stability": 0.7,
        ...         "dominance": 0.8,
        ...         "charisma": 0.9,
        ...         "pragmatism": 0.8,
        ...         "idealism": 0.7
        ...     },
        ...     time_period="1940s",
        ...     major_events=["World War II", "Battle of Britain", "Nazi Germany"],
        ...     cultural_background="British, aristocratic"
        ... )
    """
    
    # Convert ideology string to enum
    ideology_map = {
        "fascism": Ideology.FASCISM,
        "communism": Ideology.COMMUNISM,
        "capitalism": Ideology.CAPITALISM,
        "nonviolence": Ideology.NONVIOLENCE,
        "muslim_nationalism": Ideology.MUSLIM_NATIONALISM,
        "democracy": Ideology.DEMOCRACY,
        "authoritarianism": Ideology.AUTHORITARIANISM,
        "liberalism": Ideology.LIBERALISM,
        "conservatism": Ideology.CONSERVATISM
    }
    
    ideology_enum = ideology_map.get(ideology.lower(), Ideology.DEMOCRACY)
    
    # Create personality traits
    personality = PersonalityTraits(
        assertiveness=personality_traits.get("assertiveness", 0.5),
        cooperativeness=personality_traits.get("cooperativeness", 0.5),
        openness_to_change=personality_traits.get("openness_to_change", 0.5),
        emotional_stability=personality_traits.get("emotional_stability", 0.5),
        dominance=personality_traits.get("dominance", 0.5),
        charisma=personality_traits.get("charisma", 0.5),
        pragmatism=personality_traits.get("pragmatism", 0.5),
        idealism=personality_traits.get("idealism", 0.5)
    )
    
    # Create historical context
    context = HistoricalContext(
        time_period=time_period,
        major_events=major_events or [],
        cultural_background=cultural_background,
        education=education,
        key_relationships=key_relationships or [],
        defining_moments=defining_moments or []
    )
    
    # Create and return the agent
    agent = GenericAgent(
        name=name,
        ideology=ideology_enum,
        personality=personality,
        context=context,
        speaking_style=speaking_style,
        response_templates=response_templates,
        red_lines=red_lines,
        llm_client=None
    )
    
    return agent


def load_agent_from_config(config: Dict[str, Any]) -> HistoricalAgent:
    """
    Load an agent from a configuration dictionary.
    
    Args:
        config: Dictionary containing agent configuration
    
    Returns:
        A configured HistoricalAgent instance
    
    Example:
        >>> config = {
        ...     "name": "Winston Churchill",
        ...     "ideology": "democracy",
        ...     "personality": {"assertiveness": 0.85, ...},
        ...     "context": {"time_period": "1940s", ...}
        ... }
        >>> agent = load_agent_from_config(config)
    """
    
    return create_agent(
        name=config.get("name", "Unknown"),
        ideology=config.get("ideology", "democracy"),
        personality_traits=config.get("personality", {}),
        time_period=config.get("context", {}).get("time_period", ""),
        major_events=config.get("context", {}).get("major_events", []),
        cultural_background=config.get("context", {}).get("cultural_background", ""),
        education=config.get("context", {}).get("education", ""),
        key_relationships=config.get("context", {}).get("key_relationships", []),
        defining_moments=config.get("context", {}).get("defining_moments", []),
        red_lines=config.get("red_lines", []),
        speaking_style=config.get("speaking_style", "formal"),
        response_templates=config.get("response_templates", {})
    )
