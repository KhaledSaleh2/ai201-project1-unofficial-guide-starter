# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Student-generated reviews of Computer Sciences courses and professors at the University of
Wisconsin–Madison. The system answers candid questions about teaching quality, exam and workload
difficulty, grading, and which electives are worth taking — knowledge students share on Rate My
Professors and r/UWMadison but that the official course catalog never captures. It combines three
source types: opinionated professor reviews (Rate My Professors), factual grade-distribution data
(MadGrades), and long-form peer discussion (r/UWMadison).

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/131676 (Remzi Arpaci-Dusseau, CS 537) |
| 2 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/2776309 (Florian Heimerl, ML / data viz) |
| 3 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/125529 (Eric Bach, theory / algorithms) |
| 4 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/425160 (Jin-Yi Cai, theory / complexity) |
| 5 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/2770358 (Gary Dahl, CS 300 / 354) |
| 6 | MadGrades | Grade distribution | https://madgrades.com/courses/3795cfcc-807e-3ca7-8348-d4a909a42f06 (CS 200 — Programming I) |
| 7 | MadGrades | Grade distribution | https://madgrades.com/courses/07eabcce-fdab-3781-99ca-7dc2dc3544ae (CS 300 — Programming II) |
| 8 | MadGrades | Grade distribution | https://madgrades.com/courses/cb48129f-99e6-36fa-9a20-46e0617e2499 (CS 354 — Machine Organization) |
| 9 | MadGrades | Grade distribution | https://madgrades.com/courses/de8a0a8c-e076-3ec2-8b6c-e1e1ee82a53e (CS 540 — Intro to AI) |
| 10 | Reddit (r/UWMadison) | Discussion thread | https://www.reddit.com/r/UWMadison/comments/pfoc2b/who_do_you_think_is_the_best_professor_in_the_cs/ |
| 11 | Reddit (r/UWMadison) | Discussion thread | https://www.reddit.com/r/UWMadison/comments/101k2gg/cs_537_os/ |
| 12 | Reddit (r/UWMadison) | Discussion thread | https://www.reddit.com/r/UWMadison/comments/qqjwyv/best_500_cs_courses/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
