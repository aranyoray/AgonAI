"""
Web interface for AI Political Agents using Streamlit.
Supports debate simulation, experiment runner, and policy scoring.
"""

import streamlit as st
import json
from typing import List, Dict, Any
from agents import (
    HitlerAgent, GandhiAgent, JinnahAgent,
    RationalAgent, EmpatheticAgent, JudgeAgent,
)
from debates import DebateSimulator
from debates.experiment_runner import (
    get_experiment_configs, run_experiment, run_all_experiments,
    EXPERIMENT_TOPICS,
)


AGENT_REGISTRY = {
    "Hitler": HitlerAgent,
    "Gandhi": GandhiAgent,
    "Jinnah": JinnahAgent,
    "Rational": lambda: RationalAgent(),
    "Empathetic": lambda: EmpatheticAgent(),
}


def create_agent(agent_name: str):
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {agent_name}")
    return AGENT_REGISTRY[agent_name]()


def main():
    st.set_page_config(
        page_title="AgonAI - Political Agent Lab",
        page_icon="🏛️",
        layout="wide"
    )

    st.title("AgonAI: Political Agent Consensus Lab")
    st.markdown("Simulate political debates with empathy-weighted policy scoring.")

    tab_debate, tab_experiment = st.tabs(["Debate Simulator", "Experiments"])

    # ---- Tab 1: Debate Simulator ----
    with tab_debate:
        with st.sidebar:
            st.header("Configuration")
            available_agents = list(AGENT_REGISTRY.keys())
            selected_agents = st.multiselect(
                "Select Agents:", available_agents,
                default=["Gandhi", "Jinnah"]
            )
            topic = st.selectbox(
                "Topic:", EXPERIMENT_TOPICS + ["territorial_disputes", "race_relations", "partition_of_india", "custom"]
            )
            if topic == "custom":
                topic = st.text_input("Custom topic:", value="territorial_disputes")

            with st.expander("Advanced Settings"):
                max_rounds = st.slider("Max Rounds:", 5, 30, 15)
                consensus_threshold = st.slider("Consensus Threshold:", 0.1, 1.0, 0.7)
                use_judge = st.checkbox("Enable Judge Agent", value=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            if st.button("Run Debate", type="primary"):
                if len(selected_agents) < 2:
                    st.error("Please select at least 2 agents.")
                    return

                agents = [create_agent(name) for name in selected_agents]

                simulator = DebateSimulator(
                    max_rounds=max_rounds,
                    consensus_threshold=consensus_threshold
                )

                with st.spinner("Running debate simulation..."):
                    result = simulator.debate(
                        agents=agents,
                        topic=topic,
                        initial_context={
                            "context": "High-stakes political negotiation",
                            "policy_scoring": True,
                        }
                    )

                    # Score rounds
                    for round_num, rd in enumerate(result.rounds):
                        speaker = next((a for a in agents if a.name == rd.speaker), None)
                        if speaker:
                            opponent_obj = 0.0
                            for other in agents:
                                if other.name != speaker.name and other.scorecard.objective_values:
                                    opponent_obj = other.scorecard.objective_values[-1]
                            speaker.score_round(
                                topic=topic,
                                round_number=round_num + 1,
                                max_rounds=max_rounds,
                                opponent_objective=opponent_obj,
                            )

                st.session_state.debate_result = result
                st.session_state.simulator = simulator
                st.session_state.debate_agents = agents

                # Judge evaluation
                if use_judge:
                    judge = JudgeAgent()
                    rounds_data = [
                        {"speaker": rd.speaker, "response": rd.response, "round": rd.round_number}
                        for rd in result.rounds
                    ]
                    st.session_state.judge_verdict = judge.evaluate(agents, rounds_data, topic)

        with col2:
            st.header("Quick Scenarios")
            if st.button("Gandhi vs Jinnah"):
                st.session_state.selected_agents = ["Gandhi", "Jinnah"]
                st.rerun()
            if st.button("Rational vs Empathetic"):
                st.session_state.selected_agents = ["Rational", "Empathetic"]
                st.rerun()
            if st.button("Hitler vs Gandhi"):
                st.session_state.selected_agents = ["Hitler", "Gandhi"]
                st.rerun()

        # Display results
        if 'debate_result' in st.session_state:
            result = st.session_state.debate_result
            agents = st.session_state.debate_agents

            st.header("Results")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", result.status.value)
            c2.metric("Consensus", f"{result.consensus_score:.2f}")
            c3.metric("Rounds", len(result.rounds))
            c4.metric("Duration", f"{result.duration_minutes:.1f}m")

            # Policy Scores
            st.subheader("Policy Scores")
            score_cols = st.columns(len(agents))
            for i, agent in enumerate(agents):
                with score_cols[i]:
                    st.markdown(f"**{agent.name}**")
                    cs = agent.scorecard.cumulative_scores
                    st.write(f"Political: +{cs.political.benefit:.0f} / -{cs.political.cost:.0f} = {cs.political.net:.0f}")
                    st.write(f"Economic: +{cs.economic.benefit:.0f} / -{cs.economic.cost:.0f} = {cs.economic.net:.0f}")
                    st.write(f"Social: +{cs.social.benefit:.0f} / -{cs.social.cost:.0f} = {cs.social.net:.0f}")
                    st.write(f"Objective: **{agent.scorecard.final_objective:.1f}**")
                    st.write(f"Empathy: {agent.empathy_ratio:.2f} | Fatigue: {agent.fatigue:.3f}")

            # Judge verdict
            if 'judge_verdict' in st.session_state:
                jv = st.session_state.judge_verdict
                st.subheader("Judge Verdict")
                st.write(f"**Winner:** {jv.winner or 'No clear winner'} (margin: {jv.margin:.1f})")
                if jv.convergence_round:
                    st.write(f"**Convergence:** Round {jv.convergence_round}")
                for rec in jv.recommendations:
                    st.info(rec)

            # Chat transcript
            st.subheader("Debate Transcript")
            for rd in result.rounds:
                with st.chat_message(rd.speaker):
                    st.write(f"**Round {rd.round_number} - {rd.speaker}**")
                    st.write(rd.response)

            # Export
            st.subheader("Export")
            json_data = json.dumps({
                "status": result.status.value,
                "consensus_score": result.consensus_score,
                "rounds": len(result.rounds),
                "policy_scores": {a.name: a.scorecard.as_dict() for a in agents},
            }, indent=2)
            st.download_button("Download JSON", json_data, "debate_result.json", "application/json")

    # ---- Tab 2: Experiments ----
    with tab_experiment:
        st.header("Experiment Runner")
        st.markdown("Run pre-configured experiments comparing rational vs empathetic negotiation.")

        exp_topic = st.selectbox("Experiment topic:", EXPERIMENT_TOPICS, key="exp_topic")
        exp_id = st.selectbox("Experiment:", [
            "1. Rational vs Rational",
            "2. Empathetic vs Empathetic",
            "3. Rational vs Empathetic",
            "4. Low Empathy vs High Empathy",
            "5. Historical Conflict",
            "6. Historical + Empathy Injection",
            "7. Historical + Judge",
            "8. Full Pipeline",
        ])
        exp_rounds = st.slider("Max rounds:", 5, 30, 15, key="exp_rounds")

        exp_num = int(exp_id.split(".")[0])
        hist_agents = None
        if exp_num >= 5:
            hist_names = st.multiselect(
                "Historical agents (pick 2):", ["Hitler", "Gandhi", "Jinnah"],
                default=["Gandhi", "Jinnah"], key="exp_hist"
            )
            if len(hist_names) >= 2:
                hist_agents = [create_agent(n) for n in hist_names[:2]]

        if st.button("Run Experiment", key="run_exp"):
            configs = get_experiment_configs(
                topic=exp_topic,
                historical_agents=hist_agents,
                max_rounds=exp_rounds,
            )
            idx = min(exp_num - 1, len(configs) - 1)
            if idx < 0 or idx >= len(configs):
                st.error("Experiment not available with current settings.")
            else:
                with st.spinner("Running experiment..."):
                    result = run_experiment(configs[idx])

                st.success(f"Experiment: {result.config_name}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Status", result.debate_result.status.value)
                c2.metric("Consensus", f"{result.debate_result.consensus_score:.3f}")
                c3.metric("Rounds", len(result.debate_result.rounds))

                st.write("**Empathy Ratios:**", result.empathy_ratios)

                if result.judge_verdict:
                    jv = result.judge_verdict
                    st.subheader("Judge Verdict")
                    st.write(f"Winner: {jv.winner or 'No clear winner'} | Margin: {jv.margin:.1f}")
                    for rec in jv.recommendations:
                        st.info(rec)

                st.json(result.as_dict())

    st.markdown("---")
    st.markdown(
        "**AgonAI** — Exploring political negotiation through empathy-weighted multi-agent simulation."
    )


if __name__ == "__main__":
    main()
