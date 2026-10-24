#!/usr/bin/env python3
"""
How much of a chunk's distance comes from its "Title — Section" prefix?

    python diagnose_prefix.py "question" guide_accessibility.md

For every chunk of one document, prints the cosine distance from the question
to the whole chunk, to the body without its prefix line, and to the prefix
alone. Written for the unit 2 diagnosis in README.md.
"""

import sys

import numpy as np

import chunker
import config
import ingest
from store import embed


def distance(a, b):
    a, b = np.array(a), np.array(b)
    return 1 - a @ b / (np.linalg.norm(a) * np.linalg.norm(b))


def main():
    question, source = sys.argv[1], sys.argv[2]
    chunks = chunker.split_documents(ingest.load_documents(config.CORPUS))
    q = embed([question])[0]

    print(f"Question: {question}\n")
    print(f"{'chunk':45} {'chars':>5}  {'whole':>6}  {'body':>6}  {'prefix':>6}")
    for c in (c for c in chunks if c.source == source):
        head, _, body = c.text.partition("\n\n")
        whole, bare, prefix = embed([c.text, body, head])
        print(f"{head[-45:]:45} {len(c.text):5}  "
              f"{distance(q, whole):6.3f}  {distance(q, bare):6.3f}  {distance(q, prefix):6.3f}")


if __name__ == "__main__":
    main()
