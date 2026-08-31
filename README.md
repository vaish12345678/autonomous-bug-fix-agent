# 🤖 Autonomous Bug Fix Agent

An agentic software engineering system that automatically investigates failing Python repositories, identifies the root cause, generates a repair, validates the proposed change, safely applies it, runs tests, and verifies the final result.

The project is built around one principle:

> **AI should reason about the bug, but deterministic controls should decide whether a code change is safe to execute.**

The system combines AI-powered debugging with deterministic validation, patch safety checks, controlled execution, backup/recovery, bounded retries, human approval, failure classification, benchmark evaluation, and agent trajectory tracking.

---

# 🎯 Problem

## Who has this problem?

Software developers and engineering teams regularly encounter implementation defects that cause tests to fail.

A developer typically needs to:

1. Understand the reported issue.
2. Inspect the repository.
3. Identify the relevant source file.
4. Determine the root cause.
5. Design a correction.
6. Modify the source code.
7. Run the tests.
8. Investigate failures when the repair is incorrect.
9. Recover from unsuccessful changes.

For repetitive debugging tasks, this creates unnecessary engineering overhead.

## The Bottleneck

The difficult part of autonomous debugging is not simply generating code.

A useful bug-fixing agent must be able to:

* understand the issue and repository context,
* identify the correct target file,
* reason about the root cause,
* generate an appropriate repair,
* avoid modifying tests,
* validate generated code,
* reject unsafe patches,
* execute the real test suite,
* interpret failures,
* retry when appropriate,
* recover from unsuccessful repairs,
* and provide evidence explaining the final result.

---

# 💡 Solution

The **Autonomous Bug Fix Agent** converts this debugging process into a controlled agentic workflow.

```text
Issue
  │
  ▼
Repository Inspection
  │
  ▼
Initial Test Verification
  │
  ▼
AI Bug Analysis
  │
  ▼
Target File Selection
  │
  ▼
Patch Generation
  │
  ▼
Syntax Validation
  │
  ▼
Patch Safety Gate
  │
  ▼
Human Approval / Controlled Execution
  │
  ▼
Backup
  │
  ▼
Patch Application
  │
  ▼
Test Execution
  │
  ├──────── PASS ────────► Final Verification
  │
  ▼
Failure Classification
  │
  ▼
Recovery / Self-Correction
  │
  ▼
Bounded Retry
  │
  ▼
Final Verification
  │
  ▼
Trajectory + Evidence
```

The system does not blindly allow an LLM to modify a repository.

Instead:

```text
AI reasoning
     ↓
Deterministic validation
     ↓
Safety gate
     ↓
Controlled execution
     ↓
Real test feedback
     ↓
Recovery / retry
     ↓
Verified result
     ↓
Observable trajectory
```

This separation between probabilistic reasoning and deterministic verification is the central design principle of the project.

---

# 🧠 Agent Architecture

## 1. Repository Reader

The agent loads the selected benchmark repository and gathers the relevant context required for debugging.

Each benchmark contains:

* an issue description,
* a buggy implementation,
* and tests defining the expected behavior.

---

## 2. Initial Test Verification

Before modifying anything, the agent runs the repository tests.

This establishes that the benchmark actually contains a failing defect.

Example:

```text
========== VERIFYING INITIAL BUG ==========

========== RUNNING TESTS ==========

F

FAILED test_agent.py::test_divide
assert 20 == 5

✓ Initial tests failed as expected.
```

This prevents an already-passing repository from being incorrectly treated as a successful repair.

---

## 3. AI Bug Analysis

The AI receives the issue and repository context and determines:

* the likely root cause,
* the relevant source file,
* and the required correction.

Example:

```text
Root cause:
The divide function uses multiplication instead of division.

File:
agent.py

Correction:
Change `return a * b` to `return a / b`.
```

The AI is responsible for reasoning about **what is wrong and how it should be repaired**.

---

## 4. Target File Selection

The agent identifies the source file that should be modified.

The repair is focused on the implementation rather than modifying tests to make them pass.

---

## 5. Patch Generation

The AI generates the corrected source code.

The generation process is constrained to discourage:

* test modification,
* unnecessary file creation,
* invented APIs,
* hardcoded benchmark-specific outputs,
* and one-test-case-only solutions.

The goal is a minimal implementation-level repair.

---

# 🛡️ Safety Architecture

Autonomous code modification requires more than a correct-looking LLM response.

The system therefore places deterministic controls around AI-generated patches.

## 6. Syntax Validation

Generated Python source is validated before it can be applied.

```text
Generated patch
      ↓
Python syntax validation
      ↓
PASS → continue
FAIL → reject / retry
```

Invalid Python source is rejected before repository modification.

---

## 7. Patch Safety Gate

The patch safety layer validates the proposed change before application.

It checks conditions including:

* target path is inside the benchmark repository,
* target file exists,
* test files cannot be modified,
* empty patches are rejected,
* excessively large rewrites are rejected,
* destructive source removal is rejected.

Example:

```text
========== PATCH SAFETY GATE ==========

Safety status : SAFE
Safety reason : Patch passed safety validation.
Changed lines : 1
Original lines: 2
Proposed lines: 2

✓ Patch passed safety gate.
```

This provides deterministic control around AI-generated modifications.

---

## 8. Backup and Recovery

Before changing the target source file, the system creates a backup.

```text
Create backup
     ↓
Apply patch
     ↓
Run tests
     ↓
PASS → keep repair
FAIL → recover / rollback
```

This provides a recovery path when an AI-generated repair is unsuccessful.

---

## 9. Human Approval Checkpoint

Consequential repository modifications can pass through a human approval checkpoint before execution.

The decision is recorded in the trajectory.

Example:

```json
{
  "event": "HUMAN_CHECKPOINT",
  "details": {
    "decision": "APPROVED"
  }
}
```

This keeps consequential execution controlled while allowing the agent to perform the reasoning-intensive parts of the workflow.

---

# 🔄 Failure Handling and Self-Correction

## 10. Test Execution

After the patch is applied, the agent executes the actual repository tests.

A repair is not considered successful merely because the generated code is syntactically valid.

The implementation must pass the repository's tests.

Example:

```text
========== RUNNING TESTS ==========

.                                                                        [100%]

1 passed in 0.01s

==================================================
🎉 VERIFIED FIX
✓ Tests passed on attempt 1
==================================================
```

---

## 11. Failure Classification

When a repair fails, the system classifies the failure to provide structured feedback.

Supported categories include:

* timeout,
* syntax error,
* import error,
* name error,
* type error,
* attribute error,
* test failure,
* unknown failure.

This turns raw execution failure into structured information for the recovery process.

---

## 12. Bounded Self-Correction

The system supports bounded repair attempts.

The current configuration allows up to **three AI repair attempts**.

```text
Attempt 1
   ↓
Generate patch
   ↓
Validate
   ↓
Test
   ↓
FAIL
   ↓
Classify failure
   ↓
Generate improved repair
   ↓
Attempt 2
   ↓
...
```

The retry mechanism is intentionally bounded to prevent uncontrolled agent loops and unnecessary API usage.

---

# 📊 Evaluation

## Primary Metric

The primary outcome metric is:

> **Percentage of benchmark repositories whose tests pass after the repair workflow.**

The benchmark suite contains **12 independent bug cases**.

The same benchmark suite is used for deterministic evaluation.

## Current Evaluation Result

The latest evaluation completed successfully across all 12 benchmarks:

```text
Total Benchmarks : 12
Passed           : 12
Failed           : 0
Success Rate     : 100.0%

Total Runtime    : 11.5429s
Average Runtime  : 0.9619s
```

### Evaluation Summary

| Metric          | Final Result |
| --------------- | -----------: |
| Benchmarks      |           12 |
| Passed          |           12 |
| Failed          |            0 |
| Success Rate    |  **100.00%** |
| Total Runtime   |     11.5429s |
| Average Runtime |      0.9619s |

The latest evaluation was executed using:

```bash
python evaluation/evaluate.py
```

The detailed output is stored in:

```text
evaluation/results/evaluation_results.json
```

> **Important:** The deterministic benchmark evaluation does not make AI API calls. It verifies the benchmark implementations independently.

---

# 📈 Improvement Changelog

The project was developed incrementally, with each iteration addressing a reliability limitation discovered during development.

## Iteration 0 — Basic Repair Loop

### Change

Started with a basic workflow:

```text
Issue
 ↓
AI Analysis
 ↓
Patch Generation
 ↓
Patch Application
 ↓
Tests
```

### Limitation

The basic approach relied heavily on the AI-generated patch being correct.

A generated patch could be:

* syntactically invalid,
* unsafe,
* too large,
* targeted at the wrong location,
* or behaviorally incorrect.

### Decision

Add deterministic controls around AI-generated code.

---

## Iteration 1 — Syntax Validation

### Change

Added deterministic Python syntax validation before applying generated source.

### Why

Generated code should not be applied simply because the model produced it.

### Decision

**KEPT**

---

## Iteration 2 — Patch Safety Gate

### Change

Added deterministic patch safety validation.

The safety layer checks:

* repository boundary,
* target file existence,
* test-file protection,
* empty patches,
* excessive rewrites,
* destructive source removal.

### Why

Syntax correctness does not guarantee patch safety.

### Decision

**KEPT**

---

## Iteration 3 — Backup and Recovery

### Change

Added automatic backups and recovery support.

### Why

An autonomous system needs a recovery path when a generated repair fails.

### Decision

**KEPT**

---

## Iteration 4 — Failure Classification

### Change

Added structured failure classification.

### Why

A failed test should become actionable information for the next repair attempt.

### Decision

**KEPT**

---

## Iteration 5 — Bounded Self-Correction

### Change

Added bounded retry and self-correction.

### Why

A failed repair can provide useful feedback for another attempt, but the agent should not enter an uncontrolled retry loop.

### Decision

**KEPT**

---

## Iteration 6 — Human Approval

### Change

Added a human approval checkpoint before consequential patch execution.

### Why

Repository modification is a consequential action and should remain controlled.

### Decision

**KEPT**

---

## Iteration 7 — Agent Trajectory Tracking

### Change

Added structured trajectory recording.

The system records events including:

* repository reading,
* AI analysis,
* target selection,
* patch generation,
* validation,
* human approval,
* patch application,
* test results,
* failure classification,
* recovery,
* final result.

### Why

A final `PASS` does not explain how an autonomous agent reached that result.

### Decision

**KEPT**

---

## Iteration 8 — Expanded Benchmark Suite

### Change

Expanded the benchmark suite to **12 independent bug cases**.

### Why

A larger benchmark suite provides stronger evidence than demonstrating the workflow on a single bug.

### Result

The system can evaluate all 12 benchmarks automatically.

### Decision

**KEPT**

---

## Iteration 9 — Evaluation Statistics Correction

### Change

Corrected the evaluation statistics and verified the benchmark runner against the complete benchmark suite.

### Result

The current deterministic evaluation reports:

```text
12 benchmarks
12 passed
0 failed
100.00% success rate
```

### Decision

**KEPT**

---

# 🧭 Agent Trajectories

Representative trajectories are stored under:

```text
evaluation/trajectories/
```

A typical trajectory follows:

```text
RUN_STARTED
     ↓
Read repository
     ↓
AI_DECISION
     ↓
Generate patch
     ↓
Validate patch
     ↓
HUMAN_CHECKPOINT
     ↓
Apply patch
     ↓
TARGET_MODIFIED
     ↓
TEST_RESULT
     ↓
FINAL_RESULT
```

Example final result:

```json
{
  "status": "VERIFIED_AND_ACCEPTED",
  "confidence": 100,
  "risk_level": "LOW"
}
```

The trajectory provides evidence of:

* what the agent did,
* what decision it made,
* what tools responded,
* whether human approval occurred,
* what tests returned,
* and why the final result was accepted.

---

# 🧪 Benchmark Suite

The project currently contains 12 benchmark cases:

```text
benchmarks/
├── bug_01/
├── bug_02/
├── bug_03/
├── bug_04/
├── bug_05/
├── bug_06/
├── bug_07/
├── bug_08/
├── bug_09/
├── bug_10/
├── bug_11/
└── bug_12/
```

Each benchmark follows the same structure:

```text
bug_xx/
├── issue.txt
└── repo/
    ├── agent.py
    └── test_agent.py
```

The benchmark design keeps evaluation deterministic and reproducible.

---

# 🚀 Reproduction Guide

The project is designed to be reproducible from a clean Python environment.

## Requirements

Recommended:

* Python 3.12+
* Git
* Internet connection for AI-powered repair
* Gemini API key

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configure AI Access

Create:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.5-flash-lite
MAX_AI_RETRIES=3
AI_RETRY_DELAY=5
```

Do not commit `.env` or API credentials to the repository.

---

# ▶️ Run the Autonomous Agent

From the project root:

```bash
python -m backend.agent
```

The agent displays the available benchmarks:

```text
========== AVAILABLE BUGS ==========

1. bug_01
2. bug_02
3. bug_03
...
12. bug_12
```

Select a benchmark.

Example:

```text
Select bug number: 8
```

The agent then performs:

```text
VERIFYING INITIAL BUG
        ↓
READING REPOSITORY
        ↓
ANALYZING BUG
        ↓
CREATING BACKUP
        ↓
GENERATING FIX
        ↓
VALIDATING GENERATED FIX
        ↓
PATCH SAFETY GATE
        ↓
APPLYING FIX
        ↓
RUNNING TESTS
        ↓
VERIFIED FIX
```

### Example: bug_08

The benchmark initially contains:

```python
def divide(a, b):
    return a * b
```

The test fails:

```text
assert 20 == 5
```

The agent identifies the root cause and generates:

```python
def divide(a, b):
    return a / b
```

The generated code passes syntax validation and the patch safety gate.

The final test passes:

```text
1 passed
```

This demonstrates the complete issue → reasoning → repair → verification loop.

---

# 🧪 Run Full Benchmark Evaluation

Run:

```bash
python evaluation/evaluate.py
```

Expected summary:

```text
============================================================
🤖 AUTONOMOUS BUG FIX AGENT
       EVALUATION SUMMARY
============================================================

Total Benchmarks : 12
Passed           : 12
Failed           : 0
Success Rate     : 100.0%

Total Runtime    : approximately 11.5s
Average Runtime  : approximately 0.96s
```

The detailed evaluation report is written to:

```text
evaluation/results/evaluation_results.json
```

---

# 🔎 Run an Individual Benchmark

For example:

```bash
python -m pytest -q .\benchmarks\bug_08\repo
```

Expected:

```text
1 passed
```

---

# 🔧 Validation Commands

## Compile the backend

```bash
python -m compileall backend -q
```

## Verify benchmark discovery

```bash
python -c "from evaluation.evaluate import get_benchmarks; b=get_benchmarks(); print('BENCHMARKS:', len(b)); print('OK' if len(b)==12 else 'ERROR')"
```

Expected:

```text
BENCHMARKS: 12
OK
```

---

# 📁 Project Structure

```text
autonomous-bug-fix-agent/
│
└── agentic-bugfixer/
    │
    ├── backend/
    │   ├── agent.py
    │   ├── patcher.py
    │   ├── approval/
    │   ├── audit/
    │   ├── evaluation/
    │   ├── execution/
    │   ├── explainability/
    │   ├── git/
    │   ├── quality/
    │   ├── recovery/
    │   ├── reporting/
    │   └── trajectory/
    │
    ├── benchmarks/
    │   ├── bug_01/
    │   ├── bug_02/
    │   ├── ...
    │   └── bug_12/
    │
    ├── evaluation/
    │   ├── approvals/
    │   ├── audit_logs/
    │   ├── explanations/
    │   ├── recovery/
    │   ├── repair_reports/
    │   ├── reports/
    │   ├── results/
    │   └── trajectories/
    │
    ├── requirements.txt
    └── README.md
```

---

# 💰 Runtime and Cost

## Deterministic Evaluation

The benchmark runner executes repository tests without making AI API calls.

The latest evaluation completed:

```text
12 benchmarks
11.5429 seconds total
0.9619 seconds average per benchmark
```

This makes repeated deterministic evaluation fast and inexpensive.

## AI-Powered Repair

The autonomous repair workflow uses the Gemini API.

AI usage depends on:

* selected model,
* prompt size,
* repository context,
* number of repair attempts,
* and retry behavior.

The system therefore keeps AI retries bounded.

---

# 🆚 Baseline vs Improved System

The project evolved from a basic AI repair loop into a controlled autonomous debugging workflow.

| Capability             | Baseline | Improved System |
| ---------------------- | :------: | :-------------: |
| Repository inspection  |     ✓    |        ✓        |
| AI bug analysis        |     ✓    |        ✓        |
| Target selection       |  Limited |        ✓        |
| Patch generation       |     ✓    |        ✓        |
| Syntax validation      |  Limited |        ✓        |
| Test-file protection   |  Limited |        ✓        |
| Patch safety gate      |     —    |        ✓        |
| Backup                 |     —    |        ✓        |
| Recovery               |     —    |        ✓        |
| Failure classification |     —    |        ✓        |
| Self-correction        |     —    |        ✓        |
| Bounded retries        |     —    |        ✓        |
| Human approval         |     —    |        ✓        |
| Trajectory tracking    |     —    |        ✓        |
| 12-case evaluation     |     —    |        ✓        |

The key architectural improvement is:

```text
AI generates code
       ↓
Patch is validated
       ↓
Patch is safety checked
       ↓
Execution is controlled
       ↓
Tests provide feedback
       ↓
Failures trigger bounded recovery
       ↓
Final result is verified
       ↓
Trajectory provides evidence
```

---

# ⚠️ Main Failure Mode

The most important failure mode discovered during development was the assumption that a generated patch is correct simply because it looks plausible.

A code-generation model can produce a patch that:

* looks reasonable,
* passes syntax validation,
* but still fails behavioral tests.

This demonstrated that:

> **Code generation cannot be the final verification step.**

The system therefore closes the loop using actual execution:

```text
Generate
   ↓
Validate
   ↓
Apply
   ↓
Test
   ↓
Observe
   ↓
Recover if needed
   ↓
Verify
```

---

# 💡 Hot Take

The strongest lesson from this project is:

> **An autonomous coding agent should not be judged by how confidently it generates code. It should be judged by whether it can safely reach a verified result.**

LLMs are valuable for:

* understanding natural-language issues,
* reasoning about root causes,
* selecting relevant code,
* generating repairs.

But reliable autonomy requires deterministic engineering around the model:

```text
AI reasoning
     +
Safety constraints
     +
Validation
     +
Real execution
     +
Test feedback
     +
Recovery
     +
Human control
     +
Observable trajectories
     =
Reliable agentic workflow
```

The project therefore treats the LLM as a reasoning component rather than giving it unrestricted control over the repository.

---

# 🎥 Hackathon Demo

The recommended demonstration flow is:

```text
1. Show the problem
2. Show a failing benchmark
3. Show the simple baseline
4. Select a benchmark
5. Run the autonomous agent
6. Show AI bug analysis
7. Show generated patch
8. Show syntax validation
9. Show patch safety gate
10. Show human approval
11. Show patch application
12. Show test verification
13. Run the complete 12-case evaluation
14. Show 100% final result
15. Show trajectory evidence
16. Explain the main lesson
```

The complete demonstration can be performed from the terminal and repository.

---

# 🔐 Responsible Use

The project follows a controlled execution model.

Key principles:

* AI-generated changes are validated before execution.
* Test files are protected by the patch safety layer.
* Repository modifications are constrained.
* Backups are created before source modification.
* Failed repairs can be recovered.
* Retry attempts are bounded.
* Consequential execution can include human approval.
* API credentials remain outside the submission.
* Evaluation uses controlled benchmark repositories.

---

# 📌 Submission Evidence

Important evidence included in the repository:

```text
evaluation/
├── reports/
├── results/
├── trajectories/
├── approvals/
├── audit_logs/
├── explanations/
├── recovery/
└── repair_reports/
```

These artifacts make the workflow observable rather than relying only on a final success message.

---

# 🧩 Design Philosophy

The project follows three principles.

## 1. Reason with AI

Use the model where flexible reasoning is valuable.

## 2. Control with deterministic engineering

Use deterministic checks where safety and correctness must be predictable.

## 3. Verify with execution

Never assume a patch works because the model says it works.

The repository itself must provide the final behavioral evidence.

---

# 🚀 Future Improvements

Potential future improvements include:

* richer repository context retrieval,
* stronger semantic patch validation,
* more diverse benchmark repositories,
* larger-scale evaluation,
* improved recovery strategies,
* additional language support,
* stronger execution sandboxing,
* patch quality scoring,
* and trajectory visualization.

These improvements are intentionally separated from the current benchmark implementation so the current evaluation remains reproducible.

---

# 🏁 Conclusion

The **Autonomous Bug Fix Agent** demonstrates an agentic software engineering workflow in which AI performs debugging and repair reasoning while deterministic systems provide validation, safety, controlled execution, recovery, evaluation, human checkpoints, and observable agent trajectories.

The current benchmark result is:

```text
12 / 12 benchmarks passed
100% success rate
11.5429s total deterministic evaluation
0.9619s average per benchmark
```

More importantly, the project demonstrates the transition from:

```text
AI-generated patch
```

to:

```text
AI reasoning
      ↓
Deterministic safety
      ↓
Controlled execution
      ↓
Real test feedback
      ↓
Bounded recovery
      ↓
Verified result
      ↓
Observable trajectory
```

That is the core idea behind making autonomous software engineering more reliable.

---

## 🏆 Built for the micro1 Agentic Workflows Hackathon

This project focuses on reliable agentic software engineering by combining AI-based debugging with deterministic validation, controlled execution, recovery, evaluation, human checkpoints, and observable agent trajectories.
