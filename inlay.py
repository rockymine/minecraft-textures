"""Which sprite a sprite was painted on top of.

An ore is its host rock with a mineral drawn into it: most of its pixels are the host's own, pixel for
pixel, and the rest are a tight colour cluster the host does not contain. That asymmetry is what tells
host from inlay — the share of matching pixels alone is symmetric and names stone a variant of coal ore
as readily as the other way round.
"""
import numpy as np
import texmeans

LUMA = np.array([0.299, 0.587, 0.114])


def against(name, base, tol=8):
    rgb, a = texmeans.sprite(name)
    brgb, ba = texmeans.sprite(base)
    if rgb.shape != brgb.shape:
        return None
    op = (a > 127) & (ba > 127)
    if op.sum() < 32:
        return None
    same = (np.abs(rgb - brgb).max(axis=2) <= tol) & op
    share = same.sum() / op.sum()
    diff = op & ~same
    if diff.sum() < 4 or share < 0.35:
        return None

    inlay = rgb[diff]                       # the pixels this sprite painted in
    host = brgb[op]                         # everything the base is made of
    # Tight: the inlay is one material, not a second whole texture.
    spread = float(np.linalg.norm(inlay.std(axis=0)))
    # Distinct: how far the inlay's colour sits from the host's own, as an RGB distance in units of the
    # host's own spread. Measured in colour and not in brightness, because an emerald green and the grey
    # it is set in are the same luma and nothing alike.
    hs = float(np.linalg.norm(host.std(axis=0))) + 1e-9
    distinct = float(np.linalg.norm(inlay.mean(axis=0) - host.mean(axis=0)) / hs)
    return {"base": base, "share": float(share), "spread": spread, "distinct": distinct,
            "cover": float(diff.sum() / op.sum())}


def asymmetry(name, base, tol=8):
    """How much more this sprite reads as an inlay on the base than the base does on it. A true inlay is
    one-way — coal drawn into stone stands out from stone, where the grey it covers does not stand out
    from coal — and two sprites that merely resemble each other score alike in both directions."""
    a, b = against(name, base, tol), against(base, name, tol)
    if a is None:
        return None
    a["reverse"] = b["distinct"] if b else 0.0
    return a


def best(name, candidates, tol=8):
    """The host this sprite reads as an inlay on, or None. Scored on distinctness rather than share, so
    the host is the plain rock and not another ore that happens to share the same matrix."""
    out = []
    import features
    for b in candidates:
        if b == name:
            continue
        try:
            if features.features(b)["contrast"] < 6:      # nothing is inlaid into a flat colour
                continue
            r = asymmetry(name, b, tol)
        except Exception:
            continue
        if r and r["distinct"] >= 0.8 and r["cover"] >= 0.03 and r["distinct"] > 1.4 * r["reverse"]:
            out.append(r)
    if not out:
        return None
    # The plainest host wins: the one whose own texture the inlay stands out from most.
    return max(out, key=lambda r: r["distinct"] * r["share"])


def roots(names, tol=8):
    """Every sprite's host, followed to the rock it is ultimately drawn on. An ore whose best match is
    another ore shares that ore's matrix rather than sitting on it, so the chain is walked to the sprite
    nobody is an inlay of."""
    direct = {n: (best(n, names, tol) or {}).get("base") for n in names}
    out = {}
    for n in names:
        seen, cur = {n}, direct.get(n)
        while cur and direct.get(cur) and direct[cur] not in seen:
            seen.add(cur)
            cur = direct[cur]
        out[n] = cur
    return out
