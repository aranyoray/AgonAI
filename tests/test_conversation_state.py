import unittest

from utils.conversation_state import ConversationState


class ConversationStateTests(unittest.TestCase):
    def test_summary_updates_after_window(self) -> None:
        state = ConversationState(session_id="test", memory_window=3)
        for idx in range(5):
            state.append_turn("user", f"Message {idx} about goals and priorities.")
        state.update_summary()
        self.assertIn("Earlier context", state.summary)

    def test_repetition_detector_flags_similar_output(self) -> None:
        state = ConversationState(session_id="test")
        state.append_turn("assistant", "We should align on shared goals before acting.")
        self.assertTrue(
            state.is_repetitive(
                "We should align on shared goals before acting.",
                role="assistant",
                threshold=0.85,
            )
        )

    def test_metrics_update_on_acknowledgement(self) -> None:
        state = ConversationState(session_id="test")
        state.append_turn("assistant", "I hear you and appreciate the concern you raised.")
        state.update_metrics()
        self.assertGreater(state.metrics.rapport, 0.5)
        self.assertGreater(state.metrics.empathy_reservoir, 0.0)


if __name__ == "__main__":
    unittest.main()
