"""CLI entry point for the AI Architecture Board.

Usage:
  python run_workflow.py                              # uses sample_prd.json, 2 rounds
  python run_workflow.py --prd my_prd.json            # custom PRD
  python run_workflow.py --prd my_prd.json --rounds 3 # more deliberation rounds
  python run_workflow.py --resume deliberations/2026-06-18_xxx/session.json
  python run_workflow.py --list                       # list saved sessions
"""

import argparse
import json
import os
import sys
import glob

from workflow import build_graph
from core.persistence import generate_session_id, get_output_dir, save_session, load_session


def list_sessions(base_dir: str = "deliberations"):
    """Print all saved deliberation sessions."""
    if not os.path.isdir(base_dir):
        print("No saved sessions found.")
        return

    sessions = sorted(glob.glob(os.path.join(base_dir, "*", "session.json")))
    if not sessions:
        print("No saved sessions found.")
        return

    print("Saved Deliberation Sessions:")
    print("=" * 60)
    for path in sessions:
        session_dir = os.path.dirname(path)
        try:
            with open(path, "r") as f:
                state = json.load(f)
            title = state.get("prd", {}).get("title", "Unknown")
            cost = state.get("estimated_cost", 0)
            print(f"  {session_dir}")
            print(f"    Title: {title}")
            print(f"    Cost:  ${cost:.4f}")
            print()
        except (json.JSONDecodeError, IOError):
            print(f"  {session_dir} (error reading session)")


def print_results(result: dict):
    """Print the deliberation results to console in a readable format."""
    print("\n" + "=" * 60)
    print("DECISION CONTEXT")
    print("=" * 60 + "\n")
    print(json.dumps(result.get("decision_context", {}), indent=2))

    print("\n" + "=" * 60)
    print("GPT INITIAL POSITION")
    print("=" * 60 + "\n")
    print(result.get("gpt_initial_position", "N/A"))

    print("\n" + "=" * 60)
    print("GEMINI INITIAL POSITION")
    print("=" * 60 + "\n")
    print(result.get("gemini_initial_position", "N/A"))

    print("\n" + "=" * 60)
    print("DELIBERATION")
    print("=" * 60 + "\n")

    for turn in result.get("deliberation_turns", []):
        author = turn.get("author", "?")
        round_num = turn.get("round", "?")
        print(f"\n--- Round {round_num}: {author} ---\n")

        if turn.get("claims"):
            print("Claims:")
            for c in turn["claims"]:
                print(f"  [{c.get('confidence', '?').upper()}] {c.get('claim', '')}")
                if c.get("evidence"):
                    print(f"    Evidence: {c['evidence']}")
            print()

        if turn.get("criticisms"):
            print("Criticisms:")
            for c in turn["criticisms"]:
                print(f"  [{c.get('severity', '?').upper()}] {c.get('criticism', '')}")
            print()

        if turn.get("resolutions"):
            print("Resolutions:")
            for r in turn["resolutions"]:
                print(f"  {r.get('original_position', '')} → {r.get('updated_position', '')}")
                print(f"    Reason: {r.get('reason', '')}")
            print()

        if turn.get("open_questions"):
            print("Open Questions:")
            for q in turn["open_questions"]:
                print(f"  - {q}")
            print()

        if turn.get("outcome_summary"):
            print(f"Outcome: {turn['outcome_summary']}\n")

    print("\n" + "=" * 60)
    print("GPT FINAL POSITION")
    print("=" * 60 + "\n")
    print(result.get("gpt_final_position", "N/A"))

    print("\n" + "=" * 60)
    print("GEMINI FINAL POSITION")
    print("=" * 60 + "\n")
    print(result.get("gemini_final_position", "N/A"))

    consensus = result.get("consensus_artifact")
    if consensus:
        print("\n" + "=" * 60)
        print("SYNTHESIS")
        print("=" * 60 + "\n")

        if consensus.get("agreements"):
            print("Agreements:")
            for a in consensus["agreements"]:
                print(f"  - {a}")
            print()

        if consensus.get("disagreements"):
            print("Disagreements:")
            for d in consensus["disagreements"]:
                print(f"  {d.get('topic', '?')}")
                print(f"    GPT:    {d.get('gpt_position', '')}")
                print(f"    Gemini: {d.get('gemini_position', '')}")
            print()

        if consensus.get("open_questions"):
            print("Open Questions:")
            for q in consensus["open_questions"]:
                print(f"  - {q}")
            print()

        if consensus.get("decision_drivers"):
            print("Decision Drivers:")
            for d in consensus["decision_drivers"]:
                print(f"  - {d}")
            print()

        if consensus.get("recommendation"):
            print(f"Recommendation: {consensus['recommendation']}")
            print(f"Confidence: {consensus.get('confidence', '?')}")

    # Observability footer
    print("\n" + "=" * 60)
    print("RUN METADATA")
    print("=" * 60 + "\n")
    print(f"Total LLM calls:      {len(result.get('llm_calls', []))}")
    print(f"Total prompt tokens:  {result.get('total_prompt_tokens', 0)}")
    print(f"Total completion tokens: {result.get('total_completion_tokens', 0)}")
    print(f"Estimated cost:       ${result.get('estimated_cost', 0):.4f}")


def main():
    parser = argparse.ArgumentParser(
        description="AI Architecture Board — Multi-model structured deliberation system"
    )
    parser.add_argument(
        "--prd",
        default="sample_prd.json",
        help="Path to the PRD JSON file (default: sample_prd.json)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=2,
        help="Number of deliberation rounds (default: 2)",
    )
    parser.add_argument(
        "--resume",
        metavar="SESSION_PATH",
        help="Resume a saved deliberation session (path to session.json or session dir)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all saved deliberation sessions",
    )
    args = parser.parse_args()

    # List sessions mode
    if args.list:
        list_sessions()
        return

    # Resume mode — load and reprint a saved session
    if args.resume:
        print(f"Loading session from: {args.resume}")
        state = load_session(args.resume)
        print_results(state)
        return

    # Normal run mode
    if not os.path.isfile(args.prd):
        print(f"Error: PRD file not found: {args.prd}")
        sys.exit(1)

    with open(args.prd, "r") as f:
        prd = json.load(f)

    session_id = generate_session_id(prd.get("title", "untitled"))
    output_dir = get_output_dir(session_id)

    print(f"AI Architecture Board")
    print(f"PRD: {args.prd}")
    print(f"Session: {session_id}")
    print(f"Deliberation rounds: {args.rounds}")
    print(f"Output: {output_dir}")
    print()

    initial_state = {
        "prd": prd,
        "session_id": session_id,
        "rounds": args.rounds,
        "decision_context": {},
        "gpt_initial_position": "",
        "gemini_initial_position": "",
        "deliberation_turns": [],
        "gpt_final_position": "",
        "gemini_final_position": "",
        "consensus_artifact": {},
        "llm_calls": [],
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "estimated_cost": 0.0,
        "output_dir": output_dir,
    }

    # Build graph with requested number of rounds
    graph = build_graph(rounds=args.rounds)

    result = graph.invoke(initial_state)

    # Print results
    print_results(result)

    # Persist to disk
    saved_dir = save_session(result)
    print(f"\n{'=' * 60}")
    print(f"Session saved to: {saved_dir}")
    print(f"  - session.json")
    print(f"  - transcript.md")
    print(f"  - decision_context.json")
    print("=" * 60)


if __name__ == "__main__":
    main()