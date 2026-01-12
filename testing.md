# Testing Guide

This document describes a **lightweight testing approach** for validating the functionality of the desktop automation agent and its supporting scripts.

> **Important:** Testing focuses on **script behavior and system handling**, not AI model accuracy.  
> The underlying UI-TARS v1.5 (7B) model is **non-deterministic**, and variations in output are expected.

---

## Scope of Testing

The following components are covered:

- `run_agent_loop.py` – Executes multiple instructions from a file
- `run_with_arguments.py` – Executes a single instruction
- `prompt_optimiser.py` – Transforms high-level instructions into atomic steps
- Basic end-to-end integration between scripts

---

## Test Environment

### Prerequisites

- Python environment set up and activated
- Project dependencies installed
- Desktop environment available for UI automation

### Test Data

Prepare simple test inputs such as:

- A file with a single instruction
- A file with multiple instructions separated by empty lines
- An empty instruction file
- A file containing special characters

---

## Core Test Scenarios

### 1. Agent Loop (`run_agent_loop.py`)

**Basic execution**
- Run with a valid instruction file
- Verify:
  - Script executes without crashing
  - Session directories are created
  - Instructions are processed sequentially

**Error handling**
- Run without arguments
- Run with a non-existent file
- Run with an empty instruction file  
- Verify:
  - Clear error messages
  - Non-zero exit codes
  - No unhandled exceptions

**Interrupt handling**
- Start execution and press `Ctrl+C`
- Verify graceful shutdown and proper exit code

---

### 2. Single Instruction Execution (`run_with_arguments.py`)

**Valid execution**
- Run with a valid instruction
- Optionally include a session ID
- Verify:
  - Session directory is created
  - Log file is generated
  - Output is written to both console and log

**Argument validation**
- Run without instruction argument
- Verify argument parser errors and clean exit

**Interrupt handling**
- Interrupt execution with `Ctrl+C`
- Verify log file is closed properly and script exits cleanly

---

### 3. Prompt Optimiser (`prompt_optimiser.py`)

**Basic transformation**
- Provide a simple instruction
- Verify it is broken into atomic steps

**Complex instruction**
- Provide a multi-step instruction
- Verify logical ordering and step separation

**Edge cases**
- Instructions with special characters
- Empty input or invalid file path
- Verify:
  - Errors are handled gracefully
  - No crashes or silent failures

---

## Integration Testing

**End-to-end execution**
- Run `run_agent_loop.py` with multiple instructions
- Verify:
  - Each instruction triggers `run_with_arguments.py`
  - Separate session directories and logs are created
  - Failures stop execution appropriately

**Error propagation**
- Introduce a failing instruction
- Verify:
  - Error is surfaced clearly
  - Exit codes are consistent


## Disclaimer

This testing guide is intended for **developer validation and experimentation**.  
It does not replace formal QA, security review, or production readiness testing.
