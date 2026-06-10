"""
The Unofficial Guide — RAG over UW-Madison CS course/professor knowledge.

Pipeline (see planning.md):
  Ingestion -> Chunking (per source type) -> Embedding (all-MiniLM-L6-v2)
  -> Vector store (ChromaDB) -> Retrieval (top-k=7) -> Grounded generation (Groq)

Usage:
  python rag.py build          # ingest documents/, chunk, embed, store in ChromaDB
  python rag.py ask            # interactive query interface
  python rag.py eval           # run the 5 evaluation questions from planning.md
"""

import os
import re
import sys
import glob

from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = "documents"
CHROMA_DIR = "chroma_db"
COLLECTION = "unofficial_guide"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 7
GROQ_MODEL = "llama-3.3-70b-versatile"

# The 5 evaluation questions from planning.md
EVAL_QUESTIONS = [
    "Which CS professor gives the most useful or detailed feedback?",
    "Is CS 537 (Operating Systems) considered a hard course?",
    "What is the average GPA / grade distribution for CS 540?",
    "Which is more difficult, CS 537 (Operating Systems) or CS 577 (Algorithms)?",
    "Does Professor Ali Abedi curve exams?",
]

# ---------------------------------------------------------------------------
# CHUNKING — one strategy per source type (see planning.md Chunking Strategy)
# ---------------------------------------------------------------------------

COURSE_RE = re.compile(r"(?:COMP\s?SCI|COMPSCI|CS|MATH|ECE|COS|CSMATH)\s?\d{3}", re.I)


def chunk_ratemyprofessors(path):
    """One review per chunk. Reviews are self-contained, so no overlap.
    Each review block ends with a 'Helpful / Thumbs up N / Thumbs down N' footer,
    which we use as the split delimiter. The review text is the longest line in
    the block (metadata lines and tags are all short)."""
    text = open(path, encoding="utf-8").read()
    header, _, body = text.partition("=== REVIEWS ===")
    prof = re.search(r"Professor:\s*(.+)", header)
    url = re.search(r"URL:\s*(.+)", header)
    prof = prof.group(1).strip() if prof else os.path.basename(path)
    url = url.group(1).strip() if url else ""

    blocks = re.split(r"\nHelpful\nThumbs up\n\d+\nThumbs down\n\d+", body)
    chunks = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        if not lines:
            continue
        review = max(lines, key=len)
        if len(review) < 15:          # skip blocks with no real review text (ads, etc.)
            continue
        m = COURSE_RE.search(b)
        course = m.group(0).upper().replace(" ", "") if m else "unknown course"
        chunks.append((
            f"Rate My Professors review of {prof} ({course}): {review}",
            {"source": "RateMyProfessors", "professor": prof, "course": course, "url": url},
        ))
    return chunks


def chunk_madgrades(path):
    """Templating: turn each course's grade table into a natural-language sentence.
    One sentence = one chunk, no overlap."""
    text = open(path, encoding="utf-8").read()
    _, _, body = text.partition("=== COURSES ===")
    chunks = []
    for b in re.split(r"\n(?=Course:)", body.strip()):
        course = re.search(r"Course:\s*(.+)", b)
        title = re.search(r"Title:\s*(.+)", b)
        gpa = re.search(r"Cumulative GPA:\s*(.+)", b)
        grades = re.findall(r"([A-F]{1,2}):\s*([\d.]+%)\s*\(([\d,]+)\)", b)
        if not course:
            continue
        c = course.group(1).strip()
        t = title.group(1).strip() if title else ""
        g = gpa.group(1).strip() if gpa else "N/A"
        dist = ", ".join(f"{pct} got {grade}" for grade, pct, _ in grades)
        sentence = (f"At UW-Madison, {c} ({t}) has a cumulative GPA of {g} "
                    f"across all instructors and semesters. Grade distribution: {dist}.")
        chunks.append((sentence, {"source": "MadGrades", "course": c, "gpa": g,
                                  "url": "https://madgrades.com"}))
    return chunks


def chunk_reddit(path):
    """Fixed-size 500-char chunks with 150-char overlap, after stripping ads /
    UI boilerplate. Overlap preserves context across reply boundaries."""
    text = open(path, encoding="utf-8").read()
    header, _, body = text.partition("=== THREAD ===")
    thread = re.search(r"Thread:\s*(.+)", header)
    url = re.search(r"URL:\s*(.+)", header)
    title = thread.group(1).strip() if thread else os.path.basename(path)
    url = url.group(1).strip() if url else ""

    junk = ["promoted", "sign up", "shop now", "learn more", "doubleclick",
            "americanexpress", "adform", "spectrum.com", "join the conversation",
            "sort by", "comments section", "search comments", "expand comment",
            "go to comments", "avatar", "cake icon", "video player",
            "clickable image", "thumbnail image", "lenovo", "squarespace"]
    keep = []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        if s in ("Upvote", "Downvote", "Reply", "Award", "Share", "Best",
                 "Academics", "Other", "OP"):
            continue
        if re.fullmatch(r"\d+", s):                 # bare vote counts
            continue
        if "ago" in s and "•" in s:                 # "• 5y ago" byline
            continue
        if s.startswith(("u/", "r/", "http")):
            continue
        if any(j in s.lower() for j in junk):
            continue
        keep.append(s)
    clean = " ".join(keep)

    chunks, size, overlap, i = [], 500, 150, 0
    while i < len(clean):
        piece = clean[i:i + size]
        chunks.append((f"Reddit thread '{title}': {piece}",
                       {"source": "Reddit", "thread": title, "url": url}))
        if i + size >= len(clean):
            break
        i += size - overlap
    return chunks


def load_and_chunk():
    """Ingestion + chunking: dispatch each document to its source-type chunker."""
    all_chunks = []
    for path in sorted(glob.glob(f"{DOCS_DIR}/ratemyprofessors/*.txt")):
        all_chunks += chunk_ratemyprofessors(path)
    for path in sorted(glob.glob(f"{DOCS_DIR}/madgrades/*.txt")):
        all_chunks += chunk_madgrades(path)
    for path in sorted(glob.glob(f"{DOCS_DIR}/reddit/*.txt")):
        all_chunks += chunk_reddit(path)
    return all_chunks


# ---------------------------------------------------------------------------
# VECTOR STORE + RETRIEVAL
# ---------------------------------------------------------------------------

def get_collection(reset=False):
    import chromadb
    from chromadb.utils import embedding_functions
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    if reset:
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
    return client.get_or_create_collection(COLLECTION, embedding_function=ef)


def build():
    print("Ingesting and chunking documents...")
    chunks = load_and_chunk()
    print(f"  -> {len(chunks)} chunks created")
    print(f"Embedding with {EMBED_MODEL} and storing in ChromaDB (first run downloads the model)...")
    col = get_collection(reset=True)
    col.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=[c[0] for c in chunks],
        metadatas=[c[1] for c in chunks],
    )
    print(f"Done. Indexed {col.count()} chunks into '{COLLECTION}'.")


def retrieve(col, question, k=TOP_K):
    res = col.query(query_texts=[question], n_results=k)
    return list(zip(res["documents"][0], res["metadatas"][0]))


# ---------------------------------------------------------------------------
# GROUNDED GENERATION (Groq)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are The Unofficial Guide, answering questions about UW-Madison \
Computer Sciences courses and professors. You must answer ONLY using the numbered \
context passages provided. Follow these rules strictly:
- Base every claim on the context. Do NOT use outside knowledge.
- Cite the passages you use with bracketed numbers like [1], [3].
- If the context does not contain the answer, say: "I don't have information on that \
in my sources." Do not guess or invent details.
- Reviews may disagree; when they do, summarize the range of opinions."""


def generate(question, retrieved):
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    context = "\n\n".join(f"[{i+1}] {doc}" for i, (doc, _) in enumerate(retrieved))
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context passages:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content


def format_sources(retrieved):
    lines = []
    for i, (_, m) in enumerate(retrieved):
        if m["source"] == "RateMyProfessors":
            label = f"RateMyProfessors — {m['professor']} ({m['course']})"
        elif m["source"] == "MadGrades":
            label = f"MadGrades — {m['course']}"
        else:
            label = f"Reddit — {m['thread']}"
        lines.append(f"  [{i+1}] {label}")
    return "\n".join(lines)


def answer_question(col, question):
    retrieved = retrieve(col, question)
    answer = generate(question, retrieved)
    return answer, retrieved


# ---------------------------------------------------------------------------
# INTERFACES
# ---------------------------------------------------------------------------

def ask():
    col = get_collection()
    if col.count() == 0:
        print("Index is empty. Run `python rag.py build` first.")
        return
    print("The Unofficial Guide — UW-Madison CS. Ask a question (or 'quit').\n")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in ("quit", "exit"):
            break
        answer, retrieved = answer_question(col, q)
        print("\n" + answer + "\n")
        print("Sources:")
        print(format_sources(retrieved) + "\n")


def run_eval():
    col = get_collection()
    if col.count() == 0:
        print("Index is empty. Run `python rag.py build` first.")
        return
    for n, q in enumerate(EVAL_QUESTIONS, 1):
        print("=" * 80)
        print(f"Q{n}: {q}\n")
        answer, retrieved = answer_question(col, q)
        print(answer + "\n")
        print("Retrieved chunks:")
        print(format_sources(retrieved))
        print()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ask"
    if cmd == "build":
        build()
    elif cmd == "ask":
        ask()
    elif cmd == "eval":
        run_eval()
    else:
        print(__doc__)
