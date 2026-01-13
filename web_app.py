"""
Web interface for AI Political Agents using Streamlit.
"""

import streamlit as st
import json
from typing import List, Dict, Any
from agents import HitlerAgent, GandhiAgent, JinnahAgent
from debates import DebateSimulator


def create_agent(agent_name: str):
    """Create an agent by name."""
    agents = {
        "Hitler": HitlerAgent,
        "Gandhi": GandhiAgent,
        "Jinnah": JinnahAgent,
    }
    
    return agents[agent_name]()


def main():
    st.set_page_config(
        page_title="AI Political Agents",
        page_icon="🏛️",
        layout="wide"
    )
    
    st.title("🏛️ AI Political Agents Debate Simulator")
    st.markdown("Simulate political debates between historical figures using AI agents.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Agent selection
        available_agents = ["Hitler", "Gandhi", "Jinnah"]
        selected_agents = st.multiselect(
            "Select Agents:",
            available_agents,
            default=["Hitler", "Gandhi", "Jinnah"]
        )
        
        # Topic selection
        topic = st.text_input(
            "Debate Topic:",
            value="territorial_disputes",
            help="Enter the topic for the debate"
        )
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            max_rounds = st.slider("Max Rounds:", 5, 30, 15)
            consensus_threshold = st.slider("Consensus Threshold:", 0.1, 1.0, 0.7)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Start Debate", type="primary"):
            if len(selected_agents) < 2:
                st.error("Please select at least 2 agents for the debate.")
                return
            
            # Create agents
            agents = [create_agent(name) for name in selected_agents]
            
            # Create debate simulator
            simulator = DebateSimulator(
                max_rounds=max_rounds, 
                consensus_threshold=consensus_threshold
            )
            
            # Run debate
            with st.spinner("Running debate simulation..."):
                result = simulator.debate(
                    agents=agents,
                    topic=topic,
                    initial_context={
                        "historical_period": "1940s",
                        "context": "High-stakes political negotiation",
                        "stakes": "Critical - involves national interests"
                    }
                )
            
            # Store result in session state
            st.session_state.debate_result = result
            st.session_state.simulator = simulator
    
    with col2:
        st.header("Quick Scenarios")
        
        if st.button("Hitler vs Gandhi vs Jinnah"):
            st.session_state.selected_agents = ["Hitler", "Gandhi", "Jinnah"]
            st.session_state.topic = "territorial_disputes"
            st.rerun()
        
        if st.button("Hitler vs Gandhi"):
            st.session_state.selected_agents = ["Hitler", "Gandhi"]
            st.session_state.topic = "race_relations"
            st.rerun()
        
        if st.button("Gandhi vs Jinnah"):
            st.session_state.selected_agents = ["Gandhi", "Jinnah"]
            st.session_state.topic = "partition_of_india"
            st.rerun()
    
    # Display results if available
    if 'debate_result' in st.session_state:
        result = st.session_state.debate_result
        simulator = st.session_state.simulator
        
        st.header("📊 Debate Results")
        
        # Results overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Status", result.status.value)
        
        with col2:
            st.metric("Consensus Score", f"{result.consensus_score:.2f}")
        
        with col3:
            st.metric("Rounds", len(result.rounds))
        
        with col4:
            st.metric("Duration", f"{result.duration_minutes:.1f} min")
        
        # Agreements and disagreements
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Key Agreements")
            for agreement in result.key_agreements:
                st.write(f"• {agreement}")
        
        with col2:
            st.subheader("❌ Key Disagreements")
            for disagreement in result.key_disagreements:
                st.write(f"• {disagreement}")
        
        # Debate transcript
        st.subheader("📝 Debate Transcript")
        
        with st.expander("View Full Transcript", expanded=True):
            for i, round_data in enumerate(result.rounds):
                st.write(f"**Round {round_data.round_number} - {round_data.speaker}:**")
                st.write(round_data.response)
                st.write("---")
        
        # Download options
        st.subheader("💾 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            json_data = json.dumps({
                "status": result.status.value,
                "consensus_score": result.consensus_score,
                "rounds": len(result.rounds),
                "duration_minutes": result.duration_minutes,
                "agreements": result.key_agreements,
                "disagreements": result.key_disagreements,
                "transcript": simulator.get_debate_transcript()
            }, indent=2)
            
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"debate_result_{topic}.json",
                mime="application/json"
            )
        
        with col2:
            # Text export
            text_data = simulator.get_debate_transcript()
            st.download_button(
                label="📝 Download Transcript",
                data=text_data,
                file_name=f"debate_transcript_{topic}.txt",
                mime="text/plain"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**AI Political Agents** - Exploring historical political debates through AI simulation. "
        "This is a research tool for understanding how different historical figures might have "
        "interacted and whether consensus was possible."
    )


if __name__ == "__main__":
    main()
