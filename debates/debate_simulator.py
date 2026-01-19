"""
Debate simulation system for historical figure AI agents.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime

from agents.base_agent import HistoricalAgent
from utils.conversation_state import ConversationState, plan_response


class DebateStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CONCLUDED = "concluded"
    CONSENSUS_REACHED = "consensus_reached"
    DEADLOCK = "deadlock"


@dataclass
class DebateRound:
    """Represents a single round of debate."""
    round_number: int
    speaker: str
    topic: str
    response: str
    timestamp: datetime
    context: Dict[str, Any]


@dataclass
class DebateResult:
    """Result of a debate simulation."""
    status: DebateStatus
    rounds: List[DebateRound]
    consensus_score: float
    key_agreements: List[str]
    key_disagreements: List[str]
    final_positions: Dict[str, Dict[str, Any]]
    duration_minutes: float
    majority_vote: Dict[str, Any]
    final_resolution: Optional[Dict[str, Any]]


class DebateSimulator:
    """
    Simulates debates between historical figure AI agents.
    """
    
    def __init__(self, max_rounds: int = 20, consensus_threshold: float = 0.8, memory_window: int = 8):
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold
        self.memory_window = memory_window
        self.debate_history: List[DebateRound] = []
        self.conversation_state: Optional[ConversationState] = None
        
    def debate(
        self, 
        agents: List[HistoricalAgent], 
        topic: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> DebateResult:
        """
        Simulate a debate between agents on a given topic.
        """
        if len(agents) < 2:
            raise ValueError("At least 2 agents are required for a debate")
        
        start_time = time.time()
        self.debate_history = []
        current_context = initial_context or {}
        self.conversation_state = current_context.get("conversation_state")
        
        # Initialize positions
        for agent in agents:
            agent.current_position = agent.current_position.copy()
        
        # Debate loop
        if self.conversation_state and not self.conversation_state.turns:
            self.conversation_state.append_turn("system", f"Debate topic: {topic}")
            self.conversation_state.update_summary()
            self.conversation_state.extract_salience_and_open_loops()
            self.conversation_state.update_metrics()
        for round_num in range(self.max_rounds):
            # Determine current speaker (rotate through agents)
            current_speaker = agents[round_num % len(agents)]

            if self.conversation_state:
                current_context["conversation_context"] = self.conversation_state.build_prompt_context()
                current_context["response_plan"] = plan_response(
                    self.conversation_state,
                    last_user_message=None,
                ).__dict__
                current_context["conversation_state"] = self.conversation_state

            current_context["memory_summary"] = current_speaker.get_memory_summary()
            current_context["shared_memory"] = self._get_shared_memory_summary()
            
            # Generate response
            response = current_speaker.generate_response(
                topic=topic,
                other_agents=[a for a in agents if a.name != current_speaker.name],
                debate_context=current_context
            )

            current_speaker.update_position({topic: response})
            
            # Record the round
            round_data = DebateRound(
                round_number=round_num + 1,
                speaker=current_speaker.name,
                topic=topic,
                response=response,
                timestamp=datetime.now(),
                context=current_context.copy()
            )
            self.debate_history.append(round_data)
            
            # Add to conversation history
            for agent in agents:
                agent.add_to_history(
                    speaker=current_speaker.name,
                    content=response,
                    context=current_context
                )
            if self.conversation_state:
                self.conversation_state.append_turn(current_speaker.name, response)
                self.conversation_state.update_summary()
                self.conversation_state.extract_salience_and_open_loops()
                self.conversation_state.update_metrics()
            
            # Check for consensus
            consensus_score = self._calculate_consensus_score(agents)
            if consensus_score >= self.consensus_threshold:
                duration = (time.time() - start_time) / 60
                return self._create_result(
                    status=DebateStatus.CONSENSUS_REACHED,
                    agents=agents,
                    consensus_score=consensus_score,
                    duration=duration
                )
            
            # Check for deadlock (no progress in recent rounds)
            if self._is_deadlock():
                duration = (time.time() - start_time) / 60
                return self._create_result(
                    status=DebateStatus.DEADLOCK,
                    agents=agents,
                    consensus_score=consensus_score,
                    duration=duration
                )
            
            # Update context for next round
            current_context.update({
                f"round_{round_num + 1}_response": response,
                f"round_{round_num + 1}_speaker": current_speaker.name
            })
        
        # Debate concluded without consensus
        duration = (time.time() - start_time) / 60
        final_consensus_score = self._calculate_consensus_score(agents)
        
        return self._create_result(
            status=DebateStatus.CONCLUDED,
            agents=agents,
            consensus_score=final_consensus_score,
            duration=duration
        )
    
    def _calculate_consensus_score(self, agents: List[HistoricalAgent]) -> float:
        """Calculate overall consensus score between all agents."""
        if len(agents) < 2:
            return 1.0
        
        total_score = 0.0
        pair_count = 0
        
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                score = agent1.calculate_consensus_score(agent2)
                total_score += score
                pair_count += 1
        
        return total_score / pair_count if pair_count > 0 else 0.0
    
    def _is_deadlock(self, lookback_rounds: int = 5) -> bool:
        """Check if the debate has reached a deadlock."""
        if len(self.debate_history) < lookback_rounds:
            return False
        
        # Simple deadlock detection: if the same points are being repeated
        recent_responses = [round_data.response for round_data in self.debate_history[-lookback_rounds:]]
        
        # Check for repetitive content (simplified)
        unique_responses = set(recent_responses)
        return len(unique_responses) <= 2  # If only 2 or fewer unique responses in last 5 rounds
    
    def _create_result(
        self, 
        status: DebateStatus, 
        agents: List[HistoricalAgent], 
        consensus_score: float,
        duration: float
    ) -> DebateResult:
        """Create a debate result object."""
        
        # Extract key agreements and disagreements
        agreements, disagreements = self._analyze_positions(agents)
        
        # Get final positions
        final_positions = {
            agent.name: agent.current_position for agent in agents
        }
        majority_vote, final_resolution = self._conduct_majority_vote(agents)
        
        return DebateResult(
            status=status,
            rounds=self.debate_history.copy(),
            consensus_score=consensus_score,
            key_agreements=agreements,
            key_disagreements=disagreements,
            final_positions=final_positions,
            duration_minutes=duration,
            majority_vote=majority_vote,
            final_resolution=final_resolution
        )

    def _get_shared_memory_summary(self) -> str:
        recent = self.debate_history[-self.memory_window:]
        if not recent:
            return "No shared memory yet."
        lines = []
        for round_data in recent:
            snippet = round_data.response.replace("\n", " ").strip()
            if len(snippet) > 120:
                snippet = snippet[:117].rstrip() + "..."
            lines.append(f"- {round_data.speaker}: {snippet}")
        return "\n".join(lines)

    def _conduct_majority_vote(self, agents: List[HistoricalAgent]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        proposals = []
        for agent in agents:
            if not agent.current_position:
                continue
            for topic, position in agent.current_position.items():
                proposals.append({"proposer": agent.name, "topic": topic, "proposal": position})

        if not proposals:
            return {"proposals": [], "majorityNeeded": len(agents) // 2 + 1}, None

        majority_needed = len(agents) // 2 + 1
        vote_results = []
        accepted = []

        agent_map = {agent.name: agent for agent in agents}
        for proposal in proposals:
            proposer = agent_map.get(proposal["proposer"])
            votes = []
            accept_count = 0
            for agent in agents:
                evaluation = agent.evaluate_proposal(proposal["proposal"], proposer)
                votes.append(
                    {
                        "voter": agent.name,
                        "accept": evaluation["accept"],
                        "reasoning": evaluation["reasoning"],
                    }
                )
                if evaluation["accept"]:
                    accept_count += 1
            outcome = {
                "proposal": proposal,
                "acceptCount": accept_count,
                "votes": votes,
                "passed": accept_count >= majority_needed,
            }
            vote_results.append(outcome)
            if outcome["passed"]:
                accepted.append(proposal)

        final_resolution = accepted[0] if accepted else None
        return {
            "proposals": vote_results,
            "majorityNeeded": majority_needed,
            "acceptedCount": len(accepted),
        }, final_resolution
    
    def _analyze_positions(self, agents: List[HistoricalAgent]) -> Tuple[List[str], List[str]]:
        """Analyze agent positions to find agreements and disagreements."""
        agreements = []
        disagreements = []
        
        # Compare positions on common topics
        common_topics = set()
        for agent in agents:
            common_topics.update(agent.current_position.keys())
        
        for topic in common_topics:
            positions = []
            for agent in agents:
                if topic in agent.current_position:
                    positions.append((agent.name, agent.current_position[topic]))
            
            if len(positions) >= 2:
                # Check if positions are similar
                if self._positions_similar(positions):
                    agreements.append(f"Agreement on {topic}: {positions[0][1]}")
                else:
                    disagreement_text = f"Disagreement on {topic}: "
                    for name, pos in positions:
                        disagreement_text += f"{name} ({pos}); "
                    disagreements.append(disagreement_text.rstrip("; "))
        
        return agreements, disagreements
    
    def _positions_similar(self, positions: List[Tuple[str, str]], threshold: float = 0.7) -> bool:
        """Check if positions are similar enough to be considered in agreement."""
        # Simplified similarity check - in a real implementation, this would use
        # more sophisticated NLP techniques
        if len(positions) < 2:
            return True
        
        # For now, just check if the first two positions contain similar keywords
        pos1 = positions[0][1].lower()
        pos2 = positions[1][1].lower()
        
        # Simple keyword overlap check
        words1 = set(pos1.split())
        words2 = set(pos2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return (overlap / total) >= threshold
    
    def get_debate_transcript(self) -> str:
        """Generate a readable transcript of the debate."""
        transcript = "=== DEBATE TRANSCRIPT ===\n\n"
        
        for round_data in self.debate_history:
            transcript += f"Round {round_data.round_number} - {round_data.speaker}:\n"
            transcript += f"{round_data.response}\n\n"
        
        return transcript
    
    def export_debate_data(self, filepath: str) -> None:
        """Export debate data to JSON file."""
        data = {
            "rounds": [
                {
                    "round_number": round_data.round_number,
                    "speaker": round_data.speaker,
                    "topic": round_data.topic,
                    "response": round_data.response,
                    "timestamp": round_data.timestamp.isoformat(),
                    "context": round_data.context
                }
                for round_data in self.debate_history
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
