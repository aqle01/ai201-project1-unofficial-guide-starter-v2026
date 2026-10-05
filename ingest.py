"""
Stage 1 of the pipeline: loading documents off disk and cleaning them up.

The five stages are loading, chunking, embedding, retrieval, and generation.
When something goes wrong in unit 2, your job is to work out which of the five
it happened in. This is the first one.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import config


@dataclass
class Document:
    """One source file, cleaned and ready to be chunked."""

    source: str   # the filename, e.g. "housing_lottery.txt" — this is what gets cited
    text: str


def clean_text(raw: str) -> str:
    """
    Strip the stuff that isn't the real content.

    Provided corpora are already fairly clean. If you bring your own documents
    — especially anything scraped from a web page — this is where navigation
    text, ads, cookie banners and repeated boilerplate come out.
    """
    text = raw.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse runs of blank lines down to one.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse repeated spaces and tabs, but keep line structure intact.
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Some guides are hard-wrapped at ~80 columns and some aren't. Rejoin
    # wrapped lines so a paragraph is one line, but never glue a line onto a
    # heading or start a heading mid-paragraph.
    lines: list[str] = []
    for line in text.split("\n"):
        joinable = (
            lines
            and lines[-1]
            and line
            and not lines[-1].startswith("#")
            and not line.startswith("#")
        )
        if joinable:
            lines[-1] = f"{lines[-1]} {line.strip()}"
        else:
            lines.append(line)
    text = "\n".join(lines)

    return text.strip()


# Sections that appear word-for-word in at least this many documents are
# template boilerplate, not content. In city_guides every town guide ends with
# the same "Practical notes" block — which even claims the nearest hospital is
# in Brightwater inside the Brightwater guide, and contradicts
# guide_accessibility.md (Marchwood). Left in, it is nine identical chunks that
# match every "hospital" or "cash" question equally and point at no real town.
BOILERPLATE_MIN_DOCS = 3


def _sections(text: str) -> list[str]:
    """Split on level-2 headings, keeping each heading with its body."""
    return re.split(r"\n(?=## )", text)


def strip_boilerplate(documents: list[Document]) -> list[Document]:
    """Drop any section whose exact text repeats across many documents."""
    from collections import Counter

    counts = Counter(
        section
        for doc in documents
        for section in {s.strip() for s in _sections(doc.text)[1:]}
    )
    repeated = {s for s, n in counts.items() if n >= BOILERPLATE_MIN_DOCS}
    if not repeated:
        return documents

    cleaned = []
    for doc in documents:
        kept = [s for s in _sections(doc.text) if s.strip() not in repeated]
        cleaned.append(Document(source=doc.source, text="\n".join(kept).strip()))
    return cleaned


def load_documents(corpus: str | None = None) -> list[Document]:
    """
    Read every .txt and .md file in the corpus folder.

    Returns a list of Documents. Each one keeps its filename, because every
    answer your system produces has to name the document it came from.
    """
    folder = config.corpus_path(corpus)

    if not folder.exists():
        raise FileNotFoundError(
            f"No corpus at {folder}.\n"
            f"Check the corpus name in config.py, or see corpora/README.md "
            f"for what's available."
        )

    documents: list[Document] = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = clean_text(path.read_text(encoding="utf-8"))
        if text:
            documents.append(Document(source=path.name, text=text))

    if not documents:
        raise ValueError(f"{folder} has no .txt or .md files in it.")

    return strip_boilerplate(documents)


def describe(documents: list[Document]) -> str:
    """A one-line summary, printed after indexing so you can sanity-check it."""
    total = sum(len(d.text) for d in documents)
    avg = total // max(len(documents), 1)
    return (
        f"{len(documents)} documents, "
        f"{total:,} characters, "
        f"~{avg:,} characters per document"
    )


if __name__ == "__main__":
    docs = load_documents()
    print(describe(docs))
    print()
    for doc in docs[:3]:
        preview = doc.text[:200].replace("\n", " ")
        print(f"  {doc.source}: {preview}...")
