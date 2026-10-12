# Computer-Use Automation

A small end-to-end computer-use automation system demonstrating:

- LLM-driven UI discovery using Gemini
- Structured and versioned capability artifacts
- Deterministic replay without an LLM
- Runtime business-outcome handling
- Safety allowlists
- Sensitive-data redaction
- Evidence and structured logging
- Human-in-the-loop control transfer

## Architecture

The system follows this flow:

```text
Natural Language Goal
        |
        v
Gemini Discovery Agent
        |
        v
Live Browser / Playwright
        |
        v
Capability Artifact
        |
        v
Deterministic Replay
        |
        +----> SUCCESS + outputs
        |
        +----> BUSINESS_OUTCOME
        |
        +----> FAILURE / Human Handoff
```

The LLM is used for discovery only.

Production replay executes the saved capability deterministically without asking the model what action to perform.

## Project Structure

```text
demo_app/       Demo member-servicing application
src/            Core implementation
tests/          Executable demonstrations/tests
evidence/       Saved artifacts, logs, and screenshots
REPORT.md       Design decisions and trade-offs
```

## Requirements

- Python 3.10+
- Chromium
- Gemini API key

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows Command Prompt:

```bash
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Chromium:

```bash
playwright install chromium
```

## Gemini Configuration

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

`.env` is excluded from Git and must never be committed.

## Start the Demo Application

From the project root:

```bash
python demo_app/app.py
```

The application runs at:

```text
http://127.0.0.1:5000
```

Keep this terminal running.

## Demo 1 — Structured Artifact

In another terminal:

```bash
python -m tests.test_artifact
```

This creates:

```text
evidence/example_artifact.json
```

The artifact defines the capability contract, typed inputs and outputs, deterministic steps, locators, checkpoint, and policy constraints.

## Demo 2 — Browser Surface

Run:

```bash
python -m tests.test_surface
```

Playwright opens Chromium, searches for the demo member, and extracts the savings balance.

## Demo 3 — LLM Discovery

Run:

```bash
python -m tests.test_discovery
```

Gemini receives the natural-language goal and repeatedly performs:

```text
observe -> decide -> act
```

against the live UI.

Evidence is written to:

```text
evidence/discovery_run.json
evidence/discovery_success.png
```

## Demo 4 — Deterministic Replay

Run:

```bash
python -m tests.test_replay
```

This performs two demonstrations.

Successful lookup:

```text
member_id = 12345

SUCCESS
savings_balance = $2,450.75
```

Known business outcome:

```text
member_id = 99999

BUSINESS_OUTCOME
MEMBER_NOT_FOUND
```

Replay does not use Gemini or another LLM for decisions.

Inputs written to evidence logs are redacted.

## Demo 5 — Human Handoff

Run:

```bash
python -m tests.test_handoff
```

The automation deliberately pauses and transfers control:

```text
AUTOMATION
    |
    v
PAUSED
    |
    v
HUMAN
    |
    v
AUTOMATION
    |
    v
COMPLETE
```

Use the already-open browser manually and then press Enter in the terminal.

The browser is not restarted, demonstrating that human and automation operate the same live session.

Evidence is stored in:

```text
evidence/handoff_requested.png
evidence/handoff_resumed.png
evidence/handoff_log.json
```

## Safety

The implementation includes:

- Explicit domain allowlisting
- Explicit action allowlisting
- No credentials in capability artifacts
- Redacted member identifiers in replay logs
- Structured failures instead of blind continuation
- Human escalation seam for conditions automation should not resolve itself

The demo only performs reversible member lookup operations.

## Evidence

The `/evidence` directory contains evidence from actual runs, including:

```text
example_artifact.json
discovery_run.json
discovery_success.png
replay_success.json
replay_success.png
replay_not_found.json
replay_not_found.png
handoff_log.json
handoff_requested.png
handoff_resumed.png
```

## Important Design Principle

The model discovers.

The artifact captures what was learned.

Deterministic replay executes the capability in production.

This keeps routine execution predictable, reviewable, inexpensive, and independent of repeated LLM reasoning.