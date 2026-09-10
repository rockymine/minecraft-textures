"""Score a whole painted board on how its materials sit beside each other.

`scorer.py` reads a theme registry and asks one question of every pair of blocks a pattern picks
between. That misses most of what goes wrong on a board, because a path's fault is its relation to
the ground it crosses and a rock's is its relation to the ground it stands on. This reads the sketch
document instead: the registry, the materials stated on shapes, the strokes, the rocks.

Every threshold here is calibrated against one author's rulings on ten boards, named in `RULES.md`.
They are a reading, not a law, and nothing here belongs in the studio.

The readings, and what each is built from:

  repeat     the same block twice in one pattern, over distinct blocks. Document hygiene; needs no
             texture knowledge, which is why it is counted apart.
  collapse   two different blocks wearing one sprite on the face that pattern is seen from. A fact
             about the assets rather than a threshold.
  soup       two blocks of one tone family, close in contrast, AND BOTH NOISY. The noise floor is
             what `mush` was missing: snow beside quartz and grey clay beside black are one family
             and close in contrast and read as one weathered ground, which is what a surface wants.
             Cobble beside mossy cobble is the same relation between two busy blocks and reads as
             soup. The fault is two loud blocks, not two quiet ones.
  mottle     a wide colour distance between families INSIDE A SPECKLED pattern. The same three
             blocks arranged in rings read as deliberate; scattered as specks they read as a mess,
             so the pattern's grain decides whether the distance is a fault.
  crowd      more than three distinct blocks in one surface pattern.
  course     a noisy block used as a course in a band stack. A busy texture is a speck, not a layer.
  clash      near-identical colour, contrast differing sharply. Carried unchanged from `scorer.py`.
  pathEcho   a path laid in blocks the ground it crosses already carries in bulk, so nothing says a
             path is there. Specks of the same block in the ground are fine and are what make the
             path read as chosen.
  pathSpeck  a path that is a field of several blocks rather than a laid surface.
  rockLost   a rock built from the tone family of the ground it stands on.
  rockFight  one rock built from two blocks of widely separated colour.
"""
import json, math, itertools, collections, pathlib, sys
import scorer, faces

CAT, PAINT = scorer.CAT, scorer.PAINT

# Calibrated on the author's named pairs. Praised pairs top out at 8.7 contrast; the pairs called
# soup start at 22. A block at or above this reads as busy on its own.
NOISE_FLOOR = 15.0
MUSH_RATIO  = scorer.MUSH_RATIO          # one family, contrast within a third
CLASH_RATIO, CLASH_RGB = scorer.CLASH_RATIO, scorer.CLASH_RGB
WIDE_RGB    = 60.0                       # predicts the author's board preference 4 of 5
CROWD       = 3                          # "five materials in a platform floor is a mottle"
ECHO_SHARE  = 0.25                       # a block holding a quarter of the ground's stops is bulk

# How a pattern arranges what it picks between. A wide colour spread is deliberate when the
# arrangement is large and a mess when it is fine, so grain decides whether distance is a fault.
SPECKLE   = {"noise", "turbulence", "cell"}
STRUCTURED = {"electric", "voronoi", "wallRun", "wallDiagonal", "checker"}
BUCKET_FACE = scorer.BUCKET_FACE


def look(block, face):
    """What one block reads as on a face: its sprite, contrast, mean colour and tone family."""
    entry = PAINT.get(block)
    tex = faces.faces(*block)[face]
    cat = CAT.get(tex) if tex else None
    if not cat:
        return None
    hexes = entry["hex"] if entry else None
    rgb = tuple(int(hexes[i:i + 2], 16) for i in (1, 3, 5)) if hexes else None
    return {"name": entry["name"] if entry else tex, "tex": tex, "contrast": cat["contrast"],
            "rgb": rgb, "family": entry["group"] if entry else None}


def solids(node, out=None):
    """Every solid a material subtree resolves to, in document order."""
    out = [] if out is None else out
    if isinstance(node, dict):
        if node.get("kind") == "solid" and "id" in node:
            out.append((int(node["id"]), int(node.get("data", 0))))
            return out
        for v in node.values():
            solids(v, out)
    elif isinstance(node, list):
        for v in node:
            solids(v, out)
    return out


def picks(node, found=None):
    """Every pattern that picks between blocks in the plane, with its kind and its members."""
    found = [] if found is None else found
    if isinstance(node, dict):
        kind = node.get("kind")
        if kind in scorer.PICK_MEMBERS:
            members = node.get(scorer.PICK_MEMBERS[kind])
            if isinstance(members, list) and len(members) > 1:
                blocks = []
                for m in members:
                    got = solids(m.get("material", m) if isinstance(m, dict) else m)
                    if got:
                        blocks.append(got[0])
                if len(blocks) > 1:
                    found.append({"kind": kind, "blocks": blocks})
        elif kind == "checker":
            got = solids(node)
            if len(got) > 1:
                found.append({"kind": "checker", "blocks": got[:2]})
        for v in node.values():
            picks(v, found)
    elif isinstance(node, list):
        for v in node:
            picks(v, found)
    return found


def courses(node, found=None):
    """Every band stack, with the blocks laid as its courses."""
    found = [] if found is None else found
    if isinstance(node, dict):
        bands = node.get("bands") if node.get("kind") in (None, "stack", "layered") else None
        if isinstance(bands, list) and len(bands) > 1:
            blocks = []
            for band in bands:
                got = solids(band.get("material", band) if isinstance(band, dict) else band)
                if got:
                    blocks.append(got[0])
            if len(blocks) > 1:
                found.append(blocks)
        for v in node.values():
            courses(v, found)
    elif isinstance(node, list):
        for v in node:
            courses(v, found)
    return found


def shapes_of(doc):
    """Every shape on the board, with the layer height it sits at."""
    out = []
    for layer in doc.get("layers") or []:
        base = layer.get("base_y") or 0
        for shape in (layer.get("layout") or {}).get("shapes") or []:
            out.append((base + (shape.get("floor") or 0), shape))
    return out


def ground_under(doc, x, z):
    """The theme covering (x, z): the highest shape whose extent holds it, else the map default.

    Extent rather than outline, so a point just outside a concave shape can be attributed to it.
    That is a looser answer than the painter's and is stated as such — it decides which theme a
    rock is judged against, not what the world holds.
    """
    best, best_h = None, None
    for height, shape in shapes_of(doc):
        if shape.get("min_x") is None:
            continue
        if shape["min_x"] <= x <= shape["max_x"] and shape["min_z"] <= z <= shape["max_z"]:
            if best_h is None or height >= best_h:
                best, best_h = shape, height
    themes = doc.get("themes") or {}
    if best is not None:
        if best.get("material"):
            return {"surface": best["material"]}, f"shape:{best.get('id','?')}"
        if best.get("theme") and best["theme"] in themes:
            return themes[best["theme"]], f"theme:{best['theme']}"
    default = doc.get("mapTheme")
    return (themes.get(default) or {}), f"theme:{default}"


def surface_blocks(theme):
    """The blocks a theme's surface picks between, and how many stops each holds."""
    node = theme.get("surface")
    if isinstance(node, dict):
        if node.get("enabled") is False:
            return collections.Counter(), 0
        node = node.get("material", node)
    if node is None:
        return collections.Counter(), 0
    every = solids(node)
    return collections.Counter(every), len(every)


def pair_readings(blocks, face, kind, where, out):
    """Every reading over one pattern's distinct blocks."""
    seen, distinct = set(), []
    for b in blocks:
        if b not in seen:
            seen.add(b)
            distinct.append(b)
    infos = [i for i in (look(b, face) for b in distinct) if i]
    if len(distinct) > CROWD:
        out.append({"kind": "crowd", "where": where, "pattern": kind,
                    "detail": f"{len(distinct)} blocks in one pattern",
                    "a": infos[0]["name"] if infos else "?", "b": ""})
    pairs = 0
    for a, b in itertools.combinations(infos, 2):
        pairs += 1
        lo, hi = sorted((a["contrast"], b["contrast"]))
        ratio = hi / max(0.1, lo)
        dist = math.dist(a["rgb"], b["rgb"]) if a["rgb"] and b["rgb"] else None
        same = a["family"] and a["family"] == b["family"]
        row = {"where": where, "pattern": kind, "a": a["name"], "b": b["name"],
               "ratio": round(ratio, 2), "rgbd": round(dist, 1) if dist is not None else None,
               "contrast": [a["contrast"], b["contrast"]]}
        if a["name"] == b["name"]:
            out.append({**row, "kind": "repeat"})
        elif a["tex"] == b["tex"]:
            out.append({**row, "kind": "collapse"})
        elif same and ratio < MUSH_RATIO and min(a["contrast"], b["contrast"]) >= NOISE_FLOOR:
            out.append({**row, "kind": "soup"})
        elif (not same) and dist is not None and dist > WIDE_RGB and kind in SPECKLE:
            out.append({**row, "kind": "mottle"})
        elif dist is not None and dist < CLASH_RGB and ratio > CLASH_RATIO:
            out.append({**row, "kind": "clash"})
    return pairs


def score(doc):
    """Every reading on one board, and how many block pairs were examined."""
    out, pairs = [], 0
    themes = doc.get("themes") or {}

    for tid, theme in themes.items():
        if not isinstance(theme, dict):
            continue
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
            for pat in picks(node):
                pairs += pair_readings(pat["blocks"], face, pat["kind"],
                                       f"theme:{tid}/{bucket}", out)
            # Only on a face a player sees side-on. A surface stack is depth — turf over subsoil over
            # rock — and a busy block is right at the bottom of one; the fault is a busy block laid as
            # a visible course.
            for stack in (courses(node) if bucket in ("wall", "fill") else []):
                for block in dict.fromkeys(stack):
                    info = look(block, face)
                    if info and info["contrast"] >= NOISE_FLOOR:
                        out.append({"kind": "course", "where": f"theme:{tid}/{bucket}",
                                    "pattern": "bands", "a": info["name"], "b": "",
                                    "detail": f"contrast {info['contrast']} laid as a course"})

    for height, shape in shapes_of(doc):
        mat = shape.get("material")
        if not mat:
            continue
        for pat in picks(mat):
            pairs += pair_readings(pat["blocks"], 0, pat["kind"],
                                   f"shape:{shape.get('id','?')}", out)

    dressing = doc.get("dressing") or {}
    styles = dressing.get("styles") or {}
    for prop in dressing.get("props") or []:
        kind = prop.get("kind")
        if kind == "stroke":
            pave = prop.get("pave")
            if not pave:
                continue
            laid = solids(pave)
            if not laid:
                continue
            pat = picks(pave)
            members = len(dict.fromkeys(laid))
            if members > 2 and any(p["kind"] in SPECKLE for p in pat):
                out.append({"kind": "pathSpeck", "where": f"stroke:{prop.get('id','?')}",
                            "pattern": pat[0]["kind"], "a": f"{members} blocks", "b": "",
                            "detail": "a field rather than a laid surface"})
            points = prop.get("points") or []
            if points:
                x, z = points[len(points) // 2][:2]
                theme, src = ground_under(doc, x, z)
                held, total = surface_blocks(theme)
                for block in dict.fromkeys(laid):
                    share = held.get(block, 0) / total if total else 0
                    if share > ECHO_SHARE:
                        info = look(block, 0)
                        out.append({"kind": "pathEcho", "where": f"stroke:{prop.get('id','?')}",
                                    "pattern": src, "a": info["name"] if info else str(block),
                                    "b": "", "at": [x, z],
                                    "detail": f"{share:.0%} of the ground it crosses"})
        elif kind == "boulder":
            style = styles.get(prop.get("style")) or {}
            rock = style.get("rock")
            if not rock:
                continue
            blocks = list(dict.fromkeys(solids(rock)))
            infos = [i for i in (look(b, 0) for b in blocks) if i]
            x, z = prop.get("x"), prop.get("z")
            if x is not None:
                theme, src = ground_under(doc, x, z)
                held, _ = surface_blocks(theme)
                gfam = {look(b, 0)["family"] for b in held if look(b, 0)}
                for info in infos:
                    if info["family"] and info["family"] in gfam:
                        out.append({"kind": "rockLost", "where": f"boulder:{prop.get('id','?')}",
                                    "pattern": prop.get("style", "?"), "a": info["name"], "b": "",
                                    "at": [x, z], "detail": f"family {info['family']} is the ground's"})
                        break
            for a, b in itertools.combinations(infos, 2):
                if a["rgb"] and b["rgb"]:
                    dist = math.dist(a["rgb"], b["rgb"])
                    if dist > WIDE_RGB:
                        out.append({"kind": "rockFight", "where": f"boulder:{prop.get('id','?')}",
                                    "pattern": prop.get("style", "?"), "a": a["name"], "b": b["name"],
                                    "at": [x, z], "rgbd": round(dist, 1)})
    return out, pairs


def score_file(path):
    return score(json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig")))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        rows, pairs = score_file(arg)
        counted = collections.Counter(r["kind"] for r in rows)
        print(f"{pathlib.Path(arg).stem:28s} pairs {pairs:4d}  " +
              "  ".join(f"{k} {counted[k]}" for k in
                        ("repeat", "collapse", "soup", "mottle", "crowd", "course",
                         "clash", "pathEcho", "pathSpeck", "rockLost", "rockFight") if counted[k]))
