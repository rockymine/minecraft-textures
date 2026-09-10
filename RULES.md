# What the board scorer reads, and what calibrated it

`boardscore.py` reads a whole sketch document — the theme registry, the materials stated on shapes,
the strokes and the rocks — and reports what its materials will look like beside each other. It
replaces the registry-only reading in `scorer.py`, which could not see a path or a rock at all.

**Nothing here belongs in the studio.** These are one author's rulings on ten boards turned into
arithmetic, and the author's own verdict on the exercise is that it is a science of eyesight. The
tool is for looking at a batch of boards and finding the places worth walking to; it is not a gate
and it does not refuse anything.

## The calibration set

Fifteen pairs the author named while looking at ten built worlds — the boards are in
`pgm-studio-mapgen` under `specs/probe-*`, the verdicts in `specs/PROBE-REVIEW.md`.

| called good | contrast | called bad | contrast |
|---|---|---|---|
| Snow Block + Quartz Block | 6.9 / 5.3 | Cobblestone + Mossy Cobblestone | 29.2 / 35.8 |
| Gray + Black Stained Clay | 1.0 / 0.9 | Gravel + Cobblestone | 22.2 / 29.2 |
| Hardened Clay + Red Sand | 3.6 / 8.7 | Coarse Dirt + Dirt | 26.0 / 23.1 |
| Hardened Clay + Orange Stained Clay | 3.6 / 2.1 | Andesite + Polished Andesite | 23.5 / 20.4 |

The praised pairs top out at 8.7 and the condemned ones start at 20, which is the whole of
`NOISE_FLOOR = 15`.

## What changed, and why

**`mush` is gone and `soup` replaces it.** `mush` fired on one tone family with contrast within a
third, and it named as faults the two combinations the author praised most: `Snow + Quartz` on the
snowfield board and `Gray + Black Stained Clay` four times on the ashfield board. Over the five
paired boards it predicted the author's preference twice in five. The relation it describes is real
and the missing half is loudness — two quiet blocks of one family read as one ground with weather in
it, which is what a surface is for, and two busy ones read as soup. `soup` is the same test with a
noise floor under it.

**`mottle` is new, and grain decides it, not distance.** The author's commonest complaint is *too
contrasting*, which is a wide colour distance between families — and it was not measured at all.
It cannot be measured by distance alone: white clay, light grey clay and sand span 120 and 147 and
the author liked them, because that pattern laid them in rings. The same three as specks would not
work. So a wide distance is a fault **inside a speckled pattern** — noise, turbulence, cell — and
clean inside a structured one.

**`clash` is unchanged.** It predicted the author's preference in four of five pairs, every pair it
separated at all, and nothing suggested moving it.

**Four readings the registry could not reach.** `pathEcho` — a path laid in blocks the ground it
crosses already carries in bulk, so nothing marks a path. `pathSpeck` — a path that is a field of
several blocks rather than a laid surface, since a solid path beats a broken one. `rockLost` — a
rock built from the tone family it stands on, which is why sandstone rocks vanish on sand.
`rockFight` — one rock built from two widely separated colours, which is noise rather than variation.

**`course` fires only on a wall or a fill.** A surface stack is depth — turf over subsoil over rock —
and a busy block belongs at the bottom of one. The fault is a busy block laid as a course somebody
sees side-on, which is what mossy cobblestone in a tunnel wall is.

## How well it does

**On the pairs the author named: eleven of twelve.** Every praised pair comes back clean and seven
of eight condemned pairs are flagged. The miss is `Diorite + Andesite`, at 58.3 in RGB against a
cutoff of 60 — left alone rather than tuned to it, since moving a threshold to capture one point is
how a calibration becomes a fit.

**On individual boards it finds what the author found.** `Cobblestone + Mossy Cobblestone` is the
first `soup` on the plains board where the author complained of exactly that; `Sand + Coarse Dirt`
and `Sand + Gravel` are the `mottle` on the desert board whose paths the author called too
contrasting; `Hardened Clay, family brick is the ground's` is the `rockLost` on the badlands board
where the author said the boulders disappear again.

**Summed into one number per board it predicts three of five**, which is worse than `clash` alone
managed. That is the honest limit and it is a finding rather than a defect to tune away: the
readings are worth something one at a time, with the coordinates attached, and adding them together
throws away what each one knew. **Do not build a board score out of these.** The author's own
feedback was a list of places, not a mark out of ten, and this tool is at its best answering in the
same shape.
