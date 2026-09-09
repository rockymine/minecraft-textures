# Minecraft 1.8.9 block textures, and what they are made of

A working area outside `pgm-studio`, holding Mojang's own assets and the measurements taken from them.
Nothing here is committed to the studio: the assets are Mojang's and the scripts are investigation. What
the studio would take is the *derived table*, the way `BlockPaletteData`'s mean colours were already
derived from this same asset set.

## What is here, and what is not

**The measurements are committed; Mojang's assets are not.** The jar and the sprites unzipped out of it are
theirs, and publishing them would be redistribution — so `.gitignore` keeps both out and the commands below
fetch the jar by the hash Mojang's own metadata declares.

Everything the measurements are *for* works without them. `scorer.py` reads
`block-texture-catalogue.json` and `terrain-blocks.json` and nothing else, so a checkout with no jar can
score a board. Only re-deriving the tables — `catalogue.py`, `emit_look.py`, `make_html.py` — needs the
sprites.

| | |
|---|---|
| `scorer.py` · `faces.py` · `namemap.py` | reads a theme registry and reports what its patterns will look like. No assets needed |
| `baseline.py` · `BASELINE.md` · `baseline.json` | the control: 74 corpus boards scored before any of this reached an agent |
| `block-texture-catalogue.json` | 182 full-cube sprites, each with contrast, colours and how it is constructed |
| `terrain-blocks.json` | the studio's own paintable palette, as `GET /api/terrain/blocks` answered it |
| `catalogue.py` · `features.py` · `inlay.py` · `models.py` · `texmeans.py` | how the catalogue is measured. Needs the jar |
| `emit_look.py` | emits `BlockLookData.cs` into `pgm-studio`. Needs the jar |
| `probe/` | the colouring probe's synthetic fixtures. The real subject is `rockymine-probe` in `pgm-studio-mapgen` |
| `block-textures.html` | every sprite with its numbers, as one self-contained page |

## Provenance

The jar comes from Mojang's published launcher metadata, not from a mirror:

```sh
curl -sS https://launchermeta.mojang.com/mc/game/version_manifest.json          # lists every version
curl -sS https://piston-meta.mojang.com/v1/packages/d546f1707a3f2b7d034eece5ea2e311eda875787/1.8.9.json
curl -sS https://launcher.mojang.com/v1/objects/3870888a6c3d349d3771a3e9d16c9bf5e076b908/client.jar \
     -o client-1.8.9.jar
sha1sum client-1.8.9.jar   # 3870888a6c3d349d3771a3e9d16c9bf5e076b908, the hash the metadata declares
```

`assets-1.8.9/` is the `assets/minecraft/` subtree unzipped out of it: 382 block textures, 1,080 block
models, and the blockstates that bind them.

## How the studio's existing colours were computed

`BlockPaletteData` states one mean RGB per block. Reproducing it from the textures — the alpha-masked mean
of the sprite's opaque pixels, first frame only for an animated strip — matches **73 of 110** paintable
blocks to within two counts per channel, and 37 of them exactly. Every large divergence is a departure the
palette's own docstring already names: a biome-tinted block is multiplied by a fixed temperate tint (grass
is greyscale `#939393` in the file and `#79C05A` in the table), an ore leans on its accent rather than its
mean (coal ore is `#737373` measured and `#373737` stated), and an alpha-heavy block averages only what it
actually draws.

What is *not* explained by a formula is a residue of about a dozen rows sitting 7–10 counts off in the same
direction — andesite, brick, spruce planks, hay, lapis. No averaging convention tested reproduces them:
linear-light, median and alpha-weighted means each fit some rows and miss others, and the plain sRGB mean
is closest overall. **The table is a mean plus hand adjustment**, and it should be read that way rather than
as the output of a pipeline.

## What is measured here

`block-texture-catalogue.json` — one row per full-cube texture (182 of them), carrying three things.

**Where it sits on a block**, resolved from the models, which are the authority rather than a guess:
`uniform` (one sprite on all six faces — stone, andesite, clay), `column` (a side and an end — logs, hay,
smooth sandstone), `bottom-top` (a distinct top and bottom), `faced` (genuinely per-face).

**How it is drawn**, read off the pixels, as flags rather than one exclusive word — stone brick is
bevelled *and* masonry, and saying both is more use than picking one:

| flag | what it means | example |
|---|---|---|
| `inlaid` | another sprite with a material painted into it; `host` names which | every stone ore, on `stone` |
| `masonry` | straight mortar lines — rows or columns that run flat and step away from their neighbours | `stonebrick`, `brick`, `planks_oak` |
| `tiled` | the sprite repeats at a period of 2, 4 or 8 | `brick`, `hay_block_side` |
| `panelled` | few distinct rows or columns — regular structure without a clean period | `quartz_block_side` |
| `bevelled` | a chamfered edge: one border lit and another shaded | `sandstone_smooth`, `quartz_block_side` |
| `dithered` | 150+ distinct colours in 256 pixels — a generated field | `stone_andesite` (213) |
| `ramped` | 12 or fewer colours — drawn from a small hand-picked set | `stone` (5), `planks_oak` (7) |
| `grained-x` / `grained-y` | runs visibly one way | `planks_oak`, `log_oak` |
| `flat` | contrast under 8 | `clay`, `wool` |

**What it reads as**: `contrast` (spread of luma — the noise axis), `colours`, `grain` (neighbour-to-neighbour
change over the spread: speckle against blob), `anisotropy`, `bevel`, and the rank/period/seam counts the
flags are cut from.

## The finding this was taken for

The studio offers an agent one mean RGB per block. Within the `grey stone` and `cobble` families that
number is nearly constant while the textures are not:

| block | mean | contrast | colours | construction |
|---|---|---|---|---|
| Stone | `#7E7E7E` | 11.8 | 5 | ramped noise |
| Cobblestone | `#7A7A7A` | 29.2 | 79 | noise |
| Andesite | `#8A8A8D` | 23.5 | 213 | dithered noise |
| Polished Andesite | `#8E8E91` | 20.4 | 189 | **bevelled** |
| Stone Bricks | — | 18.0 | 42 | **masonry**, bevelled |
| Clay | — | 6.7 | 94 | flat |

Stone and cobblestone are four counts apart per channel and differ by a factor of 2.5 in contrast — which
is why a cobblestone footing on cobblestone ground reads as mush and nothing in the palette says so.
Andesite and its polished variant are four counts apart *and* close in contrast: what separates those two
is the bevel, not the noise. **Contrast alone would not have told them apart**, which is the reason the
construction flags are here and not just a variance number.

## Regenerating

```sh
python3 catalogue.py      # -> block-texture-catalogue.json
```

`models.py` resolves a model's six faces through its parent chain. `texmeans.py` reads sprites and means.
`features.py` measures contrast, grain, ranks, periods, edges and seams. `inlay.py` finds the host a sprite
is painted onto, one-way — the share of matching pixels alone is symmetric and would call stone a variant
of coal ore. `namemap.py` is the one hand-written table, joining a studio `(id, data)` to a texture name;
every row of it is checked against the committed swatch, so a wrong pairing shows up as a colour mismatch
rather than passing silently.
