# Class 11 Market Research Agent Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a classroom-ready Class 11 Market Research Agent module that accepts market evidence, runs structured analysis, and produces a ranked niche opportunity report.

**Architecture:** Implement the feature as a review-first workflow with a typed intake layer, modular analysis services, JSON-schema-validated outputs, and a page-level UI that lets users run each analysis step separately or as a full pipeline. Keep the MVP evidence-input-driven; do not depend on scraping or external paid APIs.

**Tech Stack:** TypeScript, React/Next.js-style page components, Zod or JSON Schema validation, Hermes skill orchestration layer, Vitest/Jest for unit tests, Playwright or RTL for UI tests.

---

## Current context / assumptions

This plan assumes a modern TypeScript web app or internal classroom app with:
- `src/app/` or `src/pages/` for routes/pages
- `src/components/` for React components
- `src/lib/` for orchestration, schema, and utilities
- `tests/` for unit/integration tests
- Hermes skill calls available through an internal server action or API layer

If the actual repo differs, keep the same file boundaries and rename paths to match the existing project layout.

---

## Target feature set

### MVP
1. Market brief form
2. Evidence block input
3. Pain-point analysis
4. Competitor gap analysis
5. Opportunity generation
6. Opportunity scoring
7. Final report rendering
8. JSON + markdown export

### Post-MVP
- save/load projects
- bilingual report mode
- instructor review mode
- future evidence connectors

---

## Proposed file structure

```text
src/
  app/
    class11/
      page.tsx
      loading.tsx
      error.tsx
      actions.ts
  components/
    class11/
      Class11Workspace.tsx
      MarketBriefForm.tsx
      EvidenceInputPanel.tsx
      EvidenceBlockEditor.tsx
      ActionToolbar.tsx
      PainClusterCards.tsx
      CompetitorMatrixTable.tsx
      OpportunityCards.tsx
      OpportunityScoringTable.tsx
      RecommendedNichePanel.tsx
      FinalReportView.tsx
      ExportButtons.tsx
      EmptyState.tsx
      AnalysisStatusBanner.tsx
  lib/
    class11/
      prompts/
        painPointPrompt.ts
        competitorGapPrompt.ts
        opportunityBriefPrompt.ts
        opportunityScorerPrompt.ts
        underservedNichePrompt.ts
        finalReportPrompt.ts
      schemas/
        marketBrief.ts
        evidenceBlock.ts
        painAnalysis.ts
        competitorAnalysis.ts
        opportunityAnalysis.ts
        scoring.ts
        finalReport.ts
      services/
        runPainPointAnalysis.ts
        runCompetitorGapAnalysis.ts
        runOpportunityBrief.ts
        runOpportunityScoring.ts
        runUnderservedNicheFinder.ts
        runFinalReport.ts
        runFullClass11Workflow.ts
      mappers/
        normalizeEvidence.ts
        reportToMarkdown.ts
        scoringRubric.ts
      types/
        index.ts
      constants/
        sourceTypes.ts
        defaultRubric.ts
      utils/
        evidenceQuality.ts
        extractQuotes.ts
        confidenceSummary.ts
        downloadJson.ts
        downloadMarkdown.ts
        classroomSummary.ts
  tests/
    class11/
      schemas/
        marketBrief.test.ts
        evidenceBlock.test.ts
        painAnalysis.test.ts
        competitorAnalysis.test.ts
        finalReport.test.ts
      services/
        runPainPointAnalysis.test.ts
        runCompetitorGapAnalysis.test.ts
        runOpportunityBrief.test.ts
        runOpportunityScoring.test.ts
        runFullClass11Workflow.test.ts
      components/
        MarketBriefForm.test.tsx
        EvidenceInputPanel.test.tsx
        FinalReportView.test.tsx
      e2e/
        class11-workflow.spec.ts
```

---

## API / action layer design

## Server actions or API endpoints

### `POST /api/class11/pain-points`
Request:
- marketBrief
- evidenceBlocks

Response:
- painAnalysis

### `POST /api/class11/competitors`
Request:
- marketBrief
- evidenceBlocks
- competitorNames

Response:
- competitorAnalysis

### `POST /api/class11/opportunities`
Request:
- marketBrief
- evidenceBlocks
- optional painAnalysis
- optional competitorAnalysis

Response:
- opportunityAnalysis

### `POST /api/class11/score`
Request:
- opportunities
- marketBrief
- optional founder constraints

Response:
- scoredOpportunities
- recommendedNiche

### `POST /api/class11/report`
Request:
- marketBrief
- evidenceBlocks
- painAnalysis
- competitorAnalysis
- opportunityAnalysis
- scoring

Response:
- finalReport
- markdown

### `POST /api/class11/full-workflow`
Request:
- marketBrief
- evidenceBlocks

Response:
- all module outputs

---

## Schema contracts

## `marketBrief.ts`
Validate:
- `businessTopic`: required string
- `targetAudience`: required string
- `geography`: optional string
- `marketGoal`: required string
- `competitors`: string[] default []
- `productCategory`: optional string
- `businessModel`: optional string
- `founderBackground`: optional string
- `constraints`: string[] default []

## `evidenceBlock.ts`
Validate:
- `id`: required string
- `sourceType`: enum (`customer_reviews`, `forum_posts`, `social_comments`, `competitor_copy`, `pricing_notes`, `interview_notes`, `other`)
- `sourceName`: required string
- `url`: optional string
- `tags`: string[] default []
- `rawText`: required string min length 20

## `painAnalysis.ts`
Validate:
- `painClusters`: array
- each cluster has `id`, `title`, `summary`, `evidenceQuotes[]`, `frequency`, `severity`, `rootCause`, `opportunityImplication`
- `summaryInsights`: string[]
- `evidenceQualityNote`: string

## `competitorAnalysis.ts`
Validate:
- `competitors[]`
- `competitorMatrix[]`
- `sharedPatterns[]`
- `underservedGaps[]`

## `opportunityAnalysis.ts`
Validate:
- `opportunities[]` length 1..5
- each opportunity has `id`, `title`, `type`, `targetCustomer`, `problemSolved`, `whyNow`, `differentiation`, `evidenceBasis[]`

## `scoring.ts`
Validate:
- `scoredOpportunities[]`
- exactly one `recommendedNiche`
- `scoringNotes[]`

## `finalReport.ts`
Validate:
- `title`
- `executiveSummary`
- `sections[]`
- `nextAction`
- `risksAndAssumptions`

---

## Prompt / service responsibilities

### `runPainPointAnalysis.ts`
- normalize evidence text
- reject empty evidence
- call Hermes with pain-point prompt
- validate JSON response
- derive evidence quality flag if needed

### `runCompetitorGapAnalysis.ts`
- separate competitor evidence from general evidence
- pass competitor names and notes
- validate structured competitor output

### `runOpportunityBrief.ts`
- merge pain + competitor context
- ask for 3–5 opportunities max
- require evidence basis for each

### `runOpportunityScoring.ts`
- apply default rubric
- validate every opportunity has score breakdown
- ensure one best recommendation

### `runFinalReport.ts`
- convert structured outputs into polished report JSON
- produce companion markdown through `reportToMarkdown.ts`

### `runFullClass11Workflow.ts`
- orchestrate all steps in order
- gracefully skip competitor step if no competitor info provided
- return partial failures with helpful UI-safe messages

---

## UI component responsibilities

### `Class11Workspace.tsx`
Container for all page state:
- market brief state
- evidence blocks state
- analysis outputs
- loading/error state
- export actions

### `MarketBriefForm.tsx`
Fields:
- business topic
- target audience
- geography
- market goal
- competitors
- founder background
- constraints

### `EvidenceInputPanel.tsx`
- add/remove evidence blocks
- group by source type
- inline validation
- paste-friendly textarea layout

### `ActionToolbar.tsx`
Buttons:
- Analyze pain points
- Compare competitors
- Find opportunities
- Score opportunities
- Generate final report
- Run full workflow

### `PainClusterCards.tsx`
Render each cluster with:
- title
- frequency
- severity
- sample quotes
- implication

### `CompetitorMatrixTable.tsx`
Columns:
- competitor
- target segment
- promise
- strengths
- weaknesses
- price level
- whitespace

### `OpportunityCards.tsx`
Render:
- title
- target customer
- problem solved
- why now
- evidence basis

### `OpportunityScoringTable.tsx`
Render numeric rubric and total scores.

### `RecommendedNichePanel.tsx`
Show:
- best niche
- why it won
- first validation step

### `FinalReportView.tsx`
Display classroom-ready markdown-like report with export controls.

### `ExportButtons.tsx`
Support:
- Export JSON
- Export Markdown
- Copy class summary

---

## Implementation tasks

### Task 1: Create shared Class 11 type definitions

**Objective:** Establish the canonical TS interfaces used across UI, services, and tests.

**Files:**
- Create: `src/lib/class11/types/index.ts`
- Test: `tests/class11/schemas/marketBrief.test.ts`

**Step 1: Write failing test**
Create a test that imports the main exported types and verifies schema-backed sample objects compile/validate.

**Step 2: Run test to verify failure**
Run: `pnpm test tests/class11/schemas/marketBrief.test.ts`
Expected: FAIL — missing module or exports.

**Step 3: Write minimal implementation**
Add exported interfaces/types for:
- `MarketBrief`
- `EvidenceBlock`
- `PainCluster`
- `PainAnalysis`
- `CompetitorProfile`
- `CompetitorAnalysis`
- `Opportunity`
- `ScoredOpportunity`
- `FinalReport`

**Step 4: Run test to verify pass**
Expected: PASS.

**Step 5: Commit**
`git commit -m "feat: add class11 shared types"`

---

### Task 2: Add schema validators for intake data

**Objective:** Ensure user input is validated before analysis begins.

**Files:**
- Create: `src/lib/class11/schemas/marketBrief.ts`
- Create: `src/lib/class11/schemas/evidenceBlock.ts`
- Test: `tests/class11/schemas/marketBrief.test.ts`
- Test: `tests/class11/schemas/evidenceBlock.test.ts`

**Step 1: Write failing tests**
Add tests for required fields, defaults, and invalid evidence block length.

**Step 2: Run tests to verify failure**
Run: `pnpm test tests/class11/schemas/marketBrief.test.ts tests/class11/schemas/evidenceBlock.test.ts`
Expected: FAIL.

**Step 3: Write minimal implementation**
Implement Zod/JSON schema validators and helper parse functions.

**Step 4: Run tests to verify pass**
Expected: PASS.

**Step 5: Commit**
`git commit -m "feat: add class11 intake schemas"`

---

### Task 3: Add analysis output schemas

**Objective:** Validate every AI response before it reaches the UI.

**Files:**
- Create: `src/lib/class11/schemas/painAnalysis.ts`
- Create: `src/lib/class11/schemas/competitorAnalysis.ts`
- Create: `src/lib/class11/schemas/opportunityAnalysis.ts`
- Create: `src/lib/class11/schemas/scoring.ts`
- Create: `src/lib/class11/schemas/finalReport.ts`
- Tests under `tests/class11/schemas/`

**Step 1:** Write failing tests using valid and invalid sample payloads.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement schema validators and export parse helpers.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: add class11 analysis schemas"`

---

### Task 4: Add prompt builders

**Objective:** Centralize prompt text and output requirements.

**Files:**
- Create: `src/lib/class11/prompts/painPointPrompt.ts`
- Create: `src/lib/class11/prompts/competitorGapPrompt.ts`
- Create: `src/lib/class11/prompts/opportunityBriefPrompt.ts`
- Create: `src/lib/class11/prompts/opportunityScorerPrompt.ts`
- Create: `src/lib/class11/prompts/underservedNichePrompt.ts`
- Create: `src/lib/class11/prompts/finalReportPrompt.ts`
- Test: `tests/class11/services/runPainPointAnalysis.test.ts`

**Step 1:** Write failing snapshot/unit tests asserting prompts include JSON-only instructions and key fields.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement prompt builder functions.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: add class11 prompt builders"`

---

### Task 5: Add evidence normalization utilities

**Objective:** Clean pasted text before sending it to Hermes.

**Files:**
- Create: `src/lib/class11/mappers/normalizeEvidence.ts`
- Create: `src/lib/class11/utils/evidenceQuality.ts`
- Create: `src/lib/class11/utils/extractQuotes.ts`
- Test: `tests/class11/services/runPainPointAnalysis.test.ts`

**Step 1:** Write failing tests for trimming, dropping blank blocks, and evidence quality messaging.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement utilities.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: add class11 evidence normalization utilities"`

---

### Task 6: Implement pain-point analysis service

**Objective:** Turn validated evidence into a schema-safe pain analysis result.

**Files:**
- Create: `src/lib/class11/services/runPainPointAnalysis.ts`
- Test: `tests/class11/services/runPainPointAnalysis.test.ts`

**Step 1:** Write failing tests for successful parse, schema rejection, and weak evidence handling.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement service logic and Hermes call wrapper.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: implement class11 pain analysis service"`

---

### Task 7: Implement competitor gap analysis service

**Objective:** Generate competitor comparison results from competitor notes.

**Files:**
- Create: `src/lib/class11/services/runCompetitorGapAnalysis.ts`
- Test: `tests/class11/services/runCompetitorGapAnalysis.test.ts`

**Step 1:** Write failing tests.
**Step 2:** Run tests.
**Step 3:** Implement service.
**Step 4:** Re-run tests.
**Step 5:** Commit.
`git commit -m "feat: implement class11 competitor analysis service"`

---

### Task 8: Implement opportunity generation service

**Objective:** Produce 3–5 evidence-grounded opportunities.

**Files:**
- Create: `src/lib/class11/services/runOpportunityBrief.ts`
- Test: `tests/class11/services/runOpportunityBrief.test.ts`

**Step 1:** Write failing tests for max length, evidence basis, and fallback to available analyses.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement service.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: implement class11 opportunity generation service"`

---

### Task 9: Implement scoring rubric and scoring service

**Objective:** Rank opportunities and choose one recommended niche.

**Files:**
- Create: `src/lib/class11/constants/defaultRubric.ts`
- Create: `src/lib/class11/mappers/scoringRubric.ts`
- Create: `src/lib/class11/services/runOpportunityScoring.ts`
- Test: `tests/class11/services/runOpportunityScoring.test.ts`

**Step 1:** Write failing tests for weights, one recommendation rule, and output validation.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement scoring.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: implement class11 opportunity scoring"`

---

### Task 10: Implement final report generator

**Objective:** Combine module outputs into a polished final report and markdown export.

**Files:**
- Create: `src/lib/class11/services/runFinalReport.ts`
- Create: `src/lib/class11/mappers/reportToMarkdown.ts`
- Create: `src/lib/class11/utils/classroomSummary.ts`
- Test: `tests/class11/schemas/finalReport.test.ts`
- Test: `tests/class11/services/runFullClass11Workflow.test.ts`

**Step 1:** Write failing tests for required sections and markdown rendering.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement final report service + markdown mapper.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: implement class11 final report generation"`

---

### Task 11: Implement full workflow orchestrator

**Objective:** Support a one-click classroom experience.

**Files:**
- Create: `src/lib/class11/services/runFullClass11Workflow.ts`
- Test: `tests/class11/services/runFullClass11Workflow.test.ts`

**Step 1:** Write failing end-to-end service tests.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement orchestrator with graceful optional competitor handling.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: implement class11 full workflow orchestrator"`

---

### Task 12: Add page-level actions/API layer

**Objective:** Expose backend operations to the UI.

**Files:**
- Create: `src/app/class11/actions.ts`
- Optionally create API route files if the app does not use server actions
- Test: `tests/class11/services/runFullClass11Workflow.test.ts`

**Step 1:** Write failing action tests or integration tests.
**Step 2:** Run tests.
**Step 3:** Implement actions.
**Step 4:** Re-run tests.
**Step 5:** Commit.
`git commit -m "feat: add class11 page actions"`

---

### Task 13: Build market brief and evidence input UI

**Objective:** Let students enter inputs without friction.

**Files:**
- Create: `src/components/class11/MarketBriefForm.tsx`
- Create: `src/components/class11/EvidenceInputPanel.tsx`
- Create: `src/components/class11/EvidenceBlockEditor.tsx`
- Create: `src/components/class11/EmptyState.tsx`
- Test: `tests/class11/components/MarketBriefForm.test.tsx`
- Test: `tests/class11/components/EvidenceInputPanel.test.tsx`

**Step 1:** Write failing UI tests.

**Step 2:** Run tests.
Expected: FAIL.

**Step 3:** Implement components.

**Step 4:** Re-run tests.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: add class11 intake components"`

---

### Task 14: Build analysis result components

**Objective:** Render outputs clearly for teaching use.

**Files:**
- Create: `src/components/class11/PainClusterCards.tsx`
- Create: `src/components/class11/CompetitorMatrixTable.tsx`
- Create: `src/components/class11/OpportunityCards.tsx`
- Create: `src/components/class11/OpportunityScoringTable.tsx`
- Create: `src/components/class11/RecommendedNichePanel.tsx`
- Create: `src/components/class11/AnalysisStatusBanner.tsx`
- Test: `tests/class11/components/FinalReportView.test.tsx`

**Step 1:** Write failing UI tests for rendering and empty states.
**Step 2:** Run tests.
**Step 3:** Implement components.
**Step 4:** Re-run tests.
**Step 5:** Commit.
`git commit -m "feat: add class11 analysis result components"`

---

### Task 15: Build final report and export UI

**Objective:** Let students and instructors use the result immediately.

**Files:**
- Create: `src/components/class11/FinalReportView.tsx`
- Create: `src/components/class11/ExportButtons.tsx`
- Create: `src/lib/class11/utils/downloadJson.ts`
- Create: `src/lib/class11/utils/downloadMarkdown.ts`
- Test: `tests/class11/components/FinalReportView.test.tsx`

**Step 1:** Write failing tests for report rendering and export behavior.
**Step 2:** Run tests.
**Step 3:** Implement view + export utilities.
**Step 4:** Re-run tests.
**Step 5:** Commit.
`git commit -m "feat: add class11 report and export UI"`

---

### Task 16: Assemble the page workspace

**Objective:** Combine intake, actions, and result panels into one classroom page.

**Files:**
- Create: `src/components/class11/Class11Workspace.tsx`
- Create: `src/app/class11/page.tsx`
- Create: `src/app/class11/loading.tsx`
- Create: `src/app/class11/error.tsx`
- Test: `tests/class11/e2e/class11-workflow.spec.ts`

**Step 1:** Write failing integration/E2E test for the happy path.

**Step 2:** Run test.
Expected: FAIL.

**Step 3:** Implement composed page.

**Step 4:** Re-run test.
Expected: PASS.

**Step 5:** Commit.
`git commit -m "feat: add class11 workspace page"`

---

### Task 17: Add seeded demo data for teaching

**Objective:** Make live teaching reliable with a preloaded sample case.

**Files:**
- Create: `src/lib/class11/constants/demoCase.ts`
- Modify: `src/components/class11/Class11Workspace.tsx`
- Test: `tests/class11/e2e/class11-workflow.spec.ts`

**Step 1:** Write failing test for loading demo data.
**Step 2:** Run test.
**Step 3:** Implement seeded example.
**Step 4:** Re-run test.
**Step 5:** Commit.
`git commit -m "feat: add class11 demo case"`

---

### Task 18: Final QA pass

**Objective:** Verify the classroom flow is stable.

**Files:**
- No new product files required
- Update tests as needed

**Verification commands:**
- `pnpm test tests/class11 --runInBand`
- `pnpm lint`
- `pnpm typecheck`
- `pnpm playwright test tests/class11/e2e/class11-workflow.spec.ts`

**Expected:** All pass.

**Commit:**
`git commit -m "test: verify class11 workflow stability"`

---

## UX / content rules for implementation

- Always show a short summary before long details.
- Every opportunity card must display its evidence basis.
- If evidence is sparse, label the result as lower confidence.
- Avoid raw note dumps in the final report.
- Limit opportunities to 5 max.
- Always produce one best recommendation.

---

## Risks / tradeoffs

### Risk 1: Over-generic outputs
Mitigation:
- enforce evidence basis arrays
- require niche specificity in prompts

### Risk 2: Weak pasted evidence
Mitigation:
- add evidence quality warning
- allow partial workflow but block overconfident summaries

### Risk 3: Prompt drift / malformed JSON
Mitigation:
- strict schema validation
- retry wrapper or safe parse fallback

### Risk 4: Classroom UI overload
Mitigation:
- use step-based panels
- include “Run full workflow” and also manual step buttons

---

## Open questions

1. Should save/load be MVP or Phase 2?
2. Should the final report be English-only, Chinese-only, or bilingual by default?
3. Does the existing teaching site prefer page-local server actions or generic API routes?
4. Is there an existing export system to plug into instead of local download helpers?

---

## Done definition

The feature is done when:
- a student can paste market evidence into Class 11
- Hermes returns pain clusters, competitor analysis, opportunities, scoring, and a final report
- one recommended niche is clearly identified
- the final report can be exported in markdown and JSON
- the full demo can be run reliably in class
