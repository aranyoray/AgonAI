"""
Conversation state management for multi-turn chat continuity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional
import re
import uuid


@dataclass
class ConversationTurn:
    role: str
    content: str
    ts: datetime


@dataclass
class ConversationMetrics:
    rapport: float = 0.5
    polarity: float = 0.5
    topic_pressure: float = 0.0
    empathy_reservoir: float = 0.0
    consensus_score: float = 0.0


@dataclass
class ResponsePlan:
    reply_type: str
    rationale: str
    repeat_detected: bool = False


class ConversationState:
    def __init__(
        self,
        session_id: str,
        memory_window: int = 8,
        compromise_threshold: float = 0.7,
        weights: Optional[Dict[str, float]] = None,
        willingness_to_compromise: float = 0.7,
    ) -> None:
        self.session_id = session_id
        self.turns: List[ConversationTurn] = []
        self.summary: str = ""
        self.salience: List[str] = []
        self.open_loops: List[str] = []
        self.metrics = ConversationMetrics()
        self.memory_window = memory_window
        self.compromise_threshold = compromise_threshold
        self.weights = weights or {
            "alignment": 0.35,
            "willingness": 0.25,
            "memory_bias": 0.2,
            "empathy": 0.2,
        }
        self.willingness_to_compromise = willingness_to_compromise
        self._memory_bias = 0.0

    def append_turn(self, role: str, content: str, ts: Optional[datetime] = None) -> None:
        self.turns.append(
            ConversationTurn(
                role=role,
                content=content,
                ts=ts or datetime.utcnow(),
            )
        )

    def appendTurn(self, role: str, content: str, ts: Optional[datetime] = None) -> None:
        self.append_turn(role=role, content=content, ts=ts)

    def update_summary(self) -> str:
        if len(self.turns) <= self.memory_window:
            return self.summary
        older_turns = self.turns[:-self.memory_window]
        summary_bits: List[str] = []
        for turn in older_turns[-6:]:
            snippet = _truncate(turn.content, 90)
            summary_bits.append(f"{turn.role}: {snippet}")
        self.summary = "Earlier context: " + " | ".join(summary_bits)
        return self.summary

    def updateSummary(self) -> str:
        return self.update_summary()

    def extract_salience_and_open_loops(self) -> None:
        salience: List[str] = []
        open_loops: List[str] = []
        for turn in self.turns[-self.memory_window:]:
            for sentence in _split_sentences(turn.content):
                if _is_salient(sentence):
                    salience.append(sentence)
                if _is_open_loop(sentence):
                    open_loops.append(sentence)
        self.salience = _dedupe_keep_order(salience, limit=6)
        self.open_loops = _dedupe_keep_order(open_loops, limit=6)

    def extractSalienceAndOpenLoops(self) -> None:
        self.extract_salience_and_open_loops()

    def update_metrics(self) -> None:
        if not self.turns:
            return
        last = self.turns[-1]
        text = last.content.lower()
        acknowledgement = _contains_any(text, ACKNOWLEDGEMENT_CUES)
        agreement = _contains_any(text, AGREEMENT_CUES)
        disagreement = _contains_any(text, DISAGREEMENT_CUES)
        empathy = _contains_any(text, EMPATHY_CUES)
        confirmation = _contains_any(text, CONFIRMATION_CUES)

        if acknowledgement:
            self.metrics.rapport = _clamp(self.metrics.rapport + 0.08)
        if agreement:
            self.metrics.polarity = _clamp(self.metrics.polarity + 0.1)
        if disagreement:
            self.metrics.polarity = _clamp(self.metrics.polarity - 0.15)
        if empathy:
            self.metrics.empathy_reservoir = _clamp(self.metrics.empathy_reservoir + 0.1)
        if acknowledgement and empathy:
            self.metrics.empathy_reservoir = _clamp(self.metrics.empathy_reservoir + 0.05)
        if confirmation:
            self._memory_bias = _clamp(self._memory_bias + 0.1)

        if disagreement:
            self.metrics.topic_pressure = _clamp(self.metrics.topic_pressure + 0.2)
        if agreement or acknowledgement:
            self.metrics.topic_pressure = _clamp(self.metrics.topic_pressure - 0.06)

        alignment = self.metrics.polarity
        consensus = (
            alignment * self.weights["alignment"]
            + self.willingness_to_compromise * self.weights["willingness"]
            + self._memory_bias * self.weights["memory_bias"]
            + self.metrics.empathy_reservoir * self.weights["empathy"]
        )
        self.metrics.consensus_score = _clamp(consensus)

    def updateMetrics(self) -> None:
        self.update_metrics()

    def last_turns(self, count: Optional[int] = None) -> List[ConversationTurn]:
        count = count or self.memory_window
        return self.turns[-count:]

    def last_turn_by_role(self, role: str) -> Optional[ConversationTurn]:
        for turn in reversed(self.turns):
            if turn.role == role:
                return turn
        return None

    def is_repetitive(self, candidate: str, role: Optional[str] = None, threshold: float = 0.9) -> bool:
        last_turn = self.last_turn_by_role(role) if role else (self.turns[-1] if self.turns else None)
        if not last_turn:
            return False
        ratio = SequenceMatcher(None, last_turn.content.lower(), candidate.lower()).ratio()
        return ratio >= threshold

    def build_prompt_context(self) -> Dict[str, Any]:
        recent = [
            {"role": turn.role, "content": turn.content, "ts": turn.ts.isoformat()}
            for turn in self.last_turns()
        ]
        return {
            "summary": self.summary,
            "recent_turns": recent,
            "salience": self.salience,
            "open_loops": self.open_loops,
            "metrics": {
                "rapport": self.metrics.rapport,
                "polarity": self.metrics.polarity,
                "topic_pressure": self.metrics.topic_pressure,
                "empathy_reservoir": self.metrics.empathy_reservoir,
                "consensus_score": self.metrics.consensus_score,
            },
            "memory_window": self.memory_window,
            "compromise_threshold": self.compromise_threshold,
        }

    def buildPromptContext(self) -> Dict[str, Any]:
        return self.build_prompt_context()


class ConversationStore:
    def load_state(self, session_id: str) -> ConversationState:
        raise NotImplementedError


class InMemoryConversationStore(ConversationStore):
    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationState] = {}

    def load_state(self, session_id: str) -> ConversationState:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationState(session_id=session_id)
        return self._sessions[session_id]


def load_state(session_id: Optional[str], store: Optional[ConversationStore] = None) -> ConversationState:
    store = store or InMemoryConversationStore()
    session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"
    return store.load_state(session_id)


def loadState(session_id: Optional[str], store: Optional[ConversationStore] = None) -> ConversationState:
    return load_state(session_id=session_id, store=store)


def plan_response(
    state: ConversationState,
    last_user_message: Optional[str] = None,
) -> ResponsePlan:
    repeat_detected = False
    if last_user_message:
        last_user = state.last_turn_by_role("user")
        if last_user:
            ratio = SequenceMatcher(
                None, last_user.content.lower(), last_user_message.lower()
            ).ratio()
            repeat_detected = ratio >= 0.92

    metrics = state.metrics
    if metrics.consensus_score >= state.compromise_threshold:
        return ResponsePlan(
            reply_type="confirm_agreement",
            rationale="Consensus score exceeds threshold; propose shared agreement and confirm.",
            repeat_detected=repeat_detected,
        )
    if metrics.topic_pressure >= 0.65 or metrics.polarity <= 0.35:
        return ResponsePlan(
            reply_type="summarize_and_choose",
            rationale="Friction detected; summarize disagreement and offer options.",
            repeat_detected=repeat_detected,
        )
    if state.open_loops:
        return ResponsePlan(
            reply_type="propose_plan",
            rationale="Open loops exist; propose a concrete plan to resolve them.",
            repeat_detected=repeat_detected,
        )
    if last_user_message and "?" in last_user_message:
        return ResponsePlan(
            reply_type="answer",
            rationale="Direct question detected; answer and advance the thread.",
            repeat_detected=repeat_detected,
        )
    return ResponsePlan(
        reply_type="propose_plan",
        rationale="Default to advancing with a plan toward consensus.",
        repeat_detected=repeat_detected,
    )


ACKNOWLEDGEMENT_CUES = [
    "i hear you",
    "i understand",
    "that makes sense",
    "thanks for",
    "appreciate",
]
AGREEMENT_CUES = [
    "agree",
    "aligned",
    "makes sense",
    "sounds good",
    "yes",
]
DISAGREEMENT_CUES = [
    "disagree",
    "not aligned",
    "no",
    "doesn't",
    "cannot",
    "won't",
]
EMPATHY_CUES = [
    "you mentioned",
    "as you said",
    "earlier you",
    "i remember",
    "given your",
    "i hear you",
    "i appreciate",
]
CONFIRMATION_CUES = [
    "that's right",
    "correct",
    "exactly",
    "yes",
    "confirmed",
]


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _is_salient(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(
        cue in lowered
        for cue in ["prefer", "priority", "goal", "need", "must", "should", "important", "want"]
    )


def _is_open_loop(sentence: str) -> bool:
    lowered = sentence.lower()
    return "?" in sentence or any(cue in lowered for cue in ["todo", "next step", "follow up", "open"])


def _dedupe_keep_order(items: List[str], limit: int) -> List[str]:
    seen = set()
    output: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        output.append(item)
        if len(output) >= limit:
            break
    return output


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _contains_any(text: str, cues: List[str]) -> bool:
    return any(cue in text for cue in cues)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))
