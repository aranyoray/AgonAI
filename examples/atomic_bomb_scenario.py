"""
Example scenario: US vs Japan - Could the atomic bomb have been prevented?
"""

from agents.base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology
from debates import DebateSimulator


class TrumanAgent(HistoricalAgent):
    """Harry S. Truman - US President during WWII"""
    
    def __init__(self, llm_client=None):
        personality = PersonalityTraits(
            assertiveness=0.8,
            cooperativeness=0.6,
            openness_to_change=0.5,
            emotional_stability=0.7,
            dominance=0.7,
            charisma=0.6,
            pragmatism=0.9,
            idealism=0.6
        )
        
        context = HistoricalContext(
            time_period="1940s",
            major_events=["Pearl Harbor", "D-Day", "Hiroshima", "Nagasaki", "V-J Day"],
            cultural_background="American, Midwestern values",
            education="High school, military service",
            key_relationships=["FDR", "Churchill", "Stalin", "Bess Truman"],
            defining_moments=["FDR's death", "Decision to use atomic bomb", "End of WWII"]
        )
        
        super().__init__(
            name="Harry S. Truman",
            ideology=Ideology.DEMOCRACY,
            personality=personality,
            context=context,
            llm_client=llm_client
        )
        
        self.red_lines = [
            "Unconditional surrender of Japan",
            "Protection of American lives",
            "Ending the war as quickly as possible",
            "Preventing Soviet expansion in Asia"
        ]
        
        self.current_position = {
            "military_strategy": "Use all available means to end the war quickly",
            "japanese_surrender": "Must be unconditional and complete",
            "atomic_weapons": "Justified to save American lives",
            "post_war_planning": "Democratization and demilitarization of Japan"
        }


class HirohitoAgent(HistoricalAgent):
    """Emperor Hirohito - Japanese Emperor during WWII"""
    
    def __init__(self, llm_client=None):
        personality = PersonalityTraits(
            assertiveness=0.4,
            cooperativeness=0.7,
            openness_to_change=0.3,
            emotional_stability=0.8,
            dominance=0.6,
            charisma=0.8,
            pragmatism=0.8,
            idealism=0.7
        )
        
        context = HistoricalContext(
            time_period="1940s",
            major_events=["Pearl Harbor", "Battle of Midway", "Hiroshima", "Nagasaki", "Surrender"],
            cultural_background="Japanese, Imperial tradition",
            education="Imperial education, military training",
            key_relationships=["Tojo", "Yamamoto", "MacArthur", "Japanese people"],
            defining_moments=["Pearl Harbor decision", "Atomic bombings", "Surrender broadcast"]
        )
        
        super().__init__(
            name="Emperor Hirohito",
            ideology=Ideology.AUTHORITARIANISM,
            personality=personality,
            context=context,
            llm_client=llm_client
        )
        
        self.red_lines = [
            "Preservation of the Imperial system",
            "Protection of Japanese people",
            "Maintenance of Japanese honor",
            "Avoiding complete destruction of Japan"
        ]
        
        self.current_position = {
            "military_strategy": "Defend the homeland at all costs",
            "surrender_terms": "Must preserve the Emperor system",
            "atomic_weapons": "Unprecedented and devastating",
            "post_war_planning": "Preserve Japanese culture and traditions"
        }


def run_atomic_bomb_debate():
    """Run a debate about whether the atomic bomb could have been prevented."""
    
    print("=== AI Political Agents Debate ===")
    print("Scenario: Truman vs Hirohito")
    print("Topic: Could the atomic bomb have been prevented?")
    print("=" * 50)
    
    # Create agents
    truman = TrumanAgent()
    hirohito = HirohitoAgent()
    
    agents = [truman, hirohito]
    
    # Create debate simulator
    simulator = DebateSimulator(max_rounds=12, consensus_threshold=0.6)
    
    # Run debate
    result = simulator.debate(
        agents=agents,
        topic="atomic_bomb_prevention",
        initial_context={
            "historical_period": "August 1945",
            "context": "Final days of WWII, decision to use atomic weapons",
            "stakes": "Extremely high - millions of lives at stake",
            "background": "Japan has not surrendered despite conventional bombing, US has atomic weapons ready"
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
    simulator.export_debate_data("truman_hirohito_atomic_bomb_debate.json")
    print(f"\nDebate data exported to: truman_hirohito_atomic_bomb_debate.json")
    
    return result


if __name__ == "__main__":
    run_atomic_bomb_debate()
