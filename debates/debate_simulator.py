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


class DebateSimulator:
    """
    Simulates debates between historical figure AI agents.
    """
    
    def __init__(self, max_rounds: int = 20, consensus_threshold: float = 0.8):
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold
        self.debate_history: List[DebateRound] = []
        
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
        
        # Initialize positions
        for agent in agents:
            agent.current_position = agent.current_position.copy()
        
        # Debate loop
        for round_num in range(self.max_rounds):
            # Determine current speaker (rotate through agents)
            current_speaker = agents[round_num % len(agents)]
            
            # Generate response
            response = current_speaker.generate_response(
                topic=topic,
                other_agents=[a for a in agents if a.name != current_speaker.name],
                debate_context=current_context
            )
            
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
        
        return DebateResult(
            status=status,
            rounds=self.debate_history.copy(),
            consensus_score=consensus_score,
            key_agreements=agreements,
            key_disagreements=disagreements,
            final_positions=final_positions,
            duration_minutes=duration
        )
    
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
