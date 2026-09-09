"""The full-cube block textures of 1.8.9, described by how they are constructed.

Three things are stated per texture. **Where it sits on a block** comes from the models in the jar, which
are the authority: one sprite on all six faces, a side-and-end pair, a distinct top and bottom, or a
genuinely per-face cube. **How it is drawn** is read off the pixels: whether it is another sprite with
something painted into it, whether it repeats, whether it carries a chamfered edge, and how much it
varies. **What it reads as** is the small set of numbers a caller can compare two blocks on.

Flags are not exclusive. Stone brick is bevelled *and* panelled, and saying so is more use than forcing
one word on it.
"""
import json, pathlib
import features, inlay, models

HERE = pathlib.Path(__file__).parent


def build():
    full = json.load(open(HERE / "full-cube-textures.json"))
    names = list(full)
    hosts = inlay.roots(names)

    out = {}
    for n in names:
        try:
            f, e = features.features(n), features.edges(n)
            s = features.seams(n) or {"seamRows": 0, "seamCols": 0}
        except Exception:
            continue
        if not f or not e:
            continue
        flags = []
        if hosts.get(n):
            flags.append("inlaid")
        if max(f["rowPeriod"], f["colPeriod"]) >= 0.40:
            flags.append("tiled")
        # An inlay's blobs are not mortar: a sprite painted onto a host carries the host's construction,
        # so the seam read belongs to the host and is not repeated here.
        if max(s["seamRows"], s["seamCols"]) >= 1 and not hosts.get(n):
            flags.append("masonry")
        if min(f["rowRank"], f["colRank"]) <= 12:
            flags.append("panelled")
        if e["bevel"] >= 0.50:
            flags.append("bevelled")
        if f["contrast"] < 8:
            flags.append("flat")
        if f["colours"] >= 150:
            flags.append("dithered")
        elif f["colours"] <= 12:
            flags.append("ramped")
        if abs(f["anisotropy"]) >= 0.35:
            flags.append("grained-x" if f["anisotropy"] > 0 else "grained-y")
        if not flags or flags == ["ramped"] or flags == ["dithered"]:
            flags.append("noise")

        out[n] = {
            "faces": sorted(full[n]),
            "host": hosts.get(n),
            "flags": flags,
            "contrast": round(f["contrast"], 1),
            "colours": f["colours"],
            "grain": round(f["grain"], 2),
            "anisotropy": round(f["anisotropy"], 2),
            "bevel": round(e["bevel"], 2),
            "rowRank": f["rowRank"], "colRank": f["colRank"],
            "rowPeriod": round(f["rowPeriod"], 2), "colPeriod": round(f["colPeriod"], 2),
            "seamRows": s["seamRows"], "seamCols": s["seamCols"],
        }
    return out


if __name__ == "__main__":
    cat = build()
    json.dump(cat, open(HERE / "block-texture-catalogue.json", "w"), indent=1, sort_keys=True)
    print(f"catalogued {len(cat)} full-cube textures -> block-texture-catalogue.json")
