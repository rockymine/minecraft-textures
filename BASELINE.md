# The baseline: 74 boards, scored before any texture data reached an agent

The control arm of the experiment, and it cost nothing to collect — these boards already existed. Every
one was authored under `AUTHORING-BRIEF.md` as it stands, which already carries the prose advice about
pattern width, and with no texture information available beyond one mean colour per block.

Taken with `python3 baseline.py`; rows in `baseline.json`.

## What was measured

Four readings, per *pattern*, over the blocks that pattern picks between, in the face the pattern's bucket
is seen from — surface and rim from above, wall and fill from the side.

| | pairs | share | boards |
|---|---|---|---|
| **repeat** — the same block listed twice in one pattern | 355 | 13.0% | 44 / 74 |
| **collapse** — two different blocks that resolve to one sprite on that face | 6 | 0.2% | 3 / 74 |
| **mush** — one tone family, contrast within a third | 304 | 11.1% | 49 / 74 |
| **clash** — near-identical colour, contrast differing by over 2.5× | 207 | 7.6% | 28 / 74 |

2,735 block pairs examined. 0.9% of block slots named something the catalogue could not read, so coverage
is not the limiting factor. **Nine boards of 74 carry no finding at all.**

## The result that changes the plan

**Collapse was proposed as the headline metric and the corpus says it is marginal.** Six occurrences, on
three boards. Every one of them is the same case — `Sandstone + Smooth Sandstone` in a surface bucket,
where both resolve to `sandstone_top` — which is exactly the mechanism the face data was built to catch,
and it simply does not come up often. Four of the six are on one desert board whose palette invited it.

The faults that actually occur are **mush** and **repeat**, and they occur on two thirds of the corpus.

**Repeat needs no texture data at all**, which is why it is counted apart. An agent writing
`stops: [grass, grass, dirt, grass]` has made a document error catchable by string comparison. Counting it
as a texture finding would flatter the data it is meant to test. It is reported because 13% of pairs is a
real quality signal and a fair control: if a new brief moves *repeat* as much as it moves *mush*, the
improvement is attention, not information.

## What mush and clash are made of

The findings concentrate on a handful of pairs, which is what makes them worth acting on.

| mush | count | why |
|---|---|---|
| Coarse Dirt + Dirt | 70 | one family, contrast ratio 1.13, means 12 apart |
| Andesite + Polished Andesite | 64 | ratio 1.15, means 7 apart |
| Gravel + Cobblestone | 46 | ratio 1.32, means 11 apart |

| clash | count | why |
|---|---|---|
| Stone + Mossy Cobblestone | 62 | means 32 apart, contrast ratio 3.03 |
| Diorite + Clay | 15 | means 13 apart, ratio 5.33 |

`Stone + Mossy Cobblestone` is the case the author named from memory before any of this was measured, and
it is the single commonest clash in the corpus. Mush lands hardest on the **surface** bucket (174 of 304),
which is the face a player spends the whole match looking at.

## What `repeat` turned out to be counting

The 13.0% above is not, or not only, the document slip it was taken for. Two different things wear the
name: `[grass, grass, dirt, grass]`, which is a mistake, and `[grass x10, coarse_dirt]`, which is an author
weighting a noise by repeating a stop — ten grass stops contribute C(10,2) = 45 repeat pairs from one
deliberate decision.

Ten probe boards were scored both ways. Raw, they carry **361 repeat pairs of 1,349** — 26.8%, twice the
corpus rate. Deduplicated to each pattern's distinct blocks, they carry **0 of 492**. Every repeat on every
one of the ten was weighting, and not one board listed a block twice by accident.

`scorer.py` takes `distinct=True` for that reading. Which one is wanted depends on the question: raw counts
what the document says, distinct counts what the palette is. **For anything comparing agents or briefs,
distinct is the honest one**, because raw mostly measures how much an author leaned on stop-repetition to
weight a field.

The corpus rate above has not been re-derived under `distinct`, so 13.0% should be read as an upper bound
on the slip and not as the slip itself.

## Reading it honestly

`repeat` and `collapse` are facts. `mush` and `clash` carry thresholds — a contrast ratio of 1.34 and of
2.5, and a colour distance of 42 — chosen by looking at this corpus. They are calibrated, not derived, and
an agent that optimises against them is not the same as an agent making better maps. What they are good
for is a **delta**: the same scorer over a new set of boards says whether something moved. Comparing an
absolute score against zero would be reading more into the thresholds than they hold.
