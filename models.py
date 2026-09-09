"""Resolve 1.8.9 block models to their six face textures, and classify the face layout.

The jar is the authority: a model states its parent and a `textures` map whose values are either
`blocks/<name>` or a `#ref` into a key the child supplies. Resolving the chain gives, per block model,
the texture on each of the six faces — which is what says whether a block wears one sprite everywhere,
a side-and-end pair, or a distinct top and bottom.
"""
import json, pathlib, functools

ROOT = pathlib.Path(__file__).parent / "assets-1.8.9/assets/minecraft"
FACES = ("down", "up", "north", "south", "east", "west")


@functools.lru_cache(maxsize=None)
def model(name):
    p = ROOT / "models" / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def resolve(name):
    """The merged texture map for a model, parents first, `#refs` followed to a real texture path."""
    chain, seen = [], set()
    cur = name
    while cur and cur not in seen:
        seen.add(cur)
        m = model(cur)
        if m is None:
            break
        chain.append(m)
        cur = m.get("parent")
    if not chain:
        return None, None
    textures = {}
    for m in reversed(chain):           # parent first, child overrides
        textures.update(m.get("textures", {}))

    def deref(v, depth=0):
        while isinstance(v, str) and v.startswith("#") and depth < 8:
            v = textures.get(v[1:])
            depth += 1
        return v

    faces = {f: deref(textures.get(f)) for f in FACES}
    root_parent = chain[-1].get("parent") or name
    return faces, chain[0].get("parent")


def layout(faces):
    """How the six faces are dressed — the user's first three categories, read off the model."""
    vals = [faces[f] for f in FACES]
    if any(v is None for v in vals):
        return "partial"                       # not a full cube (stairs, slabs, plants, ...)
    distinct = set(vals)
    if len(distinct) == 1:
        return "uniform"                       # one sprite on all six (stone, andesite, clay)
    down, up, side = faces["down"], faces["up"], faces["north"]
    sides = {faces[f] for f in ("north", "south", "east", "west")}
    if len(sides) == 1 and down == up and down != side:
        return "column"                        # side + end (logs, quartz pillar, hay)
    if len(sides) == 1 and down != up:
        return "bottom-top"                    # distinct top and bottom (grass, sandstone, TNT)
    return "faced"                             # genuinely per-face
