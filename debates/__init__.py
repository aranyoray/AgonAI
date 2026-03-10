"""
Debate simulation package for AI political agents.
"""

from .debate_simulator import DebateSimulator, DebateStatus, DebateRound, DebateResult
from .experiment_runner import (
    ExperimentConfig,
    ExperimentResult,
    BatchResult,
    run_experiment,
    run_batch,
    run_all_experiments,
    get_experiment_configs,
    EXPERIMENT_TOPICS,
)

__all__ = [
    'DebateSimulator',
    'DebateStatus',
    'DebateRound',
    'DebateResult',
    'ExperimentConfig',
    'ExperimentResult',
    'BatchResult',
    'run_experiment',
    'run_batch',
    'run_all_experiments',
    'get_experiment_configs',
    'EXPERIMENT_TOPICS',
]
