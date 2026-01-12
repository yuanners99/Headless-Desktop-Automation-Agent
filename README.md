# Desktop Automation Agent

## Overview

This repository contains a **Python-based desktop automation agent** built on top of the **UI-TARS v1.5 (7B) multimodal UI interaction model**. The project explores how large UI-capable models can be used to drive **scriptable, headless desktop automation** without relying on heavyweight desktop clients or manual intervention.

The agent is designed to interpret high-level task instructions, reason over the current screen state, and execute corresponding UI actions in a repeatable and extensible manner.

---

## Key Ideas

- **CLI-first automation**  
  The agent is designed to run entirely from the command line, making it suitable for server-side execution and integration into larger automation pipelines.

- **Model-driven UI interaction**  
  Instead of hard-coded selectors or brittle UI rules, the system relies on a UI interaction model to reason about screen state and determine the next action.

- **Prompt-centric control layer**  
  A dedicated prompt engineering module converts human-readable instructions into structured prompts optimised for UI reasoning and action selection.

- **Workflow-friendly execution**  
  The agent can be executed non-interactively, enabling orchestration by external automation or scheduling tools.

---

## Architecture Overview

The agent mirrors the core logic of the UI-TARS desktop system, but without the GUI. Its components include:

- **Prompt Layer** – Constructs structured prompts for UI-TARS reasoning.
- **Action Parser** – Converts model output into executable desktop actions.
- **Agent Core** – Manages state, retries, and execution loop.
- **Desktop Controller** – Executes UI actions (mouse, keyboard, window focus) via PyAutoGUI.
- **CLI Wrappers** – `run_with_arguments.py` for single instructions and `run_agent_loop.py` for batch execution.

This modular design keeps **decision-making model-driven** while maintaining **deterministic execution** at the system level.

---

## How It Works

At a high level, the automation loop follows this pattern:

1. Capture the current screen state
2. Construct a structured prompt using task instructions and screen context
3. Invoke the **UI-TARS v1.5 (7B)** model
4. Parse the model’s response into executable actions
5. Perform the corresponding desktop interactions
6. Repeat until the task is completed

---

## Core Components

- `desktop_agent_core.py` – Main agent loop and state management
- `prompts.py` – System and user prompt definitions for UI-TARS
- `action_parser.py` – Converts model output into structured actions
- `desktop_controller.py` – Executes UI actions on the desktop
- `run_with_arguments.py` – CLI entry point for single instructions
- `run_agent_loop.py` – Batch instruction orchestrator

---

## Exit Codes

The scripts use consistent exit codes for integration and orchestration:

| Code | Meaning | Notes |
|-----:|--------|-------|
| 0 | Success | Instruction completed successfully |
| 1 | User intervention required | Model requested manual action |
| 2 | Agent error | Parsing or execution failure |
| 3 | Authentication required | OTP / mobile input needed |
| 130 | User cancelled | Ctrl+C (CLI only) |

---

## Example Workflow

A typical automated run may involve:

- Initialising a clean execution environment
- Loading task-specific context or input data
- Interpreting a high-level instruction
- Driving UI navigation via UI-TARS reasoning
- Extracting structured information from the UI
- Returning results or execution status

Task-specific logic is intentionally abstracted to keep the framework reusable.
---

## Design Goals

- Minimise tight coupling to any single UI or application
- Avoid brittle, pixel-perfect automation logic
- Favour modularity and composability
- Enable easy experimentation with prompt strategies and model behaviour

---

## Limitations

- This is a **proof-of-concept implementation**, not a production-hardened system
- UI automation remains inherently sensitive to layout and rendering changes
- Additional safeguards would be required for large-scale or long-running workloads

---

## Notes

All proprietary systems, credentials, datasets, and business-specific logic have been removed or abstracted.  
This repository focuses solely on the **technical approach, architecture, and automation strategy**.

---

## Disclaimer

This project is provided for demonstration and experimentation purposes only. It is not intended for direct production use without further testing, security review, and operational hardening.
