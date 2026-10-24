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

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

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

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
