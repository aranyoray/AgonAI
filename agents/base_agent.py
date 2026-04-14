"""
Base class for historical figure AI agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import random

from scoring.policy_scoring import (
    OCEANTraits,
    PolicyScores,
    AgentScorecard,
    score_proposal,
    compute_objective,
    apply_empathy_multiplier,
    apply_fatigue_penalty,
    compute_penalty,
    RegionWeights,
    REGION_WEIGHTS,
)


class Ideology(Enum):
    FASCISM = "fascism"
    COMMUNISM = "communism"
    CAPITALISM = "capitalism"
    NONVIOLENCE = "nonviolence"
    MUSLIM_NATIONALISM = "muslim_nationalism"
    DEMOCRACY = "democracy"
    AUTHORITARIANISM = "authoritarianism"
    LIBERALISM = "liberalism"
    CONSERVATISM = "conservatism"


@dataclass
class PersonalityTraits:
    """Core personality traits that define a historical figure's behavior."""
    assertiveness: float  # 0.0 to 1.0
    cooperativeness: float  # 0.0 to 1.0
    openness_to_change: float  # 0.0 to 1.0
    emotional_stability: float  # 0.0 to 1.0
    dominance: float  # 0.0 to 1.0
    charisma: float  # 0.0 to 1.0
    pragmatism: float  # 0.0 to 1.0
    idealism: float  # 0.0 to 1.0

    def to_ocean(self) -> OCEANTraits:
        """Map internal personality traits to Big Five (OCEAN) traits."""
        return OCEANTraits(
            openness=self.openness_to_change,
            conscientiousness=(self.pragmatism + self.emotional_stability) / 2,
            extraversion=(self.assertiveness + self.charisma) / 2,
            agreeableness=self.cooperativeness,
            neuroticism=1.0 - self.emotional_stability,
        )


@dataclass
class HistoricalContext:
    """Historical context that influences the agent's decisions."""
    time_period: str
    major_events: List[str]
    cultural_background: str
    education: str
    key_relationships: List[str]
    defining_moments: List[str]


class HistoricalAgent(ABC):
    """
    Base class for AI agents representing historical political figures.
    """
    
    def __init__(
        self,
        name: str,
        ideology: Ideology,
        personality: PersonalityTraits,
        context: HistoricalContext,
        llm_client: Any = None,
        memory_client: Any = None,
        ocean_override: Optional[OCEANTraits] = None,
        empathy_ratio: Optional[float] = None,
        region_weights: Optional[RegionWeights] = None,
    ):
        self.name = name
        self.ideology = ideology
        self.personality = personality
        self.context = context
        self.llm_client = llm_client
        self.memory_client = memory_client
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_position: Dict[str, Any] = {}
        self.red_lines: List[str] = []  # Non-negotiable positions

        # OCEAN personality (derived from traits or overridden)
        self.ocean: OCEANTraits = ocean_override or personality.to_ocean()
        # Empathy ratio: how much the agent factors opponent's objective (0=selfish, 1=altruistic)
        self.empathy_ratio: float = empathy_ratio if empathy_ratio is not None else self.ocean.empathy_score()
        # Fatigue accumulates over rounds
        self.fatigue: float = 0.0
        # Region-specific objective weights
        self.region_weights: RegionWeights = region_weights or REGION_WEIGHTS["default"]
        # Scorecard tracks all policy scores across the debate
        self.scorecard: AgentScorecard = AgentScorecard(agent_name=name)
        # Personality multiplier derived from historical character traits
        self.personality_multiplier: float = 1.0
        
    @abstractmethod
    def generate_response(
        self, 
        topic: str, 
        other_agents: List['HistoricalAgent'],
        debate_context: Dict[str, Any]
    ) -> str:
        """
        Generate a response based on the agent's personality and historical context.
        """
        pass
    
    @abstractmethod
    def evaluate_proposal(
        self, 
        proposal: str, 
        proposer: 'HistoricalAgent'
    ) -> Dict[str, Any]:
        """
        Evaluate a proposal from another agent.
        Returns: {'accept': bool, 'reasoning': str, 'counter_proposal': str}
        """
        pass
    
    def update_position(self, new_position: Dict[str, Any]) -> None:
        """Update the agent's current position on the topic."""
        self.current_position.update(new_position)
    
    def add_to_history(self, speaker: str, content: str, context: Dict[str, Any]) -> None:
        """Add an interaction to the conversation history."""
        self.conversation_history.append({
            'speaker': speaker,
            'content': content,
            'context': context,
            'timestamp': len(self.conversation_history)
        })
        if self.memory_client:
            self.memory_client.record_event(
                agent_name=self.name,
                speaker=speaker,
                content=content,
                metadata=context,
            )
    
    def get_personality_prompt(self) -> str:
        """Generate a personality prompt for the LLM."""
        return f"""You are {self.name}, a historical figure.

Ideology: {self.ideology.value}
Time Period: {self.context.time_period}
Cultural Background: {self.context.cultural_background}

Key Traits: assertiveness={self.personality.assertiveness}, cooperativeness={self.personality.cooperativeness}, openness={self.personality.openness_to_change}, dominance={self.personality.dominance}, pragmatism={self.personality.pragmatism}

Red Lines: {', '.join(self.red_lines) if self.red_lines else 'None specified'}

RESPONSE RULES:
- Keep responses to 2-3 sentences maximum. Be punchy and direct.
- You MUST reference or rebut a specific point from the previous speaker. Quote or paraphrase them.
- In later rounds, actively seek common ground. Propose concrete compromises where possible.
- Never repeat what you said in an earlier round. Build on the conversation.
- Stay in character but be conversational, not speechifying.
"""

    def get_memory_summary(self) -> str:
        """Provide a short memory summary for this agent."""
        if not self.memory_client:
            return "Memory service not configured."
        return self.memory_client.summarize_recent(self.name)

    def memory_footer(self, debate_context: Dict[str, Any]) -> str:
        """Memory footer is no longer appended to debate output."""
        return ""

    def generate_llm_response(self, topic: str, debate_context: Dict[str, Any]) -> Optional[str]:
        """Generate a response using the LLM. Always attempts if llm_client is set."""
        if not self.llm_client:
            return None

        round_num = len(self.conversation_history)

        # Build conversation transcript from history (last 6 turns)
        transcript_lines = []
        for entry in self.conversation_history[-6:]:
            speaker = entry.get("speaker", "?")
            content = entry.get("content", "")
            if len(content) > 200:
                content = content[:197].rstrip() + "..."
            transcript_lines.append(f"{speaker}: {content}")
        transcript = "\n".join(transcript_lines) if transcript_lines else "(This is the opening statement.)"

        # Round-aware directive
        if round_num < 2:
            round_directive = "This is an early round. State your position clearly and distinctly."
        elif round_num < 5:
            round_directive = (
                "Mid-debate. You MUST reference or rebut a specific point the previous speaker made. "
                "Acknowledge any valid points before disagreeing."
            )
        else:
            round_directive = (
                "Late in the debate. Actively seek common ground. Propose a specific compromise or concession. "
                "Reference what has been discussed and identify areas of partial agreement."
            )

        system = (
            f"You are {self.name}, speaking in a multi-party debate.\n"
            f"Your ideology: {self.ideology.value}. "
            f"Key traits: cooperativeness={self.personality.cooperativeness}, "
            f"assertiveness={self.personality.assertiveness}, "
            f"pragmatism={self.personality.pragmatism}, "
            f"dominance={self.personality.dominance}.\n"
            f"Red lines (non-negotiable): {', '.join(self.red_lines) if self.red_lines else 'none'}.\n\n"
            "STRICT RULES:\n"
            "- Respond in 2-3 sentences MAXIMUM. Be punchy and direct, not speechifying.\n"
            "- Stay fully in character with your historical personality and speaking style.\n"
            "- Never repeat something you already said in a previous round.\n"
            f"- {round_directive}\n"
        )

        prompt = (
            f"Debate topic: {topic}\n\n"
            f"Conversation so far:\n{transcript}\n\n"
            f"Now respond as {self.name} in 2-3 sentences. "
            "Directly engage with what the previous speaker said."
        )

        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system=system,
                options={"temperature": 0.9, "max_tokens": 200},
            )
        except Exception:
            return None

        if not response or not response.strip():
            return None

        state = debate_context.get("conversation_state")
        if state and state.is_repetitive(response, role=self.name):
            response = (
                f"{response}\n\nLet me advance the discussion: "
                f"I propose one concrete action to move forward on {topic}."
            )
        return response.strip()

    def _get_last_opponent_summary(self) -> str:
        """Extract a short summary of the last opponent's statement from history."""
        for entry in reversed(self.conversation_history):
            if entry.get("speaker") != self.name:
                content = entry.get("content", "")
                if len(content) > 150:
                    return content[:147].rstrip() + "..."
                return content
        return ""

    # ============== Policy scoring helpers ==============
    def score_round(
        self,
        topic: str,
        round_number: int,
        max_rounds: int = 20,
        opponent_objective: float = 0.0,
        violated_red_lines: int = 0,
        low_cooperation_rounds: int = 0,
        repeated_positions: int = 0,
    ) -> float:
        """Score this agent's position for the current round.

        Returns the empathy-adjusted objective value for the round.
        """
        # Compute policy scores
        scores = score_proposal(
            topic=topic,
            agent_ideology=self.ideology.value,
            personality_modifier=self.ocean.personality_modifier(),
            cooperation_level=self.personality.cooperativeness,
        )

        # Apply personality multiplier (famous-character bonus)
        scores.political.benefit *= self.personality_multiplier
        scores.economic.benefit *= self.personality_multiplier
        scores.social.benefit *= self.personality_multiplier

        # Fatigue
        self.fatigue = apply_fatigue_penalty(
            base_fatigue=self.fatigue,
            round_number=round_number,
            emotional_stability=self.personality.emotional_stability,
            max_rounds=max_rounds,
        )

        # Penalty for bad behavior
        penalty = compute_penalty(
            violated_red_lines=violated_red_lines,
            low_cooperation_rounds=low_cooperation_rounds,
            repeated_positions=repeated_positions,
        )

        # Raw objective
        raw_obj = compute_objective(
            scores=scores,
            weights=self.region_weights,
            fatigue=self.fatigue,
            penalty=penalty,
        )

        # Empathy-adjusted objective
        adjusted = apply_empathy_multiplier(raw_obj, opponent_objective, self.empathy_ratio)

        # Record
        self.scorecard.rounds_played += 1
        self.scorecard.round_scores.append(scores)
        self.scorecard.objective_values.append(adjusted)
        self.scorecard.fatigue = self.fatigue
        self.scorecard.penalties += penalty
        self.scorecard.empathy_bonus += adjusted - raw_obj

        # Update cumulative
        cs = self.scorecard.cumulative_scores
        cs.political.benefit = min(100, cs.political.benefit + scores.political.benefit / max_rounds)
        cs.political.cost = min(100, cs.political.cost + scores.political.cost / max_rounds)
        cs.economic.benefit = min(100, cs.economic.benefit + scores.economic.benefit / max_rounds)
        cs.economic.cost = min(100, cs.economic.cost + scores.economic.cost / max_rounds)
        cs.social.benefit = min(100, cs.social.benefit + scores.social.benefit / max_rounds)
        cs.social.cost = min(100, cs.social.cost + scores.social.cost / max_rounds)

        return adjusted

    def get_empathy_ratio(self) -> float:
        return self.empathy_ratio

    def set_empathy_ratio(self, ratio: float) -> None:
        self.empathy_ratio = max(0.0, min(1.0, ratio))

    def inject_empathy(self, boost: float) -> None:
        """Increase empathy (for experimental empathy injection)."""
        self.empathy_ratio = min(1.0, self.empathy_ratio + boost)
        self.ocean.agreeableness = min(1.0, self.ocean.agreeableness + boost * 0.5)

    # ============== Compromise helpers ==============
    def willingness_to_compromise(self) -> float:
        """Score 0..1: higher when cooperative, open, pragmatic, stable, and not overly dominant/assertive."""
        positive = (
            self.personality.cooperativeness * 0.35
            + self.personality.openness_to_change * 0.25
            + self.personality.pragmatism * 0.25
            + self.personality.emotional_stability * 0.15
        )
        negative = (
            self.personality.assertiveness * 0.20
            + self.personality.dominance * 0.20
        )
        score = max(0.0, min(1.0, positive - negative * 0.5))
        return score

    def pick_response(self, pool: list, opponents_str: str) -> str:
        """Pick a random response from the pool, add a rebuttal prefix referencing the last opponent."""
        # Randomize selection instead of deterministic round-based cycling
        out = random.choice(pool).format(opponents=opponents_str)

        # Shorten: take only first 2-3 sentences
        sentences = [s.strip() for s in out.replace("! ", "!|").replace(". ", ".|").replace("? ", "?|").split("|") if s.strip()]
        if len(sentences) > 3:
            out = " ".join(sentences[:3])
            if not out.endswith((".", "!", "?")):
                out += "."

        # Prepend a reference to the last opponent's point
        last_point = self._get_last_opponent_summary()
        if last_point:
            last_speaker = ""
            for entry in reversed(self.conversation_history):
                if entry.get("speaker") != self.name:
                    last_speaker = entry.get("speaker", "")
                    break
            # Pick a rebuttal style at random for variety
            rebuttal_styles = [
                f"{last_speaker} argues \"{last_point[:80]}...\" — but I must respond:",
                f"I have heard {last_speaker}'s point about {last_point[:60]}... Let me say this:",
                f"Responding to {last_speaker}: ",
                f"{last_speaker}, you raise the matter of {last_point[:60]}... However,",
                f"To {last_speaker}'s argument — ",
            ]
            prefix = random.choice(rebuttal_styles)
            out = f"{prefix} {out}"

        return out

    def _consensus_suffix(self, round_num: int) -> str:
        """Return a consensus-building suffix for later rounds."""
        if round_num < 3:
            return ""
        w = self.willingness_to_compromise()
        if round_num >= 6 or w >= 0.6:
            options = [
                " Perhaps we can find a middle path here.",
                " I am willing to consider a compromise on this point.",
                " Let us identify what we agree on and build from there.",
                " Can we agree on at least this much?",
                " I propose we each make one concession.",
            ]
            return random.choice(options)
        if round_num >= 3:
            options = [
                " I note some common ground between us.",
                " There may be room for agreement here.",
            ]
            return random.choice(options)
        return ""

    def compromise_note(self) -> str:
        """Human-readable note appended to responses when agent is inclined to compromise."""
        w = self.willingness_to_compromise()
        if w >= 0.7:
            return "\n\nI am prepared to explore meaningful concessions if they respect core principles."
        if w >= 0.45:
            return "\n\nI am open to limited adjustments that serve the broader good."
        return ""

    def evaluate_proposal_generically(self, proposal: str, proposer: 'HistoricalAgent') -> Dict[str, Any]:
        """Generic evaluation using personality-based willingness and red lines."""
        text = proposal.lower()
        # Red lines block
        for red in self.red_lines:
            if red.lower() in text:
                return {
                    'accept': False,
                    'reasoning': f"Violates red line: {red}",
                    'counter_proposal': "Identify alternatives that avoid breaching fundamental principles"
                }
        # Ideological distance discount
        ideological = self.calculate_consensus_score(proposer)
        willingness = self.willingness_to_compromise()
        blended = (ideological * 0.5) + (willingness * 0.5)
        if blended >= 0.7:
            return {
                'accept': True,
                'reasoning': 'Compatible with my worldview and acceptable with minor edits',
                'counter_proposal': 'I accept in principle; propose clarifying safeguards for implementation'
            }
        if blended >= 0.45:
            return {
                'accept': True,
                'reasoning': 'Partially aligned; acceptable with conditions',
                'counter_proposal': 'I propose a phased approach with verifiable milestones and mutual guarantees'
            }
        return {
            'accept': False,
            'reasoning': 'Insufficient alignment given my principles and constraints',
            'counter_proposal': 'Consider narrowing scope or introducing confidence-building measures'
        }

    def calculate_consensus_score(self, other_agent: 'HistoricalAgent') -> float:
        """
        Calculate how likely this agent is to reach consensus with another agent.
        Returns a score between 0.0 (no consensus possible) and 1.0 (perfect alignment).
        """
        # Base compatibility on ideology similarity
        ideology_compatibility = self._calculate_ideology_compatibility(other_agent.ideology)
        
        # Factor in personality traits
        personality_compatibility = self._calculate_personality_compatibility(other_agent.personality)
        
        # Consider historical context compatibility
        context_compatibility = self._calculate_context_compatibility(other_agent.context)
        
        # Weighted average
        consensus_score = (
            ideology_compatibility * 0.4 +
            personality_compatibility * 0.3 +
            context_compatibility * 0.3
        )
        
        return min(1.0, max(0.0, consensus_score))
    
    def _calculate_ideology_compatibility(self, other_ideology: Ideology) -> float:
        """Calculate ideological compatibility between agents."""
        # Define ideology compatibility matrix
        compatibility_matrix = {
            Ideology.FASCISM: {
                Ideology.FASCISM: 1.0, Ideology.AUTHORITARIANISM: 0.7, Ideology.CONSERVATISM: 0.5,
                Ideology.COMMUNISM: 0.2, Ideology.DEMOCRACY: 0.1, Ideology.LIBERALISM: 0.1,
                Ideology.NONVIOLENCE: 0.0, Ideology.MUSLIM_NATIONALISM: 0.3, Ideology.CAPITALISM: 0.4
            },
            Ideology.COMMUNISM: {
                Ideology.COMMUNISM: 1.0, Ideology.AUTHORITARIANISM: 0.6, Ideology.LIBERALISM: 0.3,
                Ideology.DEMOCRACY: 0.2, Ideology.CONSERVATISM: 0.2, Ideology.FASCISM: 0.2,
                Ideology.NONVIOLENCE: 0.1, Ideology.MUSLIM_NATIONALISM: 0.2, Ideology.CAPITALISM: 0.1
            },
            Ideology.DEMOCRACY: {
                Ideology.DEMOCRACY: 1.0, Ideology.LIBERALISM: 0.8, Ideology.CONSERVATISM: 0.6,
                Ideology.NONVIOLENCE: 0.7, Ideology.COMMUNISM: 0.2, Ideology.AUTHORITARIANISM: 0.1,
                Ideology.FASCISM: 0.1, Ideology.MUSLIM_NATIONALISM: 0.3, Ideology.CAPITALISM: 0.7
            },
            Ideology.NONVIOLENCE: {
                Ideology.NONVIOLENCE: 1.0, Ideology.DEMOCRACY: 0.7, Ideology.LIBERALISM: 0.6,
                Ideology.CONSERVATISM: 0.4, Ideology.COMMUNISM: 0.1, Ideology.AUTHORITARIANISM: 0.0,
                Ideology.FASCISM: 0.0, Ideology.MUSLIM_NATIONALISM: 0.3, Ideology.CAPITALISM: 0.5
            },
            Ideology.MUSLIM_NATIONALISM: {
                Ideology.MUSLIM_NATIONALISM: 1.0, Ideology.CONSERVATISM: 0.5, Ideology.AUTHORITARIANISM: 0.4,
                Ideology.DEMOCRACY: 0.3, Ideology.LIBERALISM: 0.2, Ideology.COMMUNISM: 0.2,
                Ideology.FASCISM: 0.1, Ideology.NONVIOLENCE: 0.3, Ideology.CAPITALISM: 0.4
            },
            Ideology.AUTHORITARIANISM: {
                Ideology.AUTHORITARIANISM: 1.0, Ideology.FASCISM: 0.7, Ideology.COMMUNISM: 0.6,
                Ideology.CONSERVATISM: 0.6, Ideology.MUSLIM_NATIONALISM: 0.4, Ideology.DEMOCRACY: 0.1,
                Ideology.LIBERALISM: 0.1, Ideology.NONVIOLENCE: 0.0, Ideology.CAPITALISM: 0.3
            },
            Ideology.CONSERVATISM: {
                Ideology.CONSERVATISM: 1.0, Ideology.AUTHORITARIANISM: 0.6, Ideology.DEMOCRACY: 0.6,
                Ideology.FASCISM: 0.5, Ideology.MUSLIM_NATIONALISM: 0.5, Ideology.CAPITALISM: 0.7,
                Ideology.LIBERALISM: 0.5, Ideology.NONVIOLENCE: 0.4, Ideology.COMMUNISM: 0.2
            },
            Ideology.LIBERALISM: {
                Ideology.LIBERALISM: 1.0, Ideology.DEMOCRACY: 0.8, Ideology.NONVIOLENCE: 0.6,
                Ideology.CONSERVATISM: 0.5, Ideology.CAPITALISM: 0.8, Ideology.COMMUNISM: 0.3,
                Ideology.MUSLIM_NATIONALISM: 0.2, Ideology.AUTHORITARIANISM: 0.1, Ideology.FASCISM: 0.1
            },
            Ideology.CAPITALISM: {
                Ideology.CAPITALISM: 1.0, Ideology.LIBERALISM: 0.8, Ideology.DEMOCRACY: 0.7,
                Ideology.CONSERVATISM: 0.7, Ideology.NONVIOLENCE: 0.5, Ideology.MUSLIM_NATIONALISM: 0.4,
                Ideology.FASCISM: 0.4, Ideology.AUTHORITARIANISM: 0.3, Ideology.COMMUNISM: 0.1
            },
        }
        
        return compatibility_matrix.get(self.ideology, {}).get(other_ideology, 0.5)
    
    def _calculate_personality_compatibility(self, other_personality: PersonalityTraits) -> float:
        """Calculate personality compatibility between agents."""
        # Calculate differences in key personality traits
        assertiveness_diff = abs(self.personality.assertiveness - other_personality.assertiveness)
        cooperativeness_diff = abs(self.personality.cooperativeness - other_personality.cooperativeness)
        openness_diff = abs(self.personality.openness_to_change - other_personality.openness_to_change)
        
        # Lower differences = higher compatibility
        avg_diff = (assertiveness_diff + cooperativeness_diff + openness_diff) / 3
        return 1.0 - avg_diff
    
    def _calculate_context_compatibility(self, other_context: HistoricalContext) -> float:
        """Calculate historical context compatibility between agents."""
        # Same time period = higher compatibility
        time_compatibility = 1.0 if self.context.time_period == other_context.time_period else 0.5
        
        # Shared cultural background = higher compatibility
        cultural_compatibility = 1.0 if self.context.cultural_background == other_context.cultural_background else 0.3
        
        # Shared major events = higher compatibility
        shared_events = set(self.context.major_events) & set(other_context.major_events)
        event_compatibility = len(shared_events) / max(len(self.context.major_events), len(other_context.major_events), 1)
        
        return (time_compatibility + cultural_compatibility + event_compatibility) / 3
