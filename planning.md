# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Student-generated reviews of **Computer Sciences courses and professors at the University of
Wisconsin–Madison**. The system answers candid questions about teaching quality, exam and
workload difficulty, grading, and which electives are worth taking — the kind of advice
students trade on Reddit and Rate My Professors but that never appears in the official course
catalog. Official descriptions list topics and credits; they say nothing about whether a
professor's exams are fair, whether the curve is generous, or how a course *actually* feels to
sit through. This guide draws on three complementary source types: opinionated professor
reviews (Rate My Professors), factual grade-distribution data (MadGrades), and long-form peer
discussion (r/UWMadison), so it can both aggregate opinion and ground answers in real numbers.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

> Note: Rate My Professors review pages and Reddit threads are JavaScript-heavy / crawler-blocked,
> so during ingestion (Milestone 3) the review text will be saved into `documents/` as `.txt`/`.html`
> rather than fetched live. The Reddit rows below need real thread URLs pasted in — search
> r/UWMadison for the listed topics and drop the permalinks in. Verify which course each professor
> actually teaches before relying on it in the eval.

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Remzi Arpaci-Dusseau (teaches CS 537, Operating Systems) | https://www.ratemyprofessors.com/professor/131676 |
| 2 | Rate My Professors | Florian Heimerl (ML / data visualization) | https://www.ratemyprofessors.com/professor/2776309 |
| 3 | Rate My Professors | Eric Bach (theory / algorithms) | https://www.ratemyprofessors.com/professor/125529 |
| 4 | Rate My Professors | Jin-Yi Cai (theory / complexity) | https://www.ratemyprofessors.com/professor/425160 |
| 5 | Rate My Professors | 1–2 more profs you personally had — browse the UW-Madison page | https://www.ratemyprofessors.com/school/18418 |
| 6 | MadGrades | CS 200 — Programming I (grade distribution) | https://madgrades.com/courses/3795cfcc-807e-3ca7-8348-d4a909a42f06 |
| 7 | MadGrades | CS 300 — Programming II (grade distribution) | https://madgrades.com/courses/07eabcce-fdab-3781-99ca-7dc2dc3544ae |
| 8 | MadGrades | CS 354 — Machine Organization & Programming (grade distribution) | https://madgrades.com/courses/cb48129f-99e6-36fa-9a20-46e0617e2499 |
| 9 | MadGrades | CS 540 / 537 / 577 — find via CS subject search | https://madgrades.com/search?subjects%5B0%5D=266 |
| 10 | Reddit (r/UWMadison) | Thread: "best / favorite CS professors" | [paste thread permalink] |
| 11 | Reddit (r/UWMadison) | Thread: "is CS 537 (OS) hard / how to survive it" | [paste thread permalink] |
| 12 | Reddit (r/UWMadison) | Thread: general CS course-selection / which electives advice | [paste thread permalink] |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

> Expected answers below are drafts — confirm and tighten each one against the documents you
> actually collect (especially #3, which should match the real MadGrades number).

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which CS professor in my sources gives the most useful or detailed feedback? | A specific professor named, supported by review quotes praising feedback/clarity. Tests synthesis across multiple review docs. |
| 2 | Is CS 537 (Operating Systems) considered a hard course? | Yes — heavy workload, demanding projects (xv6/OS-TEP), but well-regarded. Tests opinion aggregation across reviews + Reddit. |
| 3 | What is the average GPA / grade distribution for CS 540? | The actual MadGrades figure (e.g., a specific average GPA / % A). Factual ground-truth — tests whether retrieval pulls the MadGrades doc, not opinion. |
| 4 | Which is more difficult, CS 537 (Operating Systems) or CS 577 (Algorithms)? | A comparison grounded in both courses' reviews; may surface contradictory opinions. Tests multi-course comparison. |
| 5 | Does Professor [pick one with little/no grading detail in your docs] curve exams? | Likely **not answerable** from the collected docs — the intended trap. A grounded system should say it doesn't know rather than invent a curve. This is your planned failure / hallucination case. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
