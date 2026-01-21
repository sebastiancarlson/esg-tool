# Workflow

This file describes the ideal workflow. It is used to generate the `plan.md` for each track.

## Principles

- Test-Driven Development (TDD). Write tests before code.
- Commit changes after every task.
- Use Git Notes for task summaries.

## Phases

Each track is broken down into phases.

### Phase Completion Verification and Checkpointing Protocol

After each phase, execute the following protocol:

1.  **Code Review:** Ensure all code meets style guidelines and project standards.
2.  **Testing:** Verify all tests pass and coverage is maintained.
3.  **Documentation:** Update any relevant documentation.
4.  **Checkpoint:** Create a checkpoint commit with a clear message summarizing the phase.
5.  **User Manual Verification:** The user manual should be updated to reflect the current state of the feature set.

## Task Breakdown

Each phase consists of tasks. Each task is broken down into sub-tasks.

### Feature Task Template

1.  Write Tests
2.  Implement Feature

### Bug Fix Task Template

1.  Write Test (to reproduce bug)
2.  Fix Bug

### Refactor Task Template

1.  Analyze Code
2.  Write Tests (for new code or changed behavior)
3.  Refactor Code
4.  Verify Tests Pass

## Code Coverage

Required test code coverage: >80%
