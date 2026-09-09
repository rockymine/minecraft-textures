"""Structural features of a 16x16 block sprite — what the texture is made of, not what colour it averages to.

Every measure is scale-free where it can be, so a dark texture and a light one with the same construction
land in the same place. Luma is Rec.601 over the opaque pixels; a sprite with holes is measured on what it
actually draws.
"""
import numpy as np
import texmeans

LUMA = np.array([0.299, 0.587, 0.114])


def luma(name):
    rgb, a = texmeans.sprite(name)
    return rgb @ LUMA, a


def features(name):
    y, a = luma(name)
    rgb, _ = texmeans.sprite(name)
    h, w = y.shape
    opaque = a > 127
    f = {"w": w, "h": h, "opaque": float(opaque.mean())}

    v = y[opaque]
    if v.size < 16:
        return None
    f["mean"] = float(v.mean())
    f["contrast"] = float(v.std())                       # the noise axis: spread of brightness
    f["range"] = float(v.max() - v.min())

    # How many colours the sprite is drawn from. A hand-drawn tile uses few; a photographic-looking
    # noise field uses many.
    cols = rgb[opaque].astype(np.int32)
    f["colours"] = int(len({tuple(c) for c in cols}))

    # Speckle against blob: neighbouring-pixel difference over the whole spread. High means the texture
    # changes every pixel (cobble, ore flecks); low means large flat regions (bricks, planks).
    dx = np.abs(np.diff(y, axis=1)).mean()
    dy = np.abs(np.diff(y, axis=0)).mean()
    f["grain"] = float((dx + dy) / 2 / (v.std() + 1e-9))
    # Which way the texture runs. >0 means it varies more across x than down y (horizontal banding).
    f["anisotropy"] = float((dy - dx) / (dy + dx + 1e-9))

    # Regular structure: how many rows and columns are distinct at a tolerance of one step of the ramp.
    def ranks(arr):
        seen = []
        for row in arr:
            if not any(np.abs(row - s).max() <= 6 for s in seen):
                seen.append(row)
        return len(seen)
    f["rowRank"] = ranks(y)
    f["colRank"] = ranks(y.T)

    # A rim: an outer ring that is near-uniform and stands away from the middle.
    def rim(width):
        ring = np.ones((h, w), bool)
        ring[width:h - width, width:w - width] = False
        ring &= opaque
        core = opaque & ~ring
        if ring.sum() < 8 or core.sum() < 8:
            return 0.0, 0.0
        return float(y[ring].std()), float(abs(y[ring].mean() - y[core].mean()))
    f["rim1Std"], f["rim1Step"] = rim(1)
    f["rim2Std"], f["rim2Step"] = rim(2)

    # Does the sprite tile with itself at half period? A brick course repeats every 8 rows.
    def period(arr, axis):
        best = 0.0
        n = arr.shape[axis]
        for p in (2, 4, 8):
            a1 = np.take(arr, range(0, n - p), axis=axis)
            a2 = np.take(arr, range(p, n), axis=axis)
            best = max(best, 1.0 - np.abs(a1 - a2).mean() / (np.abs(arr - arr.mean()).mean() + 1e-9))
        return float(best)
    f["rowPeriod"] = period(y, 0)
    f["colPeriod"] = period(y, 1)
    return f


def derived_from(name, bases, tol=8):
    """The candidate base this sprite is a repaint of, and what share of pixels it leaves untouched.

    An ore is its host rock with a mineral drawn into it, so most of its pixels are the host's own,
    pixel for pixel. Reported as the best base and the share matched.
    """
    rgb, a = texmeans.sprite(name)
    best = (0.0, None)
    for b in bases:
        if b == name:
            continue
        try:
            brgb, ba = texmeans.sprite(b)
        except Exception:
            continue
        if brgb.shape != rgb.shape:
            continue
        same = (np.abs(rgb - brgb).max(axis=2) <= tol) & (a > 127) & (ba > 127)
        share = same.sum() / max(1, (a > 127).sum())
        if share > best[0]:
            best = (float(share), b)
    return best


def edges(name):
    """How each of the four borders stands away from the middle, in units of the middle's own spread.

    A bevel is drawn as a lit edge and a shaded one — the block reads as a solid with a chamfer — so what
    identifies it is not one edge standing out but two standing out the opposite way.
    """
    y, a = luma(name)
    op = a > 127
    core = np.zeros_like(op)
    core[2:-2, 2:-2] = True
    core &= op
    if core.sum() < 16:
        return None
    cm, cs = y[core].mean(), y[core].std() + 1e-9
    step = {
        "top": (y[0][op[0]].mean() - cm) / cs if op[0].any() else 0.0,
        "bottom": (y[-1][op[-1]].mean() - cm) / cs if op[-1].any() else 0.0,
        "left": (y[:, 0][op[:, 0]].mean() - cm) / cs if op[:, 0].any() else 0.0,
        "right": (y[:, -1][op[:, -1]].mean() - cm) / cs if op[:, -1].any() else 0.0,
    }
    vals = list(step.values())
    step["spanLit"] = float(max(vals))
    step["spanShaded"] = float(min(vals))
    # A chamfer: one border lit and another shaded, both clearly away from the middle.
    step["bevel"] = float(min(max(vals), -min(vals)))
    return {k: float(v) for k, v in step.items()}


def seams(name):
    """Straight mortar lines: rows and columns that run flat along their whole length and step away from
    what is either side of them. It is what makes a masonry texture read as masonry rather than as noise,
    and it survives courses that do not repeat at any period — stone brick is laid to no clean rhythm and
    is unmistakably brickwork.
    """
    y, a = luma(name)
    op = a > 127
    if op.mean() < 0.6:
        return None
    spread = y[op].std() + 1e-9

    def count(arr):
        n, hits = arr.shape[0], 0
        for i in range(1, n - 1):
            line = arr[i]
            flat = line.std() / spread                       # runs flat along its length
            step = abs(line.mean() - (arr[i - 1].mean() + arr[i + 1].mean()) / 2) / spread
            if flat < 0.45 and step > 0.55:
                hits += 1
        return hits

    return {"seamRows": count(y), "seamCols": count(y.T)}
