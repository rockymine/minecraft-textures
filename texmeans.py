"""Per-texture statistics for the 1.8.9 block sprites.

`mean` is the alpha-masked mean of the sprite's opaque pixels — the figure `BlockPaletteData` states it
takes. An animated texture is a vertical strip of 16x16 frames and only its first frame is read, since
that is the frame a still render shows.
"""
import pathlib, functools
import numpy as np
from PIL import Image

BLOCKS = pathlib.Path(__file__).parent / "assets-1.8.9/assets/minecraft/textures/blocks"


@functools.lru_cache(maxsize=None)
def sprite(name):
    """One texture as (rgb float array HxWx3, alpha HxW), first frame only."""
    im = Image.open(BLOCKS / f"{name}.png").convert("RGBA")
    a = np.asarray(im, dtype=np.float64)
    if a.shape[0] > a.shape[1]:                      # animated strip
        a = a[: a.shape[1]]
    return a[:, :, :3], a[:, :, 3]


def mean_rgb(name):
    rgb, alpha = sprite(name)
    m = alpha > 0
    if not m.any():
        return None
    return tuple(rgb[:, :, i][m].mean() for i in range(3))


def all_means():
    out = {}
    for p in sorted(BLOCKS.glob("*.png")):
        try:
            v = mean_rgb(p.stem)
        except Exception:
            continue
        if v:
            out[p.stem] = v
    return out

