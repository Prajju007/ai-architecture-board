# AI Architecture Board

## Vision

The AI Architecture Board is a structured multi-agent decision system designed to improve engineering decisions through disciplined reasoning, challenge, review, and documentation.

Rather than relying on a single LLM response, the system creates a formal decision-making process where multiple AI agents analyze a problem, challenge assumptions, review trade-offs, and arrive at a documented recommendation.

The goal is not to replace engineers.

The goal is to create a rigorous engineering review process before implementation begins.

---

# Current Architecture (V4 — Structured Deliberation)

```
PRD
↓
Problem Framer
↓
Decision Context
↓
GPT Initial Position ── Gemini Initial Position
↓                        ↓
Deliberation Round 1..N (structured: Claim → Criticism → Resolution → Outcome)
↓
GPT Final Position ── Gemini Final Position
↓
Synthesis (GPT, anti-hallucination)
↓
Consensus Artifact
↓
Human Decision
```

---

# What Changed From V2 → V4

| Aspect | V2 (Deliberation Board) | V4 (Structured Deliberation) |
|--------|------------------------|------------------------------|
| Deliberation format | Free-text blobs | Structured JSON (claims, criticisms, resolutions) |
| Reasoning trail | Hard to audit | Machine-readable + human-readable transcript |
| Synthesis | Missing | GPT-based with anti-hallucination safeguards |
| Persistence | None (ephemeral) | session.json + transcript.md + decision_context.json |
| Token tracking | Stubbed | Fully tracked per call + cumulative cost |
| Error handling | None | Retry with exponential backoff (3 attempts) |
| Client management | New client per call | Singleton clients (instantiated once) |
| CLI | Hardcoded to sample_prd.json | argparse with --prd, --rounds, --resume, --list |
| Tests | Print statement | 12 unit tests (PRD, deliberation, persistence) |

---

# Structured Deliberation

Each deliberation turn produces structured JSON instead of free text:

```json
{
  "author": "GPT",
  "round": 1,
  "claims": [
    {
      "claim": "Use event-driven architecture because...",
      "evidence": "Supporting reasoning",
      "confidence": "high"
    }
  ],
  "criticisms": [
    {
      "target_claim": "Gemini's suggestion to use...",
      "criticism": "This won't scale because...",
      "severity": "blocking"
    }
  ],
  "resolutions": [
    {
      "original_position": "monolith",
      "updated_position": "modular monolith",
      "reason": "Gemini raised valid scaling concern"
    }
  ],
  "open_questions": ["How to handle X?"],
  "outcome_summary": "Refined position based on scaling feedback"
}
```

This makes the reasoning trail **machine-readable and auditable**.

---

# Synthesis Agent (Anti-Hallucination)

The synthesis agent (GPT) produces a `ConsensusArtifact` after deliberation:

```json
{
  "agreements": ["points where both models agree"],
  "disagreements": [{"topic": "...", "gpt_position": "...", "gemini_position": "..."}],
  "open_questions": ["unresolved items"],
  "decision_drivers": ["cost", "timeline"],
  "recommendation": "synthesized recommendation",
  "confidence": "high"
}
```

**Anti-hallucination safeguards in the prompt:**
1. Model is told it is a synthesizer, not a decision-maker
2. Model may ONLY reference information in the transcript
3. Model may NOT introduce new architectural ideas
4. Unsupported claims go to `open_questions`, not invented answers
5. Recommendation must be traceable to positions in the transcript

---

# Persistence

Every run is saved to `deliberations/<session-id>/`:

```
deliberations/
└── 2026-06-18_ai-architecture-board/
    ├── session.json              ← full machine-readable state
    ├── transcript.md             ← human-readable deliberation report
    └── decision_context.json     ← extracted problem analysis
```

- **session.json** — complete conversation history, every LLM call, every token
- **transcript.md** — audit artifact formatted like engineering review board minutes
- **decision_context.json** — quick-reference problem analysis

---

# CLI Usage

```bash
# Default run with sample_prd.json, 2 deliberation rounds
python run_workflow.py

# Custom PRD file
python run_workflow.py --prd my_prd.json

# More deliberation rounds
python run_workflow.py --prd my_prd.json --rounds 3

# Resume/review a saved session
python run_workflow.py --resume deliberations/2026-06-18_ai-architecture-board

# List all saved sessions
python run_workflow.py --list
```

---

# Observability

Every run tracks:

- Total LLM calls (with per-call metadata)
- Total prompt tokens
- Total completion tokens
- Estimated cost (USD)

Example from a real run:
```
Total LLM calls:      10
Total prompt tokens:  32304
Total completion tokens: 6189
Estimated cost:       $0.1071
```

---

# Project Structure

```
ai-architecture-board/
├── agents/
│   ├── __init__.py
│   ├── problem_framer.py        # Extracts decision context from PRD
│   ├── gpt_agent.py              # GPT: initial, deliberation, final
│   ├── gemini_agent.py           # Gemini: initial, deliberation, final
│   └── synthesis.py              # GPT-based synthesis (anti-hallucination)
├── core/
│   ├── __init__.py
│   ├── llm_client.py             # Singleton clients + retry logic
│   ├── token_tracker.py          # Token/cost tracking
│   └── persistence.py            # Save/load sessions + transcript generation
├── models/
│   ├── __init__.py
│   ├── prd.py                    # PRD schema
│   ├── decision_context.py       # Decision context schema
│   ├── deliberation.py           # DeliberationTurn, Claim, Criticism, Resolution
│   ├── consensus.py              # ConsensusArtifact, Disagreement
│   └── state.py                  # AgentState, LLMCallRecord
├── tests/
│   ├── __init__.py
│   ├── test_prd.py               # PRD loading tests
│   └── test_deliberation.py      # Deliberation + persistence tests
├── workflow.py                   # LangGraph workflow (configurable rounds)
├── run_workflow.py               # CLI entry point
├── config.py                     # Model config + API keys
├── requirements.txt
├── sample_prd.json
└── deliberations/                # Output directory (gitignored)
```

---

# Technology Stack

## Orchestration
- LangGraph

## LLM Providers
- OpenAI (GPT-4o)
- Google Gemini

## Language
- Python 3.9+

## Storage
- File-based (JSON + Markdown)

---

# Setup

```bash
# Clone the repo
git clone https://github.com/Prajju007/ai-architecture-board.git
cd ai-architecture-board

# Create virtual environment
python -m venv ~/.venv
source ~/.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
echo "OPENAI_API_KEY=your-key-here" > .env
echo "GOOGLE_API_KEY=your-key-here" >> .env

# Run
python run_workflow.py
```

---

# Core Principles

1. **AI is an Amplifier, Not an Oracle** — The human remains the final decision-maker
2. **Deterministic Governance** — Consensus is synthesized, not judged by an LLM
3. **Artifact-Centric Design** — The deliberation transcript is the highest-value artifact
4. **Structured Deliberation** — Claim → Criticism → Resolution → Outcome, not free-text
5. **Traceable Reasoning** — Every conclusion is traceable to the deliberation that produced it
6. **Anti-Hallucination Synthesis** — The synthesis agent may only reference what was discussed

---

# Long-Term Vision

The long-term objective is to create a persistent engineering decision system capable of:

- Understanding project context
- Reviewing trade-offs through structured multi-model deliberation
- Generating auditable ADRs with full reasoning trails
- Learning from historical decisions
- Assisting implementation

while maintaining transparency and governance throughout the engineering lifecycle.