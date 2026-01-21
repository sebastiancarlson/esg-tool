# Implementation Plan - CSRD Report Generation

## Phase 1: Core Logic
- [ ] Task: Create `modules/report_csrd.py` structure
    - [ ] Create the file and define the `generate_csrd_report` function signature.
- [ ] Task: Implement Data Aggregation
    - [ ] Write a function to query SQLite for Scope 1, 2, and 3 totals.
    - [ ] Create a dummy dataset for testing if DB is empty.
- [ ] Task: Implement Excel Export
    - [ ] Use Pandas `to_excel` to create a multi-sheet Excel file (Summary, Scope 1, Scope 2, Scope 3).
    - [ ] Format the Excel file with headers.

## Phase 2: UI Integration
- [x] Task: Update Streamlit Dashboard
    - [ ] Add a "Generate CSRD Report" button in the sidebar or a new tab.
    - [ ] Link the button to `generate_csrd_report`.
    - [ ] Provide a download button for the generated file.

## Phase 3: Verification
- [ ] Task: Manual Test
    - [ ] Run the app, click generate, and verify the Excel file opens and contains data.
