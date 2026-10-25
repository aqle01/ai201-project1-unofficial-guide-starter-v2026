# The Unofficial Guide

Adriana Le — corpus: `city_guides`

---

# Unit 1

## What This Does

The Unofficial Guide answers plain-English questions about a fictional coastal
region using the `city_guides` corpus: nine town guides (Brightwater,
Kestrelford, Halden Bay, Elder Ness and others) and five region-wide guides on
eating, walking, regional transport, seasons and accessibility. It answers the
practical questions a visitor asks before a trip — when the pubs stop serving
food, whether the road floods, when the car parks fill up, which town is
manageable with limited mobility — from the retrieved guide sections only, and
names the file each answer came from. If nothing in the guides is close enough
to the question, it says "I don't have enough information about that" instead
of answering. Run it with `python app.py ask "your question"`.

## Chunking Strategy

**Chunk size:** one chunk per `## ` section, capped at 800 characters. In
practice chunks are 183–758 characters, 320 on average (85 chunks from 14
documents).
**Overlap:** none between sections. If a section were ever longer than 800
characters, it would be split at sentence boundaries with one sentence of
overlap (`SECTION_OVERLAP_SENTENCES = 1`); no section is that long today.

Every guide is a `# Title` followed by labelled sections — Getting there,
Getting around, Eat and drink, What to see, Where to stay, When to go. Each
section is about one topic and runs 177–712 characters, so the section is
already the unit a question is about. The starter's fixed 800-character windows
made 51 chunks that cut straight across those headings, so one chunk could hold
the end of "Eat and drink" and the start of "What to see".

Sections often don't name their town ("No railway station; the line was closed
in 1963..."), so every chunk starts with `Title — Section heading`, e.g.
`Kestrelford — Getting there`. That prefix carries the context that overlap
would otherwise have to carry. Neighbouring sections are separate topics, so
repeating text between them would only blur them together.

Two cleaning steps in `ingest.py` also came out of reading the documents:

- **Boilerplate removal.** All nine town guides end with the same word-for-word
  "Practical notes" section. It even says "the nearest full hospital is in
  Brightwater" inside the Brightwater guide, and contradicts
  `guide_accessibility.md`, which says Marchwood. Any section repeated verbatim
  in 3+ documents is now dropped (`strip_boilerplate`).
- **Unwrapping.** Some guides are hard-wrapped at about 80 columns and some
  aren't. Wrapped lines are rejoined so each paragraph is one line.

A weakness I can already see: each guide's intro paragraph becomes its own
"Overview" chunk. The accessibility guide's Overview ("An honest assessment
rather than a promotional one...") contains no facts, yet it is the top result
for "Which town is easiest to get around with limited mobility?" (0.386). The
chunk with the actual answer, "Straightforward", ranks 4th (0.549).

## Sample Chunks

All five produced by `chunker.py::split_documents` (`python app.py chunks`).

**Chunk 1** — source: `guide_kestrelford.md#3` — produced by: `chunker.py::split_documents`

```
Kestrelford — Eat and drink

Four pubs, two cafés, and a bakery that sells out by 11am. The pubs serve food between 12 and 2 and again between 6 and 8:30, and outside those windows there is nowhere to eat at all. The bakery is the reason most people come back.
```

**Chunk 2** — source: `guide_elder_ness.md#1` — produced by: `chunker.py::split_documents`

```
Elder Ness — Getting there

A single road in, which floods at the highest spring tides roughly six times a year for about two hours either side of high water. Tide tables are posted at the turning and are worth reading. No public transport of any kind. Nearest station is Pellew Sands, 40 minutes by road.
```

**Chunk 3** — source: `guide_regional_transport.md#2` — produced by: `chunker.py::split_documents`

```
Getting around the region — Driving

Roads are good between the towns and poor on the approaches to both Kestrelford and Halden Bay. The Kestrelford approach is single-track with passing places for the final eight minutes. The Halden Bay coast road is cut into the cliff and is slow rather than difficult.

Parking is the constraint rather than driving. Both Halden Bay lots fill by 10am on summer weekends. Kestrelford's lower car park is free and involves a steep walk up.
```

**Chunk 4** — source: `guide_corry_vale.md#5` — produced by: `chunker.py::split_documents`

```
Corry Vale — Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

**Chunk 5** — source: `guide_accessibility.md#1` — produced by: `chunker.py::split_documents`

```
Getting around the region with limited mobility — Straightforward

**Thornby Wells** is the easiest town in the region. It is flat, compact, and everything is within three minutes of everything else. Parking is free for two hours anywhere in town and the station is central. The pump room and gardens are level throughout.

**Marchwood** has a modern tram network with level boarding on all four lines, running every 8 minutes on weekdays. The city museum and covered market are both step-free. The distances between districts are the main consideration.

**Brightwater** is level along the river and through the centre. The mill museum is step-free. The station is a 15-minute walk from campus on flat ground, or the shuttle meets the four busiest arrivals.
```

## Sample Answer

**Question:** Until what time do the pubs in Kestrelford serve food in the evening?

**Answer:** (`python app.py ask "..."`, output pasted as-is)

```
  (best distance 0.160, cutoff 0.7)

The pubs in Kestrelford serve food in the evening between 6 and 8:30.

Source: guide_kestrelford.md, guide_eating.md

Sources retrieved: guide_eating.md, guide_givens_mill.md, guide_kestrelford.md
```

A near-miss that gets past the gate but is caught by the grounding instruction:

```
$ python app.py ask "Is there a ferry from Halden Bay to France?"
  (best distance 0.438, cutoff 0.7)

I don't have enough information about that.

Source: guide_halden_bay.md
```

**My relevance cutoff:** 0.70 (`THRESHOLD` in `config.py`)

Best distance for each question, from `python app.py retrieve` with section
chunks and top-k 5:

| Question | In corpus? | Best distance |
|---|---|---|
| Until what time do the pubs in Kestrelford serve food in the evening? | Yes | 0.160 |
| How many times a year does the road to Elder Ness flood? | Yes | 0.282 |
| By what time do the Halden Bay car parks fill up on summer weekends? | Yes | 0.289 |
| Which town in the region is easiest to get around with limited mobility? | Yes | 0.386 |
| How many bus operators run in the region, and do they accept each other's tickets? | Yes | 0.575 |
| What is the capital of Mongolia? | No | 0.810 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.835 |
| How do I write a for loop in Rust? | No | 0.861 |
| How do I change the oil in a diesel engine? | No | 0.881 |
| Who won the 1994 World Cup? | No | 0.969 |

The in-corpus group spans 0.160–0.575 and the out-of-corpus group 0.810–0.969,
with a gap from 0.575 to 0.810. I put the cutoff at 0.70, close to the middle
of that gap. The starter's 0.6 left only 0.025 of room above the bus question,
which is the weakest of my five because its answer is one clause inside a
paragraph about bus timetables.

What 0.70 gets wrong, which I checked on extra questions:

- **Paraphrases can fall outside the gap.** "Can I use my bus ticket from one
  company on another company bus?" asks the same thing as my bus question but
  scores 0.824, so it would be refused even though the answer is in
  `guide_regional_transport.md`. No cutoff fixes that without also letting the
  Mongolia question (0.810) through.
- **Near-miss travel questions pass the gate.** "Is there a ferry from Halden
  Bay to France?" (0.438), "What is the best nightclub in Brightwater?" (0.413)
  and "Where can I rent a car in Kestrelford?" (0.410) all score like real
  questions, because they name real towns. The guides answer none of them, so
  the grounding instruction has to catch these. I tightened
  `GROUNDING_INSTRUCTION` in `generate.py` to say so: don't fill gaps with what
  is typical for travel destinations, don't use one town's document as evidence
  about another, use the exact refusal sentence, and end every answer with a
  `Source:` line.

## How I Used AI

<!-- TODO — you write this. Two specific moments: what you asked, what came
     back, what you changed. -->

**1.**

**2.**

**Unit 2.** I used Claude Code (Claude Opus) as a coding agent for this unit.

- *Running and scoring the test.* It ran `run_eval.py` for both run logs and
  turned the per-question results into the per-criterion tables. It also
  checked every cited file for the answer phrase for criterion 5. I checked
  the tables against the results files before committing.
- *Spotting the pattern in the failures.* I asked it to diagnose the one
  ranking miss. It guessed the `Title — Section` prefix was matching the
  question, then tested that instead of asserting it. It wrote
  `diagnose_prefix.py` to embed each chunk with and without its prefix. The
  result was the key number in my diagnosis: the Overview body alone is 0.897,
  with the prefix 0.386. It also pointed out the same pattern in the Halden Bay
  and bus results, where a short chunk on the right topic outranks the answer.
- *Choosing the fix.* Before the full re-run, it compared three chunkings
  using embeddings only. That showed folding the intro beat dropping it
  (rank 1 against rank 3) without spending model calls on a fix that wouldn't
  work.


<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Answer chunk ranks in the top 3 | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |
| 5. `Source:` names a file that contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Raw results: [`results/run_2026-10-24_1614_before.md`](results/run_2026-10-24_1614_before.md)
(`python run_eval.py --label before`, 15 model calls, caching off). No
`scorer.py` yet, so I scored every cell by reading the answers against the
`expects` phrase in `questions.py`.

Criteria 1, 3 and 4 depend only on retrieval, which is deterministic: the best
distance was identical on all three runs for every question. So they come out
the same in every column. The answers did change between runs. For example, the
Elder Ness answer was one long sentence in run 1 and a shorter one in runs 2
and 3, which confirms these were three real calls rather than a cached reply.

### Output — criterion 1 (retrieved chunk contains the answer)

From `run_eval.py::run_once` (retrieval by `store.py::search`, answer by
`generate.py::answer_from_chunks`), run 1, the weakest of my five questions:

```
### How many bus operators run in the region, and do they accept each other's tickets? — run 1

- Best distance: 0.5748 (passed the gate)
- Sources retrieved: guide_givens_mill.md, guide_marchwood.md, guide_regional_transport.md

Three operators run in the region, and they do not accept each other's tickets.

Source: guide_regional_transport.md
```

The run log lists sources but not chunk text. To check which chunk held the
answer, I ran `python app.py retrieve` (`app.py::cmd_retrieve`). Rank 1 is the
Buses section, which begins "Three operators run in the region and they do not
accept each other's tickets":

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.5748     guide_regional_transport.md      Getting around the region — Buses  Three operators r...
2   0.6589     guide_marchwood.md               Marchwood — Overview  Marchwood is the regional hub ...
3   0.6837     guide_givens_mill.md             Givens Mill — Getting there  No station and no bus o...
4   0.6971     guide_marchwood.md               Marchwood — Getting around  A tram network of four l...
5   0.7010     guide_regional_transport.md      Getting around the region — The railway  The line ru...
```

### Output — criterion 2 (every answer names a source)

From `generate.py::answer_from_chunks` via `run_eval.py::run_once`, run 1, all
five answers:

```
The pubs in Kestrelford serve food in the evening until 8:30.

Source: guide_kestrelford.md, guide_eating.md
```

```
The single road into Elder Ness floods at the highest spring tides roughly six times a year, for about two hours either side of high water.

Source: guide_elder_ness.md, guide_walking.md
```

```
On summer weekends, the Halden Bay car parks fill up by 10am. 

Source: guide_halden_bay.md, guide_seasons.md, guide_regional_transport.md
```

```
Thornby Wells is the easiest town in the region to get around with limited mobility because it is flat, compact, and everything is within three minutes of everything else. 

Source: guide_accessibility.md
```

```
Three operators run in the region, and they do not accept each other's tickets.

Source: guide_regional_transport.md
```

### Output — criterion 3 (gate stops out-of-corpus questions)

From `run_eval.py::check_out_of_scope` (`gate.py::check`, cutoff 0.70), console
output:

```
Out-of-scope questions (the gate should refuse these):
  refused  (best distance 0.810)  What is the capital of Mongolia?
  refused  (best distance 0.881)  How do I change the oil in a diesel engine?
  refused  (best distance 0.969)  Who won the 1994 World Cup?
  refused  (best distance 0.835)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.861)  How do I write a for loop in Rust?
  -> gate refused 5 of 5
```

### Output — criterion 4 (answer chunk ranks in the top 3)

From `app.py::cmd_retrieve` (`python app.py retrieve "..."`). Where the answer
chunk ranked: Kestrelford 1, Elder Ness 1, Halden Bay 2 ("Getting there"; the
"When to go" section ranks above it), bus operators 1, mobility **4**. This is
the miss:

```
Question: Which town in the region is easiest to get around with limited mobility?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.3855     guide_accessibility.md           Getting around the region with limited mobility — Ov...
2   0.4997     guide_accessibility.md           Getting around the region with limited mobility — Di...
3   0.5348     guide_corry_vale.md              Corry Vale — Getting around  Nothing within the vall...
4   0.5491     guide_accessibility.md           Getting around the region with limited mobility — St...
5   0.5526     guide_walking.md                 Walking in the region — Moderate, with hills  The **...
```

The answer ("**Thornby Wells** is the easiest town in the region") is in the
"Straightforward" chunk at rank 4. The fact-free Overview chunk is at rank 1.

### Output — criterion 5 (`Source:` names a file that contains the answer)

Same answers as criterion 2. I checked each cited file for the answer phrase.
Every answer cites at least one file that contains it, on all three runs. The
extra files it cites contain the answer too:

| Question | Cited | Contains the answer? |
|---|---|---|
| Kestrelford pubs | guide_kestrelford.md, guide_eating.md | both ("6 to 8:30") |
| Elder Ness flooding | guide_elder_ness.md, guide_walking.md | both ("six times a year") |
| Halden Bay car parks | guide_halden_bay.md, guide_seasons.md, guide_regional_transport.md | all three ("10am") |
| Limited mobility | guide_accessibility.md | yes ("Thornby Wells") |
| Bus operators | guide_regional_transport.md | yes ("Three operators") |

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer (4 of 5) | MET | For each question I found which chunk holds the `expects` phrase and checked it was among the five retrieved. It was for all five questions on all three runs (5, 5, 5). Retrieval gave the same distances every run, so this isn't luck on one pass. |
| 2 | Every answer names a source (5 of 5) | MET | All 15 answers end with a `Source:` line naming at least one file. I read every one in the results file instead of assuming the prompt instruction worked. |
| 3 | Gate stops out-of-corpus questions (4 of 5) | MET | `gate.py::check` refused all five `OUT_OF_SCOPE` questions, and a refused question returns `gate.REFUSAL`, "I don't have enough information about that.", which is the exact wording my criterion asks for. The margin is thin: Mongolia scored 0.810 against a 0.70 cutoff. |
| 4 | Answer chunk ranks in the top 3 (4 of 5) | MET, at the edge | 4, 4, 4 against a target of 4. The target holds on every run, so it's met, but with no room to spare. The mobility question misses every time: its answer chunk is 4th, behind the accessibility Overview chunk, which has no facts in it. One more question like that and this is MISSED. |
| 5 | `Source:` names a file that contains the answer (4 of 5) | MET | For every file each answer cited, I searched it for the answer phrase ("8:30", "six times", "10am", "Thornby Wells", "Three operators"). All five answers cite a file that contains it, on all three runs, and no answer cites a file that doesn't. |

No revisions. Every criterion could be measured the same way twice, from the
results file plus `python app.py retrieve`, so none of them was broken.
Criterion 1 turned out easy to meet: top 5 is a loose window when chunks are
whole sections. Criterion 4, the stricter top-3 version, is the one that shows
the real weakness.

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

**I missed no criterion.** That's mostly because the targets were safe, not
because retrieval is good. Below are the two places where the answer was not
the top-ranked chunk, why that happened, and which target I'd tighten.

### The mobility question: answer chunk ranks 4th (stage: chunking, via the prefix)

"Which town in the region is easiest to get around with limited mobility?" The
answer is in the accessibility guide's "Straightforward" chunk, which ranks 4th
at 0.549. The top result is that guide's Overview chunk at 0.386. Its body is
one sentence with no facts: "An honest assessment rather than a promotional
one."

The mechanism is the `Title — Section` prefix I add in `chunker.py::split_documents`.
This guide's title is "Getting around the region with limited mobility", which
is almost word for word the question. So every chunk from this guide starts
with a line that matches the question, and how much that line counts depends
on how much else is in the chunk. I measured it with `diagnose_prefix.py`,
which embeds each chunk whole, without its prefix, and the prefix alone:

```
$ python diagnose_prefix.py "Which town in the region is easiest to get around with limited mobility?" guide_accessibility.md

chunk                                         chars   whole    body  prefix
d the region with limited mobility — Overview   183   0.386   0.897   0.245
egion with limited mobility — Straightforward   758   0.549   0.543   0.242
ound the region with limited mobility — Mixed   481   0.659   0.730   0.262
 the region with limited mobility — Difficult   566   0.500   0.608   0.213
 the region with limited mobility — Practical   378   0.660   0.700   0.244
```

- The Overview body on its own is 0.897, as far away as "Who won the 1994
  World Cup?". All of its closeness comes from the prefix, and at 183
  characters it is mostly prefix.
- The Straightforward chunk gets nothing from the prefix (0.543 without it,
  0.549 with it). It is the longest chunk in the corpus (758 characters) and
  covers three towns, so the prefix line is a small share of it. The Thornby
  Wells sentence is one sentence out of nine.
- Without prefixes, Straightforward would be the closest chunk in this guide.

So the prefix did what I wanted in Milestone 3 for town guides, where it
supplies a missing town name. Here it does the opposite: it rewards the
shortest, emptiest chunk because the title already matches the question. It is
a chunking decision showing up as a ranking problem. The embedding model is
doing what it should with the text it was given.

It didn't break the answer, because top-k is 5 and the model still saw the
Straightforward chunk. With top-k 3 it wouldn't have. Criterion 1 passed
because of the top-5 window, not because retrieval found the answer first.

### The Halden Bay question: answer chunk ranks 2nd (stage: embedding)

"By what time do the Halden Bay car parks fill up on summer weekends?" The top
result is "Halden Bay — When to go" (0.289), which says "July and August are
busy enough that the parking problem becomes the defining feature of the visit"
but gives no time. The answer, "two small lots that fill by 10am on summer
weekends", is in "Getting there" at 0.326.

This one isn't the prefix: both chunks share "Halden Bay", and When to go is
closer even with prefixes stripped (0.394 against 0.452). The embedding matches
on topic (summer, busy, parking) and has no notion of whether a chunk contains
the specific fact being asked for. "Getting there" spends most of its words on
the coast road and buses, so its parking sentence is diluted.

### The pattern

Both cases are the same problem. **Retrieval ranks chunks by topic, and a chunk
that is about the question's topic but doesn't answer it beats a longer chunk
that does.** The bus question shows it too: "Marchwood — Overview" ("the
junction everyone changes trains at") is 2nd there, with nothing about bus
operators. Overview chunks are the worst offenders. Every guide has one, they
are short, and they are written as general scene-setting rather than facts. In
the accessibility guide the prefix makes this much worse.

I ruled out the other stages. Loading: every document loaded and the
boilerplate was stripped as intended. Generation: all 15 answers were correct
and cited a file that contains the answer, so the model used the chunks it got.

### Which target I'd tighten

**Criterion 1, to "the top-ranked chunk contains the answer for at least 4 of
5 questions."** "Somewhere in the top 5" is a loose window when each chunk is a
whole section. With 85 chunks, five sections from the right guide can easily
include the answer by accident. Against the tighter version my system scores
3 of 5 (Kestrelford, Elder Ness, bus operators are rank 1; Halden Bay is 2nd,
mobility 4th), so it would be **missed**. That's the honest picture of my
retrieval.

## The Improvement

**What I changed:** I stopped making each guide's intro paragraph its own
"Overview" chunk. In `chunker.py::split_documents` the intro is now folded into
the guide's first section, so "An honest assessment rather than a promotional
one" sits at the top of the "Straightforward" chunk instead of standing alone.
That took the index from 85 chunks to 76. Nothing else changed: same prefix,
same 800-character cap, same top-k 5, cutoff 0.70 and prompt.

**Why I picked it:** my diagnosis found that the mobility answer ranked 4th
because a 183-character Overview chunk was mostly its prefix line, and that
prefix happens to match the question. Removing the stand-alone Overview chunk
removes the thing that was outranking the answer.

Before running the full test, I compared three chunkings on answer rank alone
(embeddings only, no model calls). That's how I picked this change over the
other obvious one, dropping Overview chunks entirely:

| Chunking | Chunks | Kestrelford | Elder Ness | Halden Bay | Mobility | Bus |
|---|---|---|---|---|---|---|
| Current (Overview as own chunk) | 85 | 1 | 1 | 2 | **4** | 1 |
| Drop Overview chunks | 75 | 1 | 1 | 2 | 3 | 1 |
| Fold Overview into first section | 76 | 1 | 1 | 2 | **1** | 1 |

Dropping them only got the mobility answer to 3rd, and it throws away facts
that are only in the intros, like Halden Bay's population and Marchwood being
the rail junction. (This quick check counted any chunk with "10am" for Halden
Bay, so it counted the seasons guide. The full run below uses the chunk that
directly states the answer.)

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

Raw results: [`results/run_2026-10-24_1646_after.md`](results/run_2026-10-24_1646_after.md)
(`python run_eval.py --label after`, 15 model calls, caching off, same five
questions, scored by hand the same way as before).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Answer chunk ranks in the top 3 | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. `Source:` names a file that contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Before and after, side by side:

| Criterion | Before (runs 1/2/3) | After (runs 1/2/3) |
|---|---|---|
| 1. Retrieved chunk contains the answer | 5/5 · 5/5 · 5/5 | 5/5 · 5/5 · 5/5 |
| 2. Every answer names a source | 5/5 · 5/5 · 5/5 | 5/5 · 5/5 · 5/5 |
| 3. Gate stops out-of-corpus questions | 5/5 · 5/5 · 5/5 | 5/5 · 5/5 · 5/5 |
| 4. Answer chunk ranks in the top 3 | 4/5 · 4/5 · 4/5 | **5/5 · 5/5 · 5/5** |
| 5. `Source:` names a file that contains the answer | 5/5 · 5/5 · 5/5 | 5/5 · 5/5 · 5/5 |
| *Tightened criterion 1: top-ranked chunk has the answer* | *3/5* | ***4/5*** |

Rank of the answer chunk and best distance per question, from
`app.py::cmd_retrieve`:

| Question | Before rank | After rank | Before best | After best |
|---|---|---|---|---|
| Kestrelford pubs | 1 | 1 | 0.160 | 0.160 |
| Elder Ness flooding | 1 | 1 | 0.282 | 0.272 |
| Halden Bay car parks | 2 | **3** | 0.289 | 0.289 |
| Limited mobility | **4** | **1** | 0.386 | 0.482 |
| Bus operators | 1 | 1 | 0.575 | 0.575 |

Out-of-corpus best distances (`run_eval.py::check_out_of_scope`):

```
Before                                   After
refused  (best distance 0.810)  Mongolia   refused  (best distance 0.854)
refused  (best distance 0.881)  Oil        refused  (best distance 0.901)
refused  (best distance 0.969)  World Cup  refused  (best distance 1.002)
refused  (best distance 0.835)  Ibuprofen  refused  (best distance 0.835)
refused  (best distance 0.861)  Rust       refused  (best distance 0.858)
```

Real output for the question the change was aimed at, after
(`app.py::cmd_retrieve`, then run 1 from `run_eval.py::run_once`):

```
Question: Which town in the region is easiest to get around with limited mobility?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.4825     guide_accessibility.md           Getting around the region with limited mobility — St...
2   0.4997     guide_accessibility.md           Getting around the region with limited mobility — Di...
3   0.5348     guide_corry_vale.md              Corry Vale — Getting around  Nothing within the vall...
4   0.5374     guide_corry_vale.md              Corry Vale — Getting there  Corry Vale is not a town...
5   0.5526     guide_walking.md                 Walking in the region — Moderate, with hills  The **...
```

```
Thornby Wells is the easiest town in the region to get around with limited mobility because it is flat, compact, and everything is within three minutes of everything else.

Source: guide_accessibility.md
```

**Did it help?**

Yes, for the problem it targeted. Criterion 4 went from 4/5 to 5/5 on all three
runs, and the mobility answer went from 4th to 1st, because the fact-free
chunk that outranked it no longer exists. The answers themselves didn't change.
They were already correct before, because top-k 5 still caught the answer chunk.
So this change is about margin, not about fixing a wrong answer.

It also made one thing worse, by the same mechanism in reverse. Folding Halden
Bay's intro ("a working fishing port of 8,000...") into "Getting there"
added two sentences with nothing about parking to the chunk that holds the
answer. That chunk moved from 0.326 to 0.379 and from 2nd to 3rd, still inside
the top 3 but with less room. The intro diluted the answer chunk instead of
drowning it out.

Two other side effects:

- **The gate's margin widened.** The nearest out-of-corpus question went from
  0.810 to 0.835, so the gap above my 0.70 cutoff grew. My guess is that the
  short, generic Overview chunks were the closest thing in the corpus to
  general questions like "What is the capital of Mongolia?" I didn't check
  which chunk Mongolia matched before the change, so that's unconfirmed.
- **The accessibility guide's first section is now over the 800-character
  cap,** so `_pack` splits it. The second piece is a 2-sentence tail about
  Brightwater's station. It didn't affect any test question, but it's the kind
  of short chunk that caused this problem in the first place.

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

No criterion is missed after the fix, so nothing here is a missed target. These
are the problems that my criteria don't catch.

**1. Retrieval ranks topic over facts, and my fix didn't touch that.**
The Halden Bay answer is 3rd now: "When to go" talks about "the parking
problem" without giving a time, and it still ranks above "Getting there", which
gives the 10am figure. My fix removed one short, empty chunk. It didn't change
how the embedding ranks a chunk that's on the topic against one that holds the
answer. Against my tightened criterion 1 (answer in the top-ranked chunk) I'm
at 4/5. What I'd do: add BM25 keyword search alongside the embedding and
combine the two rankings. "summer weekends" and "fill" appear word for word in
the answer sentence and not in "When to go". I stopped because the course asked
for one change measured properly. Adding hybrid search on top would have made
it impossible to tell which change moved which number.

**2. Paraphrased questions are refused even when the answer is in the
corpus.** "Can I use my bus ticket from one company on another company bus?"
asks the same thing as my bus question, but its best distance is 0.813, so the
gate refuses it. The Buses chunk with the answer is only 3rd, at 0.852. My
five test questions use the corpus's own words ("operators", "tickets"), so
none of my criteria would ever catch this. Lowering the cutoff isn't the fix:
the in-corpus and out-of-corpus distances overlap here. BM25 wouldn't help
much either, because the paraphrase avoids the corpus's words. What I'd try is
query rewriting, asking the model to restate the question in the guide's terms
before retrieval. I stopped because it costs an extra model call per question,
and it's a second change I couldn't measure separately in this unit.

**3. Near-miss questions depend entirely on the prompt.** "Is there a ferry
from Halden Bay to France?" gets past the gate (0.438) because it names a real
town, and only `GROUNDING_INSTRUCTION` stops the model inventing an answer.
None of my five criteria measure this: criterion 3 only uses questions that are
obviously off-topic. I didn't re-run the near-miss questions in this unit, so I
don't know if the prompt still holds three times out of three.

**4. My fix created a new short chunk.** Folding the intro made the
accessibility guide's first section longer than 800 characters, so `_pack`
splits off a two-sentence tail about Brightwater's station. That's the same
kind of short, prefix-heavy chunk I just diagnosed. It hasn't caused a problem
on any question I tested. The fix would be to let a section run a little over
the cap rather than split off a small tail. I left it because it hasn't failed
anything I tested, and changing it now would be a second change.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

**Criterion 1 was too easy, and I'd rewrite it as "the top-ranked chunk
contains the answer for at least 4 of 5".** "Somewhere in the top 5" passed
5/5 even while the mobility answer sat 4th behind a chunk with no facts. With
whole sections as chunks, five results from the right guide will often contain
the answer by luck. My system scored 3/5 on the rank-1 version before the fix
and 4/5 after. That number would actually have shown the problem and the
improvement.

**Criterion 3 tests the wrong kind of question.** Mongolia, ibuprofen and the
World Cup are nowhere near a coastal travel guide, so the gate was always going
to refuse them. The hard cases are near-misses that name a real town (the
ferry to France) and paraphrases of questions the corpus can answer (the bus
ticket one). I'd split it in two: one criterion for near-misses refused by the
system as a whole (gate or prompt), and one for paraphrases answered rather
than refused.

**I'd write criteria 4 and 5 in unit 1 like the others.** I wrote them at the
start of this unit. I picked them before seeing any results, but by then the
run had already started. They should have been fixed in writing before any
test existed, so no one has to take my word for the timing.
