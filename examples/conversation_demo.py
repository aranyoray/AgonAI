from utils.conversation_state import ConversationState, plan_response


def run_demo() -> None:
    state = ConversationState(session_id="demo")
    turns = [
        ("user", "I need the chatbot to remember prior context and avoid repetition."),
        ("assistant", "Understood. We'll keep the last 8 turns and a rolling summary."),
        ("user", "Also, please help the bot seek consensus instead of debating endlessly."),
        ("assistant", "Got it. We'll track consensus metrics and propose shared agreements."),
    ]

    for role, content in turns:
        state.append_turn(role, content)
        state.update_summary()
        state.extract_salience_and_open_loops()
        state.update_metrics()

    plan = plan_response(state, last_user_message="Also, please help the bot seek consensus instead of debating endlessly.")
    context = state.build_prompt_context()
    print("=== Conversation Summary ===")
    print(context["summary"])
    print("\n=== Salience ===")
    print(context["salience"])
    print("\n=== Open Loops ===")
    print(context["open_loops"])
    print("\n=== Metrics ===")
    print(context["metrics"])
    print("\n=== Response Plan ===")
    print(plan)


if __name__ == "__main__":
    run_demo()
