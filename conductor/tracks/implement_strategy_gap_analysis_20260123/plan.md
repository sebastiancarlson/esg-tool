# Implementation Plan: Strategy & GAP Analysis

- [ ] Task: Database Updates
    - [ ] Sub-task: Create `f_GAP_Analysis` table.
    - [ ] Sub-task: Create `f_DMA_IRO` table.
    - [ ] Sub-task: Populate `f_ESRS_Requirements` with more detailed list (E1-E5, S1-S4, G1).
- [x] Task: Backend Modules (`modules/governance.py` & `modules/dma_tool.py`)
    - [x] Sub-task: Functions to update/get GAP status.
    - [x] Sub-task: Functions to add/get IROs for DMA topics.
    - [x] Sub-task: Update Readiness Score calculation to use real GAP data instead of mock.
- [x] Task: UI Implementation (`dashboard.py`)
    - [x] Sub-task: Build "GAP-analys" view (maybe separate from Strategy or sub-tab).
    - [x] Sub-task: Upgrade "Väsentlighet (DMA)" view to allow drilling down into topics.
    - [x] Sub-task: Visualize GAP progress (Progress bar).
