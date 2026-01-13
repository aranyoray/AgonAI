"""
AI Political Agents package for simulating historical figure debates.
"""

from .base_agent import HistoricalAgent, PersonalityTraits, HistoricalContext, Ideology
from .hitler_agent import HitlerAgent
from .gandhi_agent import GandhiAgent
from .jinnah_agent import JinnahAgent

__all__ = [
    'HistoricalAgent',
    'PersonalityTraits', 
    'HistoricalContext',
    'Ideology',
    'HitlerAgent',
    'GandhiAgent', 
    'JinnahAgent'
]
