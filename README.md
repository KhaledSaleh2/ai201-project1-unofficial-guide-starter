# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your free Groq API key (console.groq.com)

python rag.py build           # ingest documents/, chunk, embed, store in ChromaDB (387 chunks)
python rag.py ask             # interactive query interface
python rag.py eval            # run the 5 evaluation questions
```

Pipeline: Ingestion → per-source-type Chunking → Embedding (`all-MiniLM-L6-v2`) → Vector store (ChromaDB) → Retrieval (top-k=7) → Grounded generation (Groq `llama-3.3-70b-versatile`). See `planning.md` for the architecture diagram and design rationale.

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

I use a different chunking strategy per source type (see planning.md).

**Chunk size:**
- Rate My Professors: one review per chunk (split on each review's `Helpful / Thumbs up / Thumbs down` footer).
- MadGrades: one templated natural-language sentence per course.
- Reddit: fixed 500-character windows.

**Overlap:**
- Rate My Professors: none (each review is self-contained).
- MadGrades: none (each course sentence is independent).
- Reddit: 150 characters (~30%), to preserve context across reply boundaries.

**Preprocessing before chunking:**
- RMP: stripped the `Helpful / Thumbs up N / Thumbs down N` footers and `ADVERTISING` lines; reduced each review block to its review text.
- MadGrades: converted each grade-distribution table into a sentence ("...has a cumulative GPA of 3.30... Grade distribution: 35.6% got A...").
- Reddit: stripped promoted ads (Squarespace, Lenovo, etc.), vote counts, usernames, and UI boilerplate, then applied the sliding window.

**Why these choices fit your documents:** Reviews are short and self-contained, so the review is the natural unit and overlap adds nothing. Grade tables can't be embedded meaningfully as numbers, so templating turns them into matchable prose. Reddit comments are long, variable-length, and reply on each other, so fixed windows with overlap keep neighboring context together.

**Final chunk count:** 387 chunks across all documents.

### Sample chunks (5 labeled, with source document)

1. **`documents/ratemyprofessors/eric_bach.txt`** (RateMyProfessors — Eric Bach, CS577):
   > Rate My Professors review of Eric Bach (CS577): Bach is quite good. He's a little old school and only lectures on a chalkboard, however, he tries to put up relevant material on the website. He's slow to grade, but overall, a very good professor who knows his stuff...

2. **`documents/ratemyprofessors/florian_heimerl.txt`** (RateMyProfessors — Florian Heimerl, CS400):
   > Rate My Professors review of Florian Heimerl (CS400): My biggest issue with Florian is his lecturing ability. He speaks at an unbearably awkward pace and is super hard to follow in lectures, with completely illegible handwriting...

3. **`documents/madgrades/cs_grades.txt`** (MadGrades — COMP SCI 540, templated sentence):
   > At UW-Madison, COMP SCI 540 (Introduction to Artificial Intelligence) has a cumulative GPA of 3.30 across all instructors and semesters. Grade distribution: 35.6% got A, 23.6% got AB, 20.9% got B, 9.5% got BC, 6.0% got C, 1.7% got D, 1.2% got F.

4. **`documents/reddit/best_500_cs_courses.txt`** (Reddit thread, 500-char window):
   > Reddit thread 'Best 500+ CS courses': ...chooseusernamee 571 is the best value and most practical course if you intend to be a software developer and wants to work as a front end developer...

5. **`documents/reddit/cs537_os.txt`** (Reddit thread, 500-char window):
   > Reddit thread 'CS 537 OS': ...The major difficulty of algos is just conceptual. Alot of the concepts are very abstract and you will have to spend a lot of time reasoning through them. Use office hours as much as possible...

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via sentence-transformers, run locally. It is small and limited, but sufficient here: the corpus is small, the documents are short, and everything is in English. Running locally also means no API key, no rate limits, and student-written content never leaves the machine. Retrieval uses top-k = 7 — a higher k chosen deliberately because the chunks are small (one review / one sentence) and individually carry little context, so more of them are needed to give the LLM enough to work with.

**Production tradeoff reflection:** If cost weren't a constraint I'd move to a model that captures nuance better (e.g. `text-embedding-3-large` or a self-hosted `BGE-large`), because Rate My Professors and Reddit text is informal, sarcastic, human language where nuance matters for retrieval. I'd weigh: accuracy on this slang-heavy domain (favoring a larger model), context length (a longer limit would let me embed bigger Reddit chunks without truncation), latency and per-token cost (favoring local), and data privacy — sending student-written reviews to a third-party API is a real consideration. Multilingual support is low priority since the corpus is all English.

### Retrieval test results

**Query 1 — "Is CS 537 hard?"** — top 3 chunks:
1. (Reddit — CS 537 OS) "...I'm signed up for intro to operating systems next semester and was wondering... what the hw and exams are like..."
2. (Reddit — CS 537 OS) "...The major difficulty of algos is just conceptual. Alot of the concepts are very abstract..."
3. (Reddit — Best 500+ CS courses) "...OS should be required tbh. Other than that, 577 is hard but pretty essential..."

*Why these are relevant:* all three come from threads explicitly discussing CS 537 / 500-level workload. Note the query never uses the words "operating systems" or "projects," yet semantic search surfaced the right OS-difficulty discussion — it matched on meaning, not keywords.

**Query 2 — "What is the GPA for CS 540?"** — top 3 chunks:
1. (MadGrades — COMP SCI 540) "...cumulative GPA of 3.30 ... 35.6% got A, 23.6% got AB..."
2. (MadGrades — COMP SCI 354) "...cumulative GPA of 3.10..."
3. (MadGrades — COMP SCI 300) "...cumulative GPA of 3.29..."

*Why these are relevant:* the exact course (CS 540) ranked #1, with sibling MadGrades course chunks following. Templating the grade tables into sentences is what made a numeric question retrieve the numeric source instead of opinion reviews.

**Query 3 — "Which professor has the best lectures?"** — top 3 chunks:
1. (RateMyProfessors — Eric Bach, CS577) "...Not always an engaging lecturer, but a very good teacher overall. Recommended."
2. (RateMyProfessors — Gary Dahl, CS400) "Gary's lectures are second to none. He is very well organized."
3. (RateMyProfessors — Florian Heimerl, CS400) "lectures are slow, but explains things well."

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The retrieved chunks are passed to Groq (`llama-3.3-70b-versatile`) as numbered context passages, with this system prompt:

> You are The Unofficial Guide, answering questions about UW-Madison Computer Sciences courses and professors. You must answer ONLY using the numbered context passages provided. Follow these rules strictly: Base every claim on the context. Do NOT use outside knowledge. Cite the passages you use with bracketed numbers like [1], [3]. If the context does not contain the answer, say: "I don't have information on that in my sources." Do not guess or invent details. Reviews may disagree; when they do, summarize the range of opinions.

Generation temperature is set to 0.1 to keep answers tight to the context. Structurally, the question and context are sent in a single user message and only the top-k=7 retrieved chunks are ever provided — the model has no other source of information.

**How source attribution is surfaced in the response:** Two ways. (1) The model cites passages inline with bracketed numbers (`[1]`, `[3]`). (2) After every answer the interface prints a `Sources:` list mapping each number to a human-readable source — e.g. `[1] RateMyProfessors — Remzi Arpaci-Dusseau (CS537)`, `[1] MadGrades — COMP SCI 540`, or `[1] Reddit — CS 537 OS`.

---

## Query Interface

The interface is a command-line tool: `python rag.py ask`.

- **Input field:** a free-text question typed at the `>` prompt (type `quit` or `exit` to stop).
- **Output fields:** (1) a grounded natural-language **answer** with inline `[n]` citations, then (2) a **`Sources:`** block listing each cited number's origin document.

**Sample interaction transcript (one complete query and response):**

```
> What is the average GPA for CS 540?

The average GPA for COMP SCI 540 (Introduction to Artificial Intelligence) is 3.30.
The grade distribution is: 35.6% A, 23.6% AB, 20.9% B, 9.5% BC, 6.0% C, 1.7% D,
1.2% F [1].

Sources:
  [1] MadGrades — COMP SCI 540
  [2] MadGrades — COMP SCI 354 (also ECE 354)
  [3] MadGrades — COMP SCI 200
  [4] MadGrades — COMP SCI 300
  [5] RateMyProfessors — Gary Dahl (COMPSCI400)
  [6] Reddit — Best 500+ CS courses
  [7] RateMyProfessors — Gary Dahl (CS400)
```

---

## Example Responses

**Response 1 — source attribution visible — "Is CS 537 (Operating Systems) hard?"**
> According to the context passages, CS 537 (Operating Systems) is considered a hard course. One Reddit user mentions that "OS was the hardest CS course I took besides 577 algos" [1]. Another notes the projects can get "very involved" [1], and that some projects took 20–30 hours [5]. However, the final curve was "very generous" [1].
>
> Sources: [1] Reddit — CS 537 OS · [5] Reddit — CS 537 OS · [3] Reddit — Best 500+ CS courses

**Response 2 — source attribution visible — "What is the average GPA for CS 540?"**
> The average GPA for COMP SCI 540 (Introduction to Artificial Intelligence) is 3.30. The grade distribution is: 35.6% A, 23.6% AB, 20.9% B, 9.5% BC, 6.0% C, 1.7% D, 1.2% F [1].
>
> Sources: [1] MadGrades — COMP SCI 540

**Out-of-scope query (refusal) — "Does Professor Ali Abedi curve exams?"**
> I don't have information on that in my sources. There is no mention of Professor Ali Abedi in the provided context passages [1]-[7].
>
> The system declined rather than fabricating a curve from the other CS 537 professors' reviews that retrieval surfaced — the grounding instruction held.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which CS professor gives the most useful or detailed feedback? | A named professor (e.g. Remzi or Cai, who have "Gives good feedback" tags) backed by review quotes | Refused — "I don't have information on that," saying the passages discuss teaching style but not feedback quality | Relevant (pulled real review chunks) | **Inaccurate** — overly conservative refusal; see Failure Case |
| 2 | Is CS 537 (Operating Systems) considered a hard course? | Yes — hard, very involved projects, but well-regarded | "Yes, a hard course"; cited Reddit on heavy projects (20–30 hrs), "hardest besides 577," generous final curve | Relevant (Reddit 537/500-level threads) | Accurate |
| 3 | What is the average GPA / grade distribution for CS 540? | 3.30 GPA; ~35.6% A, 23.6% AB, etc. | "Average GPA is 3.30," then the full distribution, cited MadGrades [1] | Relevant (MadGrades CS 540 chunk ranked #1) | Accurate |
| 4 | Which is more difficult, CS 537 or CS 577 (Algorithms)? | A comparison; both very hard, opinions vary | Both challenging; noted "537 hardest besides 577 algos" and 577 being conceptually hard; said no clear winner | Relevant (Reddit + Bach/Cai 577 reviews) | Accurate (appropriately hedged) |
| 5 | Does Professor Ali Abedi curve exams? | Not answerable — Abedi has no reviews in the corpus | Refused — "no mention of Professor Ali Abedi in the provided context"; did NOT invent a curve from Remzi's CS 537 reviews | Off-target (pulled other CS 537 profs) but correctly ignored | Accurate (correct refusal — the conflation trap was avoided) |

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

**Question that failed:** "Which CS professor gives the most useful or detailed feedback?" (Q1)

**What the system returned:** A refusal — "I don't have information on that in my sources. The provided passages discuss the teaching styles, passion, and helpfulness of various CS professors, but they do not specifically mention the quality or detail of feedback." Retrieval actually returned relevant professor-review chunks (Cai, Remzi, Heimerl), so this is a generation/grounding failure rather than a retrieval miss.

**Root cause (tied to a specific pipeline stage):** The chunking stage. My Rate My Professors chunker reduces each review block to a single line — the review prose — and discards everything else, including Rate My Professors' structured tag lines such as "Gives good feedback." That tag is the single most direct signal for this exact question, and it was thrown away before embedding. So no chunk in the index actually contains the word "feedback" prominently; the model, correctly following its strict grounding instruction, saw only passages about lectures and humor and refused rather than guessing. The grounding worked as designed — the information simply never made it into a chunk.

**What you would change to fix it:** Include the tag lines in each RMP chunk — append the captured tags (e.g. "Tags: Gives good feedback, Caring, Amazing lectures") to the review text before embedding. That puts the "feedback" signal into the vector space so it can be retrieved, without changing the one-review-per-chunk strategy.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the per-source-type chunking strategy in planning.md first made the implementation almost a direct translation — `load_and_chunk()` just dispatches each document to the chunker the spec already described. The MadGrades templating insight in particular paid off directly: because the spec said to turn grade tables into sentences rather than embedding raw numbers, the factual question (Q3, CS 540 GPA) returned the exact 3.30 figure with a clean MadGrades citation, which would not have worked if I had embedded the table as-is.

**One way your implementation diverged from the spec, and why:** The spec said "one review per chunk" but didn't specify *how* I'd isolate the review text from the surrounding metadata and tags. In implementation I took a shortcut — reducing each review block to its single longest line — for speed and robustness against messy formatting. I didn't anticipate that this would discard the RMP tag lines, which cost me the "Gives good feedback" signal and directly caused the Q1 failure (see Failure Case). A spec that had said "keep review text *and* tags" would have avoided it.

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

- *What I gave the AI:* My Documents list and Chunking Strategy section from planning.md, and asked it to implement ingestion plus the per-source-type chunkers.
- *What it produced:* `load_and_chunk()` and three chunkers in `rag.py` — `chunk_ratemyprofessors()` (split on the Helpful/Thumbs footer), `chunk_madgrades()` (template tables into sentences), and `chunk_reddit()` (strip ads/UI, then 500/150 sliding window).
- *What I changed or overrode:* I kept the per-type design and the 500/150 Reddit numbers from my spec. The RMP chunker uses a "longest line per review" heuristic, which I accepted for speed but which dropped the review tags — I later identified this as the root cause of my Q1 failure and documented the fix rather than patching it under time pressure.

**Instance 2**

- *What I gave the AI:* My Retrieval Approach section (all-MiniLM-L6-v2, top-k=7, ChromaDB) and my grounding requirement (answer only from retrieved chunks, cite sources).
- *What it produced:* The embedding/storage step using ChromaDB's SentenceTransformer embedding function, a `retrieve()` that returns the top 7 chunks, and a `generate()` that calls Groq's `llama-3.3-70b-versatile` with a grounding system prompt, plus a `Sources:` printout mapping each citation to its origin.
- *What I changed or overrode:* I set generation temperature to 0.1 for tighter grounding and added an explicit refusal instruction ("say 'I don't have information on that in my sources'"). That refusal behavior is exactly what made the system correctly decline the Q5 Ali Abedi trap instead of hallucinating.
