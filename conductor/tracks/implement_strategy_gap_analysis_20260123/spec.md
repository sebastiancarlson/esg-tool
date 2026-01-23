# Specification: Advanced CSRD Strategy & GAP Analysis

## 1. Overview
This module upgrades the "Strategy" section to become a fully compliant CSRD management tool. It introduces a GAP Analysis tool to track ESRS data point readiness and enhances the Double Materiality Assessment (DMA) with IRO (Impact, Risk, Opportunity) documentation.

## 2. Goals
- **GAP Analysis Tool:** Interactive checklist for all ESRS disclosure requirements (E1-G1), tracking status (Not Started, In Progress, Compliant) and linking to evidence.
- **Enhanced DMA:** Add ability to document *why* a topic is material, linking it to specific Impacts, Risks, and Opportunities (IROs).
- **Stakeholder Module:** Simple register to log stakeholder engagement (who, when, key concerns).

## 3. Data Model

### 3.1 GAP Analysis (`f_GAP_Analysis`)
| Column | Type | Description |
|---|---|---|
| `esrs_code` | TEXT | PK, Foreign Key to `f_ESRS_Requirements` (e.g., "E1-1") |
| `status` | TEXT | "Not Started", "In Progress", "Compliant", "N/A" |
| `owner` | TEXT | Person responsible (e.g., "CFO") |
| `evidence_link` | TEXT | Link to document or internal data |
| `notes` | TEXT | Action plan or comments |
| `last_updated` | TEXT | Date |

### 3.2 Enhanced DMA (`f_DMA_IRO`)
*Links to existing `f_DMA_Materiality`.*
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | PK |
| `dma_topic_id` | INTEGER | FK to `f_DMA_Materiality` |
| `type` | TEXT | "Impact", "Risk", "Opportunity" |
| `description` | TEXT | Description of the IRO |
| `time_horizon` | TEXT | "Short", "Medium", "Long" |
| `financial_effect` | TEXT | Qualitative or Quantitative estimate |

## 4. User Interface
- **GAP Analysis Tab:**
    - Table view of all ESRS requirements.
    - Status pills (Red/Yellow/Green).
    - Edit modal to update status and add notes.
    - Progress bar: "CSRD Readiness %".
- **Strategy Tab (Upgraded):**
    - Click on a bubble in the DMA matrix to open detailed view.
    - Add/Edit IROs for each topic.

## 5. Logic
- **Readiness Score:** Calculated as `(Compliant + N/A) / Total Requirements`.
