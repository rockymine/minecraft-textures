# Arm 2: the palette answers texture, and the paint does not change

Ten boards, five places, two arms. `PROBE.md` describes the design; this is what it returned.

Each board is a copy of `rockymine-probe` painted by a fresh agent given that spec's `PROMPT.md` verbatim,
working through the studio's HTTP API alone — no repository access, no knowledge of an experiment, no
knowledge of another arm. Five ran against `pgm-studio` at `43de43a`, where `GET /api/terrain/blocks`
answers each block's sprite, contrast, colours and construction per face; five against its parent
`98262bf`, where the same route answers one mean colour. Verified before any run: 110 blocks both sides,
identical ids, names, groups and hexes; 110 of 110 carrying `top`/`side` on one arm and 0 of 110 on the
other.

The boards and their documents are committed in `pgm-studio-mapgen` under `specs/probe-*` and `maps/probe-*`.
Every finding row is in `probe/runs/score-*.json`, and `probe/runs/timelines.jsonl` holds each run's
reconstructed timeline.

## The result

Read as deltas per pair, over each pattern's distinct blocks:

| place | repeat | collapse | mush | clash |
|---|---|---|---|---|
| plains | +0.0p | +0.0p | **−6.3p** | +2.6p |
| a desert | +0.0p | −2.0p | −0.4p | −0.8p |
| a snowfield | +0.0p | +0.0p | **+6.3p** | +0.0p |
| badlands | +0.0p | +0.0p | +2.1p | +4.2p |
| a volcanic ashfield | +0.0p | +0.0p | −5.5p | +4.2p |
| **sign** | 5 tied | 1 better | **3 better, 2 worse** | 1 better, 3 worse |
| **mean** | +0.0p | −0.4p | **−0.8p** | +2.0p |

**Mush did not move.** Three better, two worse, mean −0.8 points, which under a sign test is a coin toss.
The two largest deltas are −6.3p and +6.3p — the shape of run-to-run variation, not of an effect. Clash
went the other way, three of five worse.

**Collapse fired twice in ten boards, once per arm.** Both on the desert pair, both from the sandstone
family: `Smooth Sandstone + Double Sandstone Slab` with the texture data, `Smooth Sandstone + Sandstone`
without. The rates differ (3.6% against 5.6%) only because the two boards hold different numbers of pairs;
the count is one and one. The fault the face data was built to catch was made by the arm holding the data,
in the exact form the feature's own commit message names.

## Why: the field that answers it was never read

Counted over each run's transcript:

| | `/terrain/blocks` calls | `contrast` | `construction` | `"texture"` | sprite names |
|---|---|---|---|---|---|
| with texture data (5 runs) | 3–4 | 3–9 | 2–11 | **0** | **0** |
| without (5 runs) | 3–4 | 0–1 | 0 | 0 | 0 |

The data arrived and was read: `contrast` and `construction` appear in all five texture-arm transcripts and
in none of the five others. But `texture` and every sprite name appear **zero times in all ten runs**.

Agents consumed the two continuous fields and never compared the categorical one. `texture` is the only
field that answers whether two blocks are the same block on a face, and `collapse` is the only reading that
depends on it — so the metric with the strongest mechanism behind it failed for want of the one field
nobody looked at. A number invites comparison; an identity string apparently does not, unless something
says to compare it.

**This is not evidence that the data cannot work.** It is evidence that a field's presence in a response is
not the same as its reachability. Arm 3 — the same palette plus one worked example of querying `texture`
before choosing — is the cheap next test, and the instrumentation above is what it should be judged on.

## What the boards showed apart from the numbers

**Effort is identical across arms.** Means: 28.9 against 28.0 minutes, 130 against 129 tool calls, 66
against 64 API calls, 11.6 against 12.0 renders. Both arms write first at 6.6 minutes after 12–16 reads.
Nothing separates them but the palette.

**Every one of the ten told terrain from the things standing on it**, with no layer marked `kind: made` to
help. Pillars, kerbs, lintels and parapets were named as built on all ten boards. Once the studio raised
`SK23` — a one-block-wide shape is all edge, so a theme's surface never paints it — both arms moved those
shapes onto a stated `material`, which is what the field is for. That habit tracks the finding, not the arm:
on the snowfield the no-data arm used more shape materials than the other.

**Both badlands agents independently authored the same board**: one world-Y strata shared as the wall bucket
of every theme, bleached caprock marking the objective plateaus, one cut stone for everything built. Two
agents, no contact, different palettes, same design.

**No agent moved the geometry.** All ten painted the board they were given.

## What the scorer could not tell

The two boards that read best as places — the badlands and ashfield boards from the no-data arm — are also
two of the worst-scoring, at 24.3% and 19.8% clash. The plains board with the highest mush (19.1%) reads as
a clean landscape with legible routes. On these ten boards the calibrated thresholds do not track whether a
board looks right, which is the caveat `BASELINE.md` states, seen from the other side.

## Limits

Five pairs; an effect of a few points would not be visible. Both repositories' `CLAUDE.md` are injected into
every agent's context, including the advice to finish ground by slope, which all ten used — identical across
arms, so the deltas hold, but no agent here was naive and none of these boards is comparable to the corpus
absolutes in `BASELINE.md`. One model throughout, so the spread between runs is one model's sampling
variance. The snowfield pair was relaunched after both agents died on API errors; both boards were verified
unpainted first.

Write counts in `timelines.jsonl` are reconstructed from shell commands, so a run that drove the API from
inside a script under-reports them — `ashfield-ct` shows none for that reason, and its board is fully
painted.
