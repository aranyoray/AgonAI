"""
Example scenario: Hitler vs Gandhi vs Jinnah debate
"""

from agents import HitlerAgent, GandhiAgent, JinnahAgent
from debates import DebateSimulator


def run_hitler_gandhi_jinnah_debate():
    """Run a debate between Hitler, Gandhi, and Jinnah."""
    
    print("=== AI Political Agents Debate ===")
    print("Scenario: Hitler vs Gandhi vs Jinnah")
    print("Topic: Territorial Disputes and National Identity")
    print("=" * 50)
    
    # Create agents
    hitler = HitlerAgent()
    gandhi = GandhiAgent()
    jinnah = JinnahAgent()
    
    agents = [hitler, gandhi, jinnah]
    
    # Create debate simulator
    simulator = DebateSimulator(max_rounds=15, consensus_threshold=0.7)
    
    # Run debate
    result = simulator.debate(
        agents=agents,
        topic="territorial_disputes",
        initial_context={
            "historical_period": "1940s",
            "context": "Post-World War II territorial negotiations",
            "stakes": "High - involves national survival and identity"
        }
    )
    
    # Display results
    print(f"\n=== DEBATE RESULTS ===")
    print(f"Status: {result.status.value}")
    print(f"Consensus Score: {result.consensus_score:.2f}")
    print(f"Duration: {result.duration_minutes:.1f} minutes")
    print(f"Rounds: {len(result.rounds)}")
    
    print(f"\n=== KEY AGREEMENTS ===")
    for agreement in result.key_agreements:
        print(f"• {agreement}")
    
    print(f"\n=== KEY DISAGREEMENTS ===")
    for disagreement in result.key_disagreements:
        print(f"• {disagreement}")
    
    print(f"\n=== DEBATE TRANSCRIPT ===")
    print(simulator.get_debate_transcript())
    
    # Export data
    simulator.export_debate_data("hitler_gandhi_jinnah_debate.json")
    print(f"\nDebate data exported to: hitler_gandhi_jinnah_debate.json")
    
    return result


if __name__ == "__main__":
    run_hitler_gandhi_jinnah_debate()
