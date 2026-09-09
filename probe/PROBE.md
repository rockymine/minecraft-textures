# The colouring probe

An agent is asked to paint a board that is already built, and nothing else. What comes back is scored with
`scorer.py` against the corpus baseline in `BASELINE.md`.

## The board

A **hand-authored map**, not a synthetic fixture. Ten layers over a `rot_180` board: ground cut by a tunnel
whose walls and cover are their own layers, a pillar-and-rim structure standing over it, planters, two wool
rooms, a bedrock approach wall on the seam between two pieces, and a pair of destroyables in cages built for
them. 80 shapes, 10,714 cells, two islands joined by a build zone.

It is the subject because a synthetic board cannot pose the question. Every bucket is reachable — surfaces a
player walks, walls where layers step, fill behind a cut, rim at the board's edge — and the shapes carry the
heights and adjacencies a real board has rather than the ones a fixture was built to have. It was authored
with no paint on it at all, which is the state the probe needs and the state it was finished in.

**No run touches the authored map.** `mint.py` copies its three documents under a fresh slug and drops any
theme registry, so each run gets a pristine board it can be given and thrown away:

```sh
python3 mint.py plains-a      # -> probe-plains-a, at /maps/probe-plains-a/sketch
python3 mint.py --refresh     # re-read the master from the source map, after the author edits it
```

A minted board raises `SK8` (no finish), `SK11` ×3 and `SK20` ×2. All five are true of the document and none
of them is about paint; a run is not being asked to answer them.

## What the agent is told

Deliberately almost nothing. The point is whether *data it can look up* changes what it picks, so the brief
must not carry the advice being tested. **No numbers, no thresholds**, no guidance about pattern width,
family membership or contrast, and none of `AUTHORING-BRIEF.md`'s material section — that prose is the
confound, and it is already known not to work.

> Board `<slug>` is built and unpainted: ten layers, no theme registry. Paint it so it reads like
> **`<a place>`**. Author whatever themes you think it needs and say which shape wears which. Look at what
> you have made before you call it done.
>
> `GET /api/map/<slug>/sketch` is the board and `GET /api/map/<slug>/sketch/layers` its layers.
> `PUT /api/map/<slug>/sketch/themes/{id}` registers a theme, `PUT /api/map/<slug>/sketch/map-theme` says
> which covers everything unclaimed, and `PATCH /api/map/<slug>/sketch/shapes/{shapeId}` puts one on a shape.
> `GET /api/terrain/blocks` is the blocks a material may be built from.
> `POST /api/terrain/theme-preview` renders a finish before you commit to it, and
> `GET /api/map/<slug>/render/surface?format=png` is the board once painted.

Five places worth asking for, chosen to reach different parts of the palette rather than to be hard:
**plains**, **a desert**, **a snowfield**, **badlands**, **a volcanic ashfield**.

## The arms

1. **Control** — the 74 boards already scored in `BASELINE.md`. No new run needed.
2. **Data only** — the palette extended with `contrast`, `colours`, `construction`, `topTexture` and
   `sideTexture` on `GET /api/terrain/blocks`. Brief unchanged from the block above.
3. **Data and a worked example** — the same, plus one demonstration in the brief of *querying* before
   choosing. Only run if arm 2 does not move.

## Reading the result

Score with `scorer.py`; compare the **delta** against the baseline rates, never the absolute against zero —
the mush and clash thresholds are calibrated from the corpus, not derived from anything.

`repeat` is the control **inside** the experiment. It needs no texture knowledge at all, so if a run moves
repeat as much as it moves mush, what improved was attention rather than information.

And look at the boards. The scorer counts pairs; it cannot tell you whether one reads as the place it was
asked for, and a run that scores well and looks wrong means the thresholds measure the wrong thing.

## The synthetic fixtures

`fixture.py` still builds three — `flat` (one height, so the whole paint is the surface bucket), `relief`
(four heights) and `island` (all rim). They are worth keeping for isolating one bucket when a result on the
real board is ambiguous about which one moved. They are not the subject.
