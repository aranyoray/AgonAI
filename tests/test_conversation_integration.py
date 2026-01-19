import unittest

from utils.conversation_state import ConversationState, plan_response


class ConversationIntegrationTests(unittest.TestCase):
    def test_repeat_question_detected(self) -> None:
        state = ConversationState(session_id="integration")
        state.append_turn("user", "How do we maintain context across turns?")
        state.append_turn("assistant", "We can store a summary and recent turns.")
        plan = plan_response(state, last_user_message="How do we maintain context across turns?")
        self.assertTrue(plan.repeat_detected)

    def test_disagreement_triggers_summarize_and_choose(self) -> None:
        state = ConversationState(session_id="integration")
        for _ in range(4):
            state.append_turn("user", "I disagree with that approach.")
            state.update_metrics()
        plan = plan_response(state, last_user_message="I still disagree.")
        self.assertEqual(plan.reply_type, "summarize_and_choose")

    def test_open_loops_drive_plan(self) -> None:
        state = ConversationState(session_id="integration")
        state.append_turn("user", "We should decide on next steps. What should we do next?")
        state.extract_salience_and_open_loops()
        plan = plan_response(state, last_user_message="What should we do next?")
        self.assertEqual(plan.reply_type, "propose_plan")


if __name__ == "__main__":
    unittest.main()
