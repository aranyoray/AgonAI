"""
Test script for the AI Political Agents system.
"""

from agents import HitlerAgent, GandhiAgent, JinnahAgent
from debates import DebateSimulator


def test_agent_creation():
    """Test that agents can be created successfully."""
    print("Testing agent creation...")
    
    try:
        hitler = HitlerAgent()
        gandhi = GandhiAgent()
        jinnah = JinnahAgent()
        
        print(f"✓ Hitler agent created: {hitler.name}")
        print(f"✓ Gandhi agent created: {gandhi.name}")
        print(f"✓ Jinnah agent created: {jinnah.name}")
        
        return [hitler, gandhi, jinnah]
    except Exception as e:
        print(f"✗ Error creating agents: {e}")
        return None


def test_consensus_calculation(agents):
    """Test consensus calculation between agents."""
    print("\nTesting consensus calculation...")
    
    try:
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                score = agent1.calculate_consensus_score(agent2)
                print(f"✓ {agent1.name} vs {agent2.name}: {score:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Error calculating consensus: {e}")
        return False


def test_debate_simulation(agents):
    """Test a short debate simulation."""
    print("\nTesting debate simulation...")
    
    try:
        simulator = DebateSimulator(max_rounds=5, consensus_threshold=0.8)
        
        result = simulator.debate(
            agents=agents,
            topic="territorial_disputes",
            initial_context={"test": True}
        )
        
        print(f"✓ Debate completed: {result.status.value}")
        print(f"✓ Consensus score: {result.consensus_score:.2f}")
        print(f"✓ Rounds: {len(result.rounds)}")
        
        return True
    except Exception as e:
        print(f"✗ Error in debate simulation: {e}")
        return False


def test_agent_responses(agents):
    """Test that agents can generate responses."""
    print("\nTesting agent responses...")
    
    try:
        for agent in agents:
            response = agent.generate_response(
                topic="territorial_disputes",
                other_agents=[a for a in agents if a.name != agent.name],
                debate_context={"test": True}
            )
            
            print(f"✓ {agent.name} generated response ({len(response)} chars)")
        
        return True
    except Exception as e:
        print(f"✗ Error generating responses: {e}")
        return False


def main():
    """Run all tests."""
    print("=== AI Political Agents System Test ===\n")
    
    # Test agent creation
    agents = test_agent_creation()
    if not agents:
        print("❌ Agent creation failed. Exiting.")
        return
    
    # Test consensus calculation
    if not test_consensus_calculation(agents):
        print("❌ Consensus calculation failed.")
        return
    
    # Test agent responses
    if not test_agent_responses(agents):
        print("❌ Agent response generation failed.")
        return
    
    # Test debate simulation
    if not test_debate_simulation(agents):
        print("❌ Debate simulation failed.")
        return
    
    print("\n✅ All tests passed! The system is working correctly.")
    
    # Run a sample debate
    print("\n=== Sample Debate ===")
    simulator = DebateSimulator(max_rounds=3, consensus_threshold=0.5)
    result = simulator.debate(
        agents=agents,
        topic="territorial_disputes",
        initial_context={"sample": True}
    )
    
    print(f"\nDebate Status: {result.status.value}")
    print(f"Consensus Score: {result.consensus_score:.2f}")
    print(f"Rounds: {len(result.rounds)}")
    
    print("\nFirst few responses:")
    for i, round_data in enumerate(result.rounds[:3]):
        print(f"\nRound {round_data.round_number} - {round_data.speaker}:")
        print(f"{round_data.response[:200]}...")


if __name__ == "__main__":
    main()
