"""Which texture a paintable block shows on top and which on its sides.

A terrain theme paints in buckets: the surface bucket writes the block a player walks on and sees from
above, the wall bucket writes the block seen from the side. For most blocks those are one sprite. For the
ones below they are not, and the difference is the whole reason two blocks can be interchangeable in one
bucket and quite distinct in another.

Taken from the jar's own models (`model-faces.json`); a block not named here wears one sprite on all six
faces and its `namemap` texture is both answers.
"""
import namemap

# (id, data) -> (top, side); from the block models in the 1.8.9 jar.
MULTI = {
    (2, 0):   ("grass_top", "grass_side"),
    (3, 2):   ("dirt_podzol_top", "dirt_podzol_side"),
    (24, 0):  ("sandstone_top", "sandstone_normal"),
    (24, 2):  ("sandstone_top", "sandstone_smooth"),
    (43, 0):  ("stone_slab_top", "stone_slab_side"),
    (43, 8):  ("stone_slab_top", "stone_slab_side"),
    (43, 9):  ("sandstone_top", "sandstone_normal"),
    (99, 0):  ("mushroom_block_skin_brown", "mushroom_block_skin_brown"),
    (99, 15): ("mushroom_block_skin_stem", "mushroom_block_skin_stem"),
    (103, 0): ("melon_top", "melon_side"),
    (110, 0): ("mycelium_top", "mycelium_side"),
    (155, 0): ("quartz_block_top", "quartz_block_side"),
    (155, 1): ("quartz_block_chiseled_top", "quartz_block_chiseled"),
    (170, 0): ("hay_block_top", "hay_block_side"),
    (179, 0): ("red_sandstone_top", "red_sandstone_normal"),
    (181, 8): ("red_sandstone_top", "red_sandstone_normal"),
}


def faces(bid, data):
    if (bid, data) in MULTI:
        return MULTI[(bid, data)]
    t = namemap.texture_for(bid, data)
    return (t, t)
