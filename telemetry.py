def update_telemetry(
    state,
    prompt_tokens,
    completion_tokens
):

    return {

        "total_prompt_tokens":
        state.get(
            "total_prompt_tokens",
            0
        ) + prompt_tokens,

        "total_completion_tokens":
        state.get(
            "total_completion_tokens",
            0
        ) + completion_tokens,

        "llm_calls":
        state.get(
            "llm_calls",
            0
        ) + 1
    }


def merge_updates(
    state,
    updates,
    prompt_tokens,
    completion_tokens
):

    telemetry = update_telemetry(
        state,
        prompt_tokens,
        completion_tokens
    )

    updates.update(
        telemetry
    )

    return updates