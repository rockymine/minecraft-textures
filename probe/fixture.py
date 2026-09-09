"""The colouring fixtures: boards with geometry and no paint.

Three boards, each a set of regions that tile it. Nothing about any of them suggests a material — regions
are named for where they are and what shape they have, never for what they might be made of — and every
theme registry is empty. The whole of an agent's job is to fill `themes` and say which region wears which.

The three differ only in which buckets they can reach, so a run says where a fault lives rather than only
that one exists:

  flat    every region at one height. No wall is ever cut, so the whole of the paint is the SURFACE
          bucket — the face a player looks at for the length of a match, and where 57% of the corpus
          baseline's mush sits.
  relief  five regions at four heights, so every internal boundary is a wall. Surface, wall and fill all
          paint, and a block chosen for the top has to answer for its side as well.
  island  one landmass in void, so every edge is a rim. Adds the one bucket the other two never reach.
"""
import json, pathlib

BOARD = 60

# id, min_x, min_z, max_x, max_z, height
FLAT = [
    ("west-field",  -60, -60, -20,  60, 12),
    ("north-field", -20, -60,  60, -20, 12),
    ("mid-field",   -20, -20,  22,  22, 12),
    ("east-field",   22, -20,  60,  22, 12),
    ("south-field", -20,  22,  60,  60, 12),
]

RELIEF = [
    ("west-flat",   -60, -60, -15,  60, 12),
    ("north-flat",  -15, -60,  60, -25, 12),
    ("centre-rise", -15, -25,  20,  25, 20),
    ("east-shelf",   20, -25,  60,  25, 15),
    ("south-low",   -15,  25,  60,  60,  8),
]

ISLAND = [
    ("shore-west",  -46, -34, -14,  34, 10),
    ("crown",       -14, -34,  18,  34, 16),
    ("shore-east",   18, -34,  46,  34, 10),
    ("spit-north",  -14, -50,  18, -34, 10),
]

BOARDS = {"flat": FLAT, "relief": RELIEF, "island": ISLAND}


def layout(regions):
    return {
        "setup": {"mirror_mode": "none", "center": {"cx": 0, "cz": 0},
                  "bbox": {"min_x": -BOARD, "max_x": BOARD, "min_z": -BOARD, "max_z": BOARD}},
        "layers": [{"id": "ground", "name": "Ground", "base_y": 0, "layout": {
            "shapes": [{"id": rid, "type": "rectangle", "operation": "add", "override": False,
                        "min_x": x0, "min_z": z0, "max_x": x1, "max_z": z1,
                        "floor": 0, "base_height": h}
                       for rid, x0, z0, x1, z1, h in regions],
            "groups": [{"id": "board", "name": "The board", "mirrors": False,
                        "shapeIds": [r[0] for r in regions]}]}}],
        "themes": {},
    }


def intent(name, regions):
    """Two spawns on the two widest regions, far apart, and an observer over the middle. Deliberately no
    objective: nothing here is played, and a goal would put blocks on the ground being judged."""
    first, last = regions[0], regions[-1]
    def mid(r, inset=12):
        return ((r[1] + r[3]) // 2, (r[2] + r[4]) // 2, r[5])
    (rx, rz, rh), (bx, bz, bh) = mid(first), mid(last)
    return {
        "teams": [{"id": "red", "name": "Red", "color": "red"},
                  {"id": "blue", "name": "Blue", "color": "blue"}],
        "maxPlayers": 8,
        "spawns": [
            {"team": "red", "point": {"x": rx, "y": rh + 1, "z": rz}, "yaw": 135,
             "protection": [{"minX": rx - 8, "minZ": rz - 8, "maxX": rx + 8, "maxZ": rz + 8}]},
            {"team": "blue", "point": {"x": bx, "y": bh + 1, "z": bz}, "yaw": -45,
             "protection": [{"minX": bx - 8, "minZ": bz - 8, "maxX": bx + 8, "maxZ": bz + 8}]}],
        "observer": {"point": {"x": 0, "y": 46, "z": -BOARD - 10}, "yaw": 180},
        "build": {"maxHeight": 40, "areas": [], "holes": [], "voidEnforcement": {"exclusions": []}},
        "wools": [], "destroyables": [],
        "meta": {"name": name, "authors": [], "contributors": []},
    }


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    for key, regions in BOARDS.items():
        name = f"Colour probe — {key}"
        (here / f"{key}.layout.json").write_text(json.dumps(layout(regions), indent=1))
        (here / f"{key}.intent.json").write_text(json.dumps(intent(name, regions), indent=1))
        heights = sorted({r[5] for r in regions})
        print(f"  {key:8s} {len(regions)} regions, heights {heights}")
