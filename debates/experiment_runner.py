"""
Experiment runner for Goals 1-3.

8 experiment configurations:
1. Rational vs Rational (pure negotiation, maximize points)
2. Empathetic vs Empathetic (mutual empathy)
3. Rational vs Empathetic (asymmetric)
4. Less Empathy vs More Empathy (gradient)
5. Historical Agent A vs Historical Agent B (in-character)
6. Historical Agent A vs B with empathy injection into less-empathetic agent
7. Historical Agent A vs B with Judge evaluation
8. Full pipeline: Historical + empathy injection + Judge + policy scoring

Topics are parameterized: war, immigration, socialism (and custom).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

from agents.base_agent import HistoricalAgent
from agents.baseline_agents import RationalAgent, EmpatheticAgent
from agents.judge_agent import JudgeAgent, JudgeVerdict
from debates.debate_simulator import DebateSimulator, DebateResult
from scoring.policy_scoring import REGION_WEIGHTS, RegionWeights


EXPERIMENT_TOPICS = ["war", "immigration", "socialism", "territorial_disputes", "economic_policy"]


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment run."""
    name: str
    description: str
    agents: List[HistoricalAgent]
    topic: str
    max_rounds: int = 15
    consensus_threshold: float = 0.7
    use_judge: bool = False
    empathy_injection: Optional[Dict[str, float]] = None  # {agent_name: boost}
    region_weights: Optional[RegionWeights] = None
    num_simulations: int = 1  # for averaging


@dataclass
class ExperimentResult:
    """Result of a single experiment."""
    config_name: str
    topic: str
    debate_result: DebateResult
    judge_verdict: Optional[JudgeVerdict]
    scorecards: Dict[str, Dict[str, Any]]
    duration_seconds: float
    empathy_ratios: Dict[str, float]
    convergence_round: Optional[int]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "experiment": self.config_name,
            "topic": self.topic,
            "status": self.debate_result.status.value,
            "consensus_score": round(self.debate_result.consensus_score, 4),
            "rounds_played": len(self.debate_result.rounds),
            "duration_seconds": round(self.duration_seconds, 2),
            "empathy_ratios": {k: round(v, 3) for k, v in self.empathy_ratios.items()},
            "convergence_round": self.convergence_round,
            "scorecards": self.scorecards,
            "judge_verdict": self.judge_verdict.as_dict() if self.judge_verdict else None,
            "agreements": self.debate_result.key_agreements,
            "disagreements": self.debate_result.key_disagreements,
        }


@dataclass
class BatchResult:
    """Result of running multiple experiments."""
    experiments: List[ExperimentResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total_experiments": len(self.experiments),
            "summary": self.summary,
            "experiments": [e.as_dict() for e in self.experiments],
        }


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    """Run a single experiment."""
    start = time.time()

    # Apply empathy injection if specified
    if config.empathy_injection:
        for agent in config.agents:
            if agent.name in config.empathy_injection:
                agent.inject_empathy(config.empathy_injection[agent.name])

    # Record empathy ratios before debate
    empathy_ratios = {a.name: a.empathy_ratio for a in config.agents}

    # Run debate
    simulator = DebateSimulator(
        max_rounds=config.max_rounds,
        consensus_threshold=config.consensus_threshold,
    )
    debate_result = simulator.debate(
        agents=config.agents,
        topic=config.topic,
        initial_context={
            "context": "Experiment simulation",
            "policy_scoring": True,
        },
    )

    # Score each round retroactively for agents
    for round_num, rd in enumerate(debate_result.rounds):
        speaker = next((a for a in config.agents if a.name == rd.speaker), None)
        if speaker:
            opponent_obj = 0.0
            for other in config.agents:
                if other.name != speaker.name and other.scorecard.objective_values:
                    opponent_obj = other.scorecard.objective_values[-1]
            speaker.score_round(
                topic=config.topic,
                round_number=round_num + 1,
                max_rounds=config.max_rounds,
                opponent_objective=opponent_obj,
            )

    # Judge evaluation
    judge_verdict = None
    convergence_round = None
    if config.use_judge:
        judge = JudgeAgent(region_weights=config.region_weights)
        rounds_data = [
            {"speaker": rd.speaker, "response": rd.response, "round": rd.round_number}
            for rd in debate_result.rounds
        ]
        judge_verdict = judge.evaluate(config.agents, rounds_data, config.topic)
        convergence_round = judge_verdict.convergence_round

    scorecards = {a.name: a.scorecard.as_dict() for a in config.agents}
    duration = time.time() - start

    return ExperimentResult(
        config_name=config.name,
        topic=config.topic,
        debate_result=debate_result,
        judge_verdict=judge_verdict,
        scorecards=scorecards,
        duration_seconds=duration,
        empathy_ratios=empathy_ratios,
        convergence_round=convergence_round,
    )


def run_batch(configs: List[ExperimentConfig]) -> BatchResult:
    """Run a batch of experiments and produce a summary."""
    results: List[ExperimentResult] = []
    for config in configs:
        for _ in range(config.num_simulations):
            result = run_experiment(config)
            results.append(result)

    # Summarize
    summary = _summarize_batch(results)
    return BatchResult(experiments=results, summary=summary)


def _summarize_batch(results: List[ExperimentResult]) -> Dict[str, Any]:
    if not results:
        return {}

    by_experiment: Dict[str, List[ExperimentResult]] = {}
    for r in results:
        by_experiment.setdefault(r.config_name, []).append(r)

    summary: Dict[str, Any] = {}
    for name, group in by_experiment.items():
        rounds_list = [len(r.debate_result.rounds) for r in group]
        consensus_list = [r.debate_result.consensus_score for r in group]
        conv_rounds = [r.convergence_round for r in group if r.convergence_round is not None]
        summary[name] = {
            "num_runs": len(group),
            "avg_rounds": sum(rounds_list) / len(rounds_list),
            "avg_consensus": sum(consensus_list) / len(consensus_list),
            "avg_convergence_round": sum(conv_rounds) / len(conv_rounds) if conv_rounds else None,
            "topics": list(set(r.topic for r in group)),
        }
    return summary


# ---------------------------------------------------------------------------
# Pre-built experiment configurations (the 8 experiments)
# ---------------------------------------------------------------------------

def get_experiment_configs(
    topic: str = "war",
    historical_agents: Optional[List[HistoricalAgent]] = None,
    max_rounds: int = 15,
) -> List[ExperimentConfig]:
    """
    Return all 8 experiment configurations.

    Parameters
    ----------
    topic : str
        Topic for the debates.
    historical_agents : list, optional
        Two historical agents for experiments 5-8.
        If None, only experiments 1-4 are returned.
    max_rounds : int
        Max rounds per debate.
    """
    configs: List[ExperimentConfig] = []

    # Experiment 1: Rational vs Rational (pure point maximization)
    configs.append(ExperimentConfig(
        name="1_rational_vs_rational",
        description="Two purely rational agents negotiate to maximize their own points",
        agents=[
            RationalAgent(name="Rational-A"),
            RationalAgent(name="Rational-B"),
        ],
        topic=topic,
        max_rounds=max_rounds,
        use_judge=True,
    ))

    # Experiment 2: Empathetic vs Empathetic
    configs.append(ExperimentConfig(
        name="2_empathetic_vs_empathetic",
        description="Two empathetic agents seek mutual benefit",
        agents=[
            EmpatheticAgent(name="Empathetic-A", empathy_ratio=0.6),
            EmpatheticAgent(name="Empathetic-B", empathy_ratio=0.6),
        ],
        topic=topic,
        max_rounds=max_rounds,
        use_judge=True,
    ))

    # Experiment 3: Rational vs Empathetic (asymmetric)
    configs.append(ExperimentConfig(
        name="3_rational_vs_empathetic",
        description="Rational agent faces empathetic agent — asymmetric empathy",
        agents=[
            RationalAgent(name="Rational"),
            EmpatheticAgent(name="Empathetic", empathy_ratio=0.6),
        ],
        topic=topic,
        max_rounds=max_rounds,
        use_judge=True,
    ))

    # Experiment 4: Less Empathy vs More Empathy (gradient)
    configs.append(ExperimentConfig(
        name="4_low_empathy_vs_high_empathy",
        description="Low-empathy (0.2) vs high-empathy (0.8) agents",
        agents=[
            EmpatheticAgent(name="Low-Empathy", empathy_ratio=0.2),
            EmpatheticAgent(name="High-Empathy", empathy_ratio=0.8),
        ],
        topic=topic,
        max_rounds=max_rounds,
        use_judge=True,
    ))

    # Experiments 5-8 require historical agents
    if historical_agents and len(historical_agents) >= 2:
        a1, a2 = historical_agents[0], historical_agents[1]

        # Experiment 5: Historical A vs B (in-character, no modifications)
        configs.append(ExperimentConfig(
            name="5_historical_conflict",
            description=f"{a1.name} vs {a2.name} — unmodified historical personas",
            agents=[a1, a2],
            topic=topic,
            max_rounds=max_rounds,
            use_judge=True,
        ))

        # Experiment 6: Same as 5 but inject empathy into the less-empathetic agent
        less_empathetic = a1 if a1.empathy_ratio < a2.empathy_ratio else a2
        configs.append(ExperimentConfig(
            name="6_historical_empathy_injection",
            description=f"Same as exp 5 but inject +0.3 empathy into {less_empathetic.name}",
            agents=[a1, a2],
            topic=topic,
            max_rounds=max_rounds,
            use_judge=True,
            empathy_injection={less_empathetic.name: 0.3},
        ))

        # Experiment 7: Historical A vs B with full Judge evaluation
        configs.append(ExperimentConfig(
            name="7_historical_judged",
            description=f"{a1.name} vs {a2.name} with comprehensive Judge evaluation",
            agents=[a1, a2],
            topic=topic,
            max_rounds=max_rounds,
            use_judge=True,
        ))

        # Experiment 8: Full pipeline — historical + empathy + judge + all scoring
        configs.append(ExperimentConfig(
            name="8_full_pipeline",
            description="Full pipeline: historical agents + empathy injection + judge + policy scoring",
            agents=[a1, a2],
            topic=topic,
            max_rounds=max_rounds,
            use_judge=True,
            empathy_injection={less_empathetic.name: 0.4},
            region_weights=REGION_WEIGHTS.get("conflict_zone"),
        ))

    return configs


def run_all_experiments(
    topics: Optional[List[str]] = None,
    historical_agents: Optional[List[HistoricalAgent]] = None,
    max_rounds: int = 15,
    num_simulations: int = 1,
) -> BatchResult:
    """
    Run all 8 experiments across all specified topics.

    This is the main entry point for the experiment suite.
    """
    topics = topics or ["war", "immigration", "socialism"]
    all_configs: List[ExperimentConfig] = []

    for topic in topics:
        configs = get_experiment_configs(
            topic=topic,
            historical_agents=historical_agents,
            max_rounds=max_rounds,
        )
        for c in configs:
            c.num_simulations = num_simulations
        all_configs.extend(configs)

    return run_batch(all_configs)
