"""Persistence layer for deliberation sessions.

Saves each run as a structured session directory containing:
  - session.json   (full machine-readable state)
  - transcript.md  (human-readable deliberation report)
  - decision_context.json (extracted problem analysis)
"""

import json
import os
import datetime


def generate_session_id(prd_title: str) -> str:
    """Generate a filesystem-safe session ID from date + PRD title."""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_title = "".join(
        c if c.isalnum() or c in "-_" else "-" for c in prd_title.lower().strip()
    )
    # Collapse multiple dashes
    safe_title = "-".join(part for part in safe_title.split("-") if part)
    return f"{date_str}_{safe_title}"


def get_output_dir(session_id: str, base_dir: str = "deliberations") -> str:
    """Return the output directory path for a session, creating it if needed."""
    path = os.path.join(base_dir, session_id)
    os.makedirs(path, exist_ok=True)
    return path


def save_session(state: dict) -> str:
    """Save the full deliberation state to disk.

    Args:
        state: The complete AgentState dict after workflow completion.

    Returns:
        Path to the saved session directory.
    """
    session_id = state.get("session_id") or generate_session_id(
        state.get("prd", {}).get("title", "untitled")
    )
    output_dir = state.get("output_dir") or get_output_dir(session_id)

    os.makedirs(output_dir, exist_ok=True)

    # Save full session state
    session_path = os.path.join(output_dir, "session.json")
    with open(session_path, "w") as f:
        json.dump(state, f, indent=2, default=str)

    # Save decision context separately for quick reference
    if state.get("decision_context"):
        dc_path = os.path.join(output_dir, "decision_context.json")
        with open(dc_path, "w") as f:
            json.dump(state["decision_context"], f, indent=2, default=str)

    # Save human-readable transcript
    transcript_path = os.path.join(output_dir, "transcript.md")
    with open(transcript_path, "w") as f:
        f.write(generate_transcript(state))

    return output_dir


def load_session(session_path: str) -> dict:
    """Load a saved deliberation session from disk.

    Args:
        session_path: Path to the session.json file OR the session directory.

    Returns:
        The full AgentState dict.
    """
    if os.path.isdir(session_path):
        session_path = os.path.join(session_path, "session.json")
    with open(session_path, "r") as f:
        return json.load(f)


def generate_transcript(state: dict) -> str:
    """Generate a human-readable Markdown transcript of the deliberation.

    This is the audit artifact — formatted like engineering review board
    minutes, showing the full reasoning evolution.
    """
    lines = []
    prd = state.get("prd", {})
    dc = state.get("decision_context", {})

    # Header
    lines.append(f"# Deliberation Session: {prd.get('title', 'Untitled')}")
    lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Session ID: `{state.get('session_id', 'N/A')}`")
    lines.append("")

    # PRD summary
    lines.append("## PRD Summary")
    lines.append(f"**Problem:** {prd.get('problem_statement', 'N/A')}")
    lines.append(f"**Goals:** {', '.join(prd.get('goals', []))}")
    lines.append(f"**Constraints:** {', '.join(prd.get('constraints', []))}")
    lines.append("")

    # Decision Context
    if dc:
        lines.append("## Decision Context")
        for key, label in [
            ("facts", "Facts"),
            ("constraints", "Constraints"),
            ("assumptions", "Assumptions"),
            ("unknowns", "Unknowns"),
            ("risks", "Risks"),
            ("tradeoffs", "Trade-offs"),
            ("success_criteria", "Success Criteria"),
            ("open_questions", "Open Questions"),
        ]:
            items = dc.get(key, [])
            if items:
                lines.append(f"### {label}")
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")

    # Initial Positions
    lines.append("## Initial Positions")
    lines.append("### GPT")
    lines.append("```")
    lines.append(state.get("gpt_initial_position", "N/A"))
    lines.append("```")
    lines.append("")
    lines.append("### Gemini")
    lines.append("```")
    lines.append(state.get("gemini_initial_position", "N/A"))
    lines.append("```")
    lines.append("")

    # Deliberation Turns
    turns = state.get("deliberation_turns", [])
    if turns:
        lines.append("## Deliberation")
        lines.append("")
        for turn in turns:
            round_num = turn.get("round", "?")
            author = turn.get("author", "?")
            lines.append(f"### Round {round_num} — {author}")
            lines.append("")

            # Claims
            claims = turn.get("claims", [])
            if claims:
                lines.append("**Claims:**")
                for c in claims:
                    conf = c.get("confidence", "?")
                    lines.append(f"- [{conf.upper()}] {c.get('claim', '')}")
                    if c.get("evidence"):
                        lines.append(f"  - Evidence: {c['evidence']}")
                lines.append("")

            # Criticisms
            criticisms = turn.get("criticisms", [])
            if criticisms:
                lines.append("**Criticisms:**")
                for c in criticisms:
                    sev = c.get("severity", "?")
                    lines.append(f"- [{sev.upper()}] Target: {c.get('target_claim', '')}")
                    lines.append(f"  - {c.get('criticism', '')}")
                lines.append("")

            # Resolutions
            resolutions = turn.get("resolutions", [])
            if resolutions:
                lines.append("**Resolutions:**")
                for r in resolutions:
                    lines.append(f"- Changed: \"{r.get('original_position', '')}\"")
                    lines.append(f"  → \"{r.get('updated_position', '')}\"")
                    lines.append(f"  Reason: {r.get('reason', '')}")
                lines.append("")

            # Open questions
            oq = turn.get("open_questions", [])
            if oq:
                lines.append("**Open Questions:**")
                for q in oq:
                    lines.append(f"- {q}")
                lines.append("")

            # Outcome summary
            if turn.get("outcome_summary"):
                lines.append(f"**Outcome:** {turn['outcome_summary']}")
                lines.append("")

    # Final Positions
    lines.append("## Final Positions")
    lines.append("### GPT")
    lines.append("```")
    lines.append(state.get("gpt_final_position", "N/A"))
    lines.append("```")
    lines.append("")
    lines.append("### Gemini")
    lines.append("```")
    lines.append(state.get("gemini_final_position", "N/A"))
    lines.append("```")
    lines.append("")

    # Synthesis
    consensus = state.get("consensus_artifact")
    if consensus:
        lines.append("## Synthesis")
        if consensus.get("agreements"):
            lines.append("### Agreements")
            for a in consensus["agreements"]:
                lines.append(f"- {a}")
            lines.append("")

        if consensus.get("disagreements"):
            lines.append("### Disagreements")
            for d in consensus["disagreements"]:
                lines.append(f"- **{d.get('topic', '?')}**")
                lines.append(f"  - GPT: {d.get('gpt_position', '')}")
                lines.append(f"  - Gemini: {d.get('gemini_position', '')}")
            lines.append("")

        if consensus.get("open_questions"):
            lines.append("### Open Questions")
            for q in consensus["open_questions"]:
                lines.append(f"- {q}")
            lines.append("")

        if consensus.get("decision_drivers"):
            lines.append("### Decision Drivers")
            for d in consensus["decision_drivers"]:
                lines.append(f"- {d}")
            lines.append("")

        if consensus.get("recommendation"):
            lines.append("### Recommendation")
            lines.append(f"> {consensus['recommendation']}")
            lines.append(f"\n*Confidence: {consensus.get('confidence', '?')}*")
            lines.append("")

    # Observability footer
    lines.append("---")
    lines.append("## Run Metadata")
    lines.append(f"- Total LLM calls: {len(state.get('llm_calls', []))}")
    lines.append(f"- Total prompt tokens: {state.get('total_prompt_tokens', 0)}")
    lines.append(f"- Total completion tokens: {state.get('total_completion_tokens', 0)}")
    lines.append(f"- Estimated cost: ${state.get('estimated_cost', 0):.4f}")
    lines.append("")

    return "\n".join(lines)