# Class 11 Developer Build Spec + Student Lesson Plan

> **For Hermes:** This is a planning-only document for building and teaching Class 11: AI Product Selection / Market Research Agent.

**Goal:** Define both (1) the developer-facing implementation blueprint and (2) the student/instructor-facing lesson flow for a classroom-ready Class 11 module.

**Architecture:** Build Class 11 as a review-first, input-driven analysis workflow. Students provide market context and evidence, Hermes runs modular skills for pain-point analysis, competitor comparison, opportunity generation, and scoring, then outputs a structured final report. The teaching experience mirrors the product workflow so students learn by operating the same modules they will later reuse.

**Tech Stack:** Hermes skill orchestration, structured JSON outputs, markdown report rendering, optional classroom UI module, optional persistence/export layer.

---

# Part 1 — Developer Build Spec

## 1. Product Summary

### Module name
`class11-market-research-agent`

### Purpose
Help students and instructors convert raw market evidence into:
- pain-point clusters
- competitor gap analysis
- underserved niche ideas
- ranked product/service opportunities
- a final market opportunity brief

### Core principle
Do not make the MVP depend on live scraping. The first version should work reliably from pasted evidence.

---

## 2. System Architecture

### Input layer
Collect:
- market brief
- evidence blocks
- competitor notes
- optional founder constraints

### Analysis layer
Orchestrate these reusable skills/modules:
1. `pain-point-cluster-analysis`
2. `competitor-gap-analysis`
3. `market-opportunity-brief`
4. `opportunity-scorer`
5. `underserved-niche-finder`
6. `class11-final-report-polisher`

### Presentation layer
Render:
- cards
- tables
- ranked shortlist
- final markdown report

### Optional persistence layer
Store projects and outputs for student reuse and instructor review.

---

## 3. Recommended Repository / Module Structure

If this is added to a web app or internal Hermes classroom system, use a structure like:

```text
class11-market-research-agent/
  README.md
  docs/
    class11-spec.md
    prompts/
      pain-point-cluster-analysis.md
      competitor-gap-analysis.md
      market-opportunity-brief.md
      opportunity-scorer.md
      underserved-niche-finder.md
      final-report-polisher.md
    schemas/
      market-brief.schema.json
      evidence-block.schema.json
      pain-analysis.schema.json
      competitor-analysis.schema.json
      opportunity-analysis.schema.json
      final-report.schema.json
  skills/
    pain-point-cluster-analysis.md
    competitor-gap-analysis.md
    market-opportunity-brief.md
    opportunity-scorer.md
    underserved-niche-finder.md
    class11-final-report-polisher.md
  src/
    intake/
      marketBrief.ts
      evidenceValidator.ts
    analysis/
      runPainPointAnalysis.ts
      runCompetitorAnalysis.ts
      runOpportunityGeneration.ts
      runOpportunityScoring.ts
      runUnderservedNicheFinder.ts
      buildFinalReport.ts
    scoring/
      scoringRubric.ts
      scoreNormalizer.ts
    ui/
      Class11Page.tsx
      MarketBriefForm.tsx
      EvidenceInputPanel.tsx
      PainClusterCards.tsx
      CompetitorMatrix.tsx
      OpportunityCards.tsx
      ScoringTable.tsx
      FinalReportPanel.tsx
    types/
      market.ts
      evidence.ts
      pain.ts
      competitor.ts
      opportunity.ts
      report.ts
    utils/
      extractEvidenceQuotes.ts
      summarizeConfidence.ts
      exportMarkdown.ts
      exportJson.ts
  tests/
    intake/
    analysis/
    scoring/
    ui/
```

If the classroom environment is prompt/skill-first instead of app-first, keep the same conceptual split even if file locations differ.

---

## 4. Data Contracts

## 4.1 MarketBrief
```json
{
  "business_topic": "AI tools for small law firms",
  "target_audience": "solo and small law firms",
  "geography": "US",
  "market_goal": "find underserved service/product opportunities",
  "competitors": ["Clio", "MyCase", "Smokeball"],
  "product_category": "legal operations software",
  "business_model": "SaaS or productized service",
  "founder_background": "strong in AI automation",
  "constraints": ["small budget", "fast MVP preferred"]
}
```

## 4.2 EvidenceBlock
```json
{
  "id": "ev-001",
  "source_type": "customer_reviews",
  "source_name": "G2 reviews for Clio",
  "url": "",
  "tags": ["billing", "setup", "small firm"],
  "raw_text": "Setup is complicated and billing workflows are hard to customize."
}
```

## 4.3 PainAnalysis
```json
{
  "pain_clusters": [
    {
      "id": "complex-onboarding",
      "title": "Complex onboarding and setup",
      "summary": "Users struggle to configure the system without expert help.",
      "evidence_quotes": [
        "Setup took days and required support.",
        "Too hard to configure for a small team."
      ],
      "frequency": "high",
      "severity": "high",
      "root_cause": "The product assumes advanced admin knowledge.",
      "opportunity_implication": "There is room for a simpler guided setup experience."
    }
  ],
  "summary_insights": [
    "Customers repeatedly complain about time-to-value.",
    "Complexity is a stronger pain than missing features."
  ],
  "evidence_quality_note": "Moderate evidence quality based on repeated review themes."
}
```

## 4.4 CompetitorAnalysis
```json
{
  "competitors": [
    {
      "name": "Clio",
      "positioning": "All-in-one legal practice management platform",
      "target_segment": "small to mid-size law firms",
      "strengths": ["broad features", "strong brand recognition"],
      "weaknesses": ["complexity", "premium pricing", "heavy setup"],
      "pricing_impression": "premium",
      "moat": "brand trust and mature product breadth",
      "customer_frustration_areas": ["setup", "customization", "cost"],
      "messaging_gaps": ["little emphasis on simplicity for solo firms"],
      "product_gaps": ["lightweight AI-first workflow assistant"]
    }
  ],
  "competitor_matrix": [],
  "shared_patterns": [
    "Incumbents are broad and complex.",
    "Ease-of-use is under-emphasized."
  ],
  "underserved_gaps": [
    "Solo firms wanting narrow workflow automation without full-suite complexity."
  ]
}
```

## 4.5 Opportunity
```json
{
  "id": "opp-001",
  "title": "AI intake assistant for solo law firms",
  "type": "AI automation service",
  "target_customer": "solo law firms",
  "problem_solved": "manual intake and client qualification",
  "why_now": "firms want efficiency but full systems feel too heavy",
  "differentiation": "simple setup, lower cost, narrow workflow focus",
  "evidence_basis": [
    "repeated complaints about setup complexity",
    "price dissatisfaction",
    "manual intake workflow friction"
  ],
  "scores": {
    "demand_signal": 4,
    "competition_advantage": 3,
    "monetization_potential": 4,
    "speed_to_launch": 5,
    "execution_feasibility": 4,
    "founder_fit": 4,
    "content_seo_potential": 4,
    "ai_automation_fit": 5
  },
  "total_score": 33,
  "verdict": "best first niche",
  "reasoning": "Strong repeated pain and a narrow MVP path."
}
```

## 4.6 FinalReport
```json
{
  "title": "Class 11 Market Opportunity Brief",
  "executive_summary": "The strongest first niche is AI-assisted intake for solo law firms.",
  "sections": [
    {"title": "Business context", "content": "..."},
    {"title": "Top pain points", "content": "..."},
    {"title": "Competitor snapshot", "content": "..."}
  ],
  "next_action": "Validate the top niche with 5 customer interviews or pilot outreach."
}
```

---

## 5. Skill Specifications

## 5.1 `pain-point-cluster-analysis`

### Input
- market brief
- target audience
- evidence blocks

### Output
- `pain_clusters[]`
- `summary_insights[]`
- `evidence_quality_note`

### Rules
- Use only provided evidence.
- Merge semantically similar complaints.
- Quote real customer wording where possible.
- Label frequency and severity qualitatively.
- Admit weak evidence.

### Prompt stub
```text
You are a market research analyst extracting recurring customer pain points from raw evidence.
Analyze only the provided evidence.
Group similar complaints into structured clusters.
Return JSON only.
```

---

## 5.2 `competitor-gap-analysis`

### Input
- market brief
- target audience
- competitor names
- competitor evidence blocks

### Output
- `competitors[]`
- `competitor_matrix[]`
- `shared_patterns[]`
- `underserved_gaps[]`

### Rules
- Describe each competitor fairly.
- Stay evidence-grounded.
- Separate facts from inference.
- Identify gaps that matter commercially.

---

## 5.3 `market-opportunity-brief`

### Input
- market brief
- evidence blocks
- optional pain analysis
- optional competitor analysis

### Output
- market summary
- opportunity shortlist
- opportunity rationale
- recommended niche
- validation plan

### Rules
- Prefer specific niches over broad markets.
- Recommend max 5 opportunities.
- Recommend one best first move.

---

## 5.4 `opportunity-scorer`

### Input
- opportunities[]
- scoring rubric
- founder constraints

### Output
- scored opportunities[]
- recommended niche
- scoring notes

### Default weights
- demand_signal: 20%
- competition_advantage: 15%
- monetization_potential: 15%
- speed_to_launch: 15%
- execution_feasibility: 10%
- founder_fit: 10%
- content_seo_potential: 5%
- ai_automation_fit: 10%

---

## 5.5 `underserved-niche-finder`

### Input
- pain analysis
- competitor analysis
- market brief

### Output
- underserved niches[]
- why underserved
- test angle

### Detection heuristics
- strong pain + weak solution
- expensive incumbents + simpler alternative
- ignored subsegment
- manual workflow + automation fit
- broad incumbents + niche unmet need

---

## 5.6 `class11-final-report-polisher`

### Input
- outputs from previous modules

### Output
- polished markdown report
- optional Chinese summary
- optional presentation summary

### Rules
- Avoid raw note dumps.
- Explain why the recommendation won.
- Surface assumptions and next steps.

---

## 6. Orchestration Flow

### One-click full workflow
1. Validate market brief
2. Validate at least one evidence block exists
3. Run pain-point analysis
4. Run competitor analysis if competitor evidence exists
5. Run opportunity generation
6. Run opportunity scoring
7. Optionally run underserved niche finder
8. Build final report
9. Render report and exports

### Partial workflow support
Allow users to run modules individually:
- pain-point only
- competitor only
- opportunities only
- final report only

---

## 7. UI Specification

## 7.1 Main Page
Title: `Class 11 — AI Market Research Agent`

### Panel A — Market Brief
Fields:
- business / market topic
- target audience
- geography
- market goal
- competitors
- founder strengths / constraints

### Panel B — Evidence Input
Sections/tabs:
- reviews
- forums / social
- competitor copy
- pricing notes
- interview notes
- other notes

### Panel C — Actions
Buttons:
- Analyze pain points
- Compare competitors
- Find opportunities
- Score opportunities
- Generate final report
- Run full workflow

### Panel D — Results
Blocks:
- pain cluster cards
- competitor matrix
- opportunity cards
- scoring table
- best niche recommendation

### Panel E — Export
Buttons:
- copy markdown
- export JSON
- export classroom summary
- save project

---

## 8. UX Requirements

- Accept messy pasted text.
- Show concise summaries before details.
- Use expandable evidence quotes.
- Show `insufficient evidence` when data is thin.
- Never imply data was scraped if it was pasted.
- Do not surface raw chain-of-thought.
- Keep the student-facing language practical and teachable.

---

## 9. Validation Rules

## Market brief validation
- `business_topic` required
- `target_audience` required
- `market_goal` required
- optional fields allowed empty

## Evidence validation
- at least one evidence block required
- minimum non-whitespace content threshold
- warn if evidence is too short for reliable clustering

## Output validation
- maximum 5 opportunities
- exactly 1 recommended niche
- every recommendation must include evidence basis
- final report must include risks and next action

---

## 10. Testing Strategy

## Unit tests
- evidence normalization
- scoring calculations
- rubric weighting
- empty/invalid input handling
- JSON schema validation

## Integration tests
- market brief + evidence -> pain analysis
- market brief + competitor notes -> competitor analysis
- full workflow -> final report
- weak evidence -> guarded output with assumptions

## UI tests
- form validation
- add/remove evidence blocks
- button states
- results rendering
- export button behavior

## Acceptance tests
- demo case completes end-to-end in one classroom session
- output contains 3–5 opportunities
- output names one best niche
- output includes validation plan

---

## 11. Phased Build Plan

## Phase 1 — MVP
Build:
1. market brief form
2. evidence input
3. pain-point skill
4. competitor gap skill
5. opportunity brief skill
6. final report renderer

## Phase 2 — Decision quality
Build:
1. opportunity scorer
2. underserved niche finder
3. ranking table
4. recommendation logic refinement

## Phase 3 — Student operations
Build:
1. save/load project
2. export JSON/markdown
3. bilingual option
4. instructor mode

## Phase 4 — Stretch
Build later:
- live research connectors
- scraping helpers
- CRM handoff
- landing page handoff
- SEO/content handoff
- presentation export

---

## 12. Developer Acceptance Criteria

The build is complete when:
- a student can submit market context and evidence
- the app/skill flow returns structured pain clusters
- competitor analysis is evidence-grounded
- 3–5 opportunities are generated
- opportunities are ranked
- one recommended niche is returned
- final report is readable and exportable

---

# Part 2 — Student-Facing Class 11 Lesson Plan

## 1. Lesson Title
**Class 11 — AI 选品 / 市场研究 Agent**

## 2. Lesson Promise
By the end of this class, students will be able to use Hermes to turn real market evidence into a shortlist of business opportunities and choose one niche to test first.

## 3. Learning Objectives
Students will learn how to:
1. define a market clearly
2. collect useful customer evidence
3. identify repeated pain points
4. compare competitors strategically
5. find underserved opportunities
6. rank ideas instead of chasing random inspiration
7. decide on one practical next step

---

## 4. Class Duration
Recommended: **90 minutes**

### Suggested breakdown
- 10 min: introduction and framing
- 15 min: evidence collection principles
- 15 min: live Hermes demo — pain points
- 15 min: live Hermes demo — competitors
- 15 min: live Hermes demo — opportunities + ranking
- 15 min: student exercise
- 5 min: presentations / wrap-up

Optional compressed version: 60 minutes.

---

## 5. Required Materials
Students need:
- one market idea or business topic
- 3–5 pieces of raw evidence
- optional competitor list
- access to Hermes or the classroom interface

Examples of evidence:
- review snippets
- Reddit/forum discussions
- YouTube comment snippets
- copied competitor copy
- pricing notes
- customer interview notes

---

## 6. Teaching Narrative

### Key message
Most people choose businesses from intuition alone. Better founders choose markets by studying pain, competition, and unmet demand.

### Instructor framing line
“Today we are not trying to guess a good business idea. We are using AI to read the market more clearly and choose a niche with evidence.”

---

## 7. Instructor Demo Flow

## Step 1 — Pick a sample market
Use one relatable example such as:
- AI tools for small law firms
- AI customer support for Shopify stores
- AI lead qualification for local service businesses

Explain:
- who the customer is
- what kind of problem they likely have
- why this market is worth exploring

## Step 2 — Show raw evidence
Paste several example inputs:
- review excerpts
- forum complaints
- competitor site claims
- pricing notes

Tell students:
- messy input is okay
- we care more about repeated pain than perfect formatting

## Step 3 — Run pain-point analysis
Ask Hermes to identify:
- repeated complaints
- strongest pain signals
- which problems sound expensive or urgent

Teaching point:
Raw comments become structured patterns.

## Step 4 — Run competitor analysis
Ask Hermes to compare:
- who competitors serve
- what they are good at
- what frustrates users
- what segment is underserved

Teaching point:
You are not just researching companies; you are looking for whitespace.

## Step 5 — Run opportunity generation
Ask Hermes to propose:
- 3–5 opportunity ideas
- product or service angles
- why each exists

Teaching point:
Good ideas come from pain + gap, not fantasy.

## Step 6 — Run scoring and choose one niche
Have Hermes rank the opportunities.
Discuss:
- which one is easiest to test
- which one has strongest pain
- which one fits the founder/team best

Teaching point:
A smaller opportunity you can launch wins over a bigger one you cannot execute.

## Step 7 — Show final report
Display the final structured report.
Explain how this becomes:
- a decision memo
- a founder brief
- input for later classes like offer design or landing page creation

---

## 8. Student Exercise

### Exercise prompt
“Choose one business or market topic. Gather 3–5 pieces of customer or competitor evidence. Use Hermes to identify pain points, compare competitors, generate opportunities, and recommend one niche to test first.”

### Student deliverables
Each student should produce:
1. one market brief
2. one pain-point summary
3. one competitor comparison
4. three opportunity ideas minimum
5. one best first niche
6. one validation action

---

## 9. Student Worksheet Template

## Part A — My market
- Market topic:
- Target audience:
- Geography:
- My goal:

## Part B — Evidence I collected
- Review / comment 1:
- Review / comment 2:
- Review / comment 3:
- Competitor note 1:
- Competitor note 2:

## Part C — Hermes output
- Top pain points:
- Top competitor weakness:
- Best underserved niche:
- Top 3 opportunities:
- Best first niche:
- Why it won:
- First test:

---

## 10. Suggested Student Prompt Pack

## Prompt 1 — Pain points
```text
Analyze these customer comments and identify the most repeated pain points.
Group similar complaints, estimate frequency/severity qualitatively, and explain what business opportunity each pain point suggests.
```

## Prompt 2 — Competitors
```text
Compare these competitors based on the notes below.
For each competitor, summarize positioning, strengths, weaknesses, likely target customer, and the biggest gap in the market.
```

## Prompt 3 — Opportunities
```text
Using the pain points and competitor gaps, propose 3 to 5 practical product or service opportunities.
Prefer niche-specific ideas that can be tested quickly.
```

## Prompt 4 — Ranking
```text
Rank these opportunities based on demand, competition, ease of launch, monetization potential, and founder fit.
Recommend one best first niche and explain why.
```

---

## 11. Example Classroom Output Format

```markdown
## Market summary
Small law firms need simpler automation tools that do not require full-suite setup.

## Top pain points
1. Setup is too complicated
2. Pricing feels too high for solo firms
3. Manual intake is still inefficient

## Competitor gap
Existing tools are broad practice-management suites, not lightweight workflow-first assistants.

## Top opportunities
1. AI intake assistant for solo law firms
2. Billing automation helper for small firms
3. Client follow-up workflow assistant

## Best first niche
AI intake assistant for solo law firms

## Why this niche
It solves repeated pain, is narrow enough to launch quickly, and has strong automation fit.

## First action
Interview 5 solo firms or pitch a pilot workflow to 3 firms.
```

---

## 12. Instructor Discussion Questions

Use these during debrief:
- Which pain point appears most urgent?
- Which competitor weakness showed up repeatedly?
- Which niche looks attractive but difficult?
- Which opportunity is easiest to test next week?
- What assumption would you validate first?

---

## 13. Grading / Review Rubric

Score each student on:
- clarity of market definition
- quality of evidence collected
- quality of pain-point interpretation
- logic of competitor analysis
- practicality of chosen opportunity
- strength of validation step

### Simple rubric
- 5 = strong and specific
- 3 = acceptable but generic
- 1 = weak / unsupported

---

## 14. Common Student Mistakes

### Mistake 1
Choosing a market that is too broad.

### Fix
Force a narrower customer segment.

### Mistake 2
Using only one weak piece of evidence.

### Fix
Require at least 3 evidence snippets.

### Mistake 3
Producing generic ideas like “make an app.”

### Fix
Ask: what exact pain, for which exact user, in which exact workflow?

### Mistake 4
Choosing the biggest idea, not the best testable idea.

### Fix
Use ranking and founder-fit logic.

---

## 15. Homework / Follow-on Assignment

Ask each student to do one of the following:
1. collect 10 more evidence snippets for the winning niche
2. write a simple offer statement for the best niche
3. design a one-page landing page brief
4. outline a validation interview script

This creates a clean bridge into later classes.

---

## 16. Lesson Success Criteria

The class worked if most students can:
- describe one real market pain clearly
- identify one competitor gap clearly
- explain why one niche is better than another
- choose one realistic validation step

---

## 17. Recommended Instructor Close

Use a summary like:

> “Today you learned that market selection should come from evidence, not just enthusiasm. Hermes helps you read customer pain, competitor weakness, and niche opportunity faster — but your job is still to choose the most practical next test.”

---

## 18. Best Next Build / Teaching Handoff

This class should feed naturally into:
- offer design
- landing page creation
- SEO content planning
- outreach / validation scripts
- marketing experiments

That makes Class 11 a strong decision layer instead of a standalone research exercise.
