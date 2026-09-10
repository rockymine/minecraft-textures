"""Score a terrain theme on what its patterns will actually look like.

Three readings, and they are measurements rather than gates — nothing here refuses anything. Each is taken
per *pattern*, over the blocks that pattern picks between, and in the face the pattern's bucket is seen
from: the surface and rim buckets are read from above, the wall and fill buckets from the side.

  repeat    the same block listed twice in one pattern. A document fault, and the one reading here that
            needs no texture knowledge at all — kept separate for exactly that reason, since counting it
            as a texture finding would flatter the data it is meant to test. Two different things wear
            this name: `[grass, grass, dirt, grass]`, which is a slip, and `[grass x10, coarse_dirt]`,
            which is an author weighting a noise by repeating a stop. `distinct=True` dedupes each
            pattern before reading it, which drops the weighting and leaves the palette choice.
  collapse  two DIFFERENT blocks that resolve to the same sprite on that face. The pattern has fewer
            blocks in it than the document says, and only the face data can tell. Sandstone and smooth
            sandstone in a surface pattern are one block; in a wall pattern they are two.
  mush      two blocks of one tone family whose contrast is within a third of each other. Nothing tells
            them apart at distance — a cobble footing on cobble ground.
  clash     two blocks of near-identical mean colour whose contrast differs by more than 2.5x. The colour
            says one ground and the grain says two, which reads as a seam — mossy cobble against stone.

Collapse is the honest headline: it is a fact about sprites, not a threshold anyone chose. Mush and clash
carry numbers picked from the corpus and should be read as supporting.
"""
import json, math, pathlib, itertools, collections
import faces

HERE = pathlib.Path(__file__).parent
CAT = json.load(open(HERE / "block-texture-catalogue.json"))
PAINT = {(b["id"], b["data"]): b for b in json.load(open(HERE / "terrain-blocks.json"))}

# Which face a bucket is seen from. Surface and rim are the courses a player walks on; wall is the vertical
# face of cut terrain and fill is what shows behind it, so both are read from the side.
BUCKET_FACE = {"surface": 0, "rim": 0, "wall": 1, "fill": 1}

# Patterns that pick between blocks laid side by side in the plane. A `layered` stack is deliberately not
# here: its members are courses at different depths, which is a different question from two blocks meeting.
PICK_MEMBERS = {
    "noise": "stops", "turbulence": "stops", "electric": "stops",
    "cell": "palette", "voronoi": "bands",
    "wallRun": "runs", "wallDiagonal": "runs",
}

MUSH_RATIO, CLASH_RATIO, CLASH_RGB = 1.34, 2.5, 42.0


def _blocks(node, out):
    """Every solid this material subtree resolves to, as (id, data)."""
    if isinstance(node, dict):
        if node.get("kind") == "solid" and "id" in node:
            out.append((int(node["id"]), int(node.get("data", 0))))
            return
        for v in node.values():
            _blocks(v, out)
    elif isinstance(node, list):
        for v in node:
            _blocks(v, out)


def patterns(node, bucket, found):
    """Every picking pattern in a bucket's material, with the blocks it picks between."""
    if isinstance(node, dict):
        kind = node.get("kind")
        if kind in PICK_MEMBERS:
            members = node.get(PICK_MEMBERS[kind])
            if isinstance(members, list) and len(members) > 1:
                picks = []
                for m in members:
                    got = []
                    _blocks(m.get("material", m) if isinstance(m, dict) else m, got)
                    if got:
                        picks.append(got[0])          # the block that member reads as
                if len(picks) > 1:
                    found.append({"bucket": bucket, "kind": kind, "blocks": picks})
        if kind == "checker":
            got = []
            _blocks(node, got)
            if len(got) > 1:
                found.append({"bucket": bucket, "kind": "checker", "blocks": got[:2]})
        for v in node.values():
            patterns(v, bucket, found)
    elif isinstance(node, list):
        for v in node:
            patterns(v, bucket, found)
    return found


def _info(block, face):
    """The sprite this block shows on a face, and what that sprite reads as."""
    b = PAINT.get(block)
    tex = faces.faces(*block)[face]
    v = CAT.get(tex) if tex else None
    if not v:
        return None
    hexes = b["hex"] if b else None
    rgb = tuple(int(hexes[i:i + 2], 16) for i in (1, 3, 5)) if hexes else None
    return {"tex": tex, "contrast": v["contrast"], "rgb": rgb,
            "family": b["group"] if b else None, "name": b["name"] if b else tex}


def score_theme(theme, theme_id="?", distinct=False):
    """Every finding in one theme, plus how much of it could be read at all."""
    found, unknown, pairs = [], 0, 0
    for bucket, face in BUCKET_FACE.items():
        node = theme.get(bucket)
        if node is None:
            continue
        if bucket in ("surface", "rim"):
            if node.get("enabled") is False:
                continue
            node = node.get("material")
        elif bucket == "wall" and theme.get("wallEnabled") is False:
            continue
        if node is None:
            continue
        for pat in patterns(node, bucket, []):
            blocks = pat["blocks"]
            if distinct:
                seen, kept = set(), []
                for b in blocks:
                    if b not in seen:
                        seen.add(b)
                        kept.append(b)
                blocks = kept
            infos = []
            for b in blocks:
                i = _info(b, face)
                if i is None:
                    unknown += 1
                else:
                    infos.append(i)
            for a, b in itertools.combinations(infos, 2):
                pairs += 1
                lo, hi = sorted((a["contrast"], b["contrast"]))
                ratio = hi / max(0.1, lo)
                rgbd = (math.dist(a["rgb"], b["rgb"])
                        if a["rgb"] and b["rgb"] else None)
                shared = a["family"] and a["family"] == b["family"]
                if a["name"] == b["name"]:
                    kind = "repeat"
                elif a["tex"] == b["tex"]:
                    kind = "collapse"
                elif shared and ratio < MUSH_RATIO:
                    kind = "mush"
                elif rgbd is not None and rgbd < CLASH_RGB and ratio > CLASH_RATIO:
                    kind = "clash"
                else:
                    continue
                found.append({"theme": theme_id, "bucket": pat["bucket"], "pattern": pat["kind"],
                              "kind": kind, "a": a["name"], "b": b["name"], "tex": a["tex"],
                              "ratio": round(ratio, 2),
                              "rgbd": round(rgbd, 1) if rgbd is not None else None})
    return found, pairs, unknown


def score_registry(themes, distinct=False):
    out, pairs, unknown = [], 0, 0
    for tid, t in themes.items():
        if not isinstance(t, dict):
            continue
        f, p, u = score_theme(t, tid, distinct)
        out += f
        pairs += p
        unknown += u
    return out, pairs, unknown
