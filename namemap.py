"""Studio palette row -> 1.8.9 texture name, for the blocks a terrain paint may use.

Hand-written because there is no id table in the jar and no texture name in the studio: the join is the
one thing neither side states. Every row is checked against the committed swatch by `compare.py`, so a
wrong pairing shows up as a colour that does not match rather than passing silently.
"""
# (id, data) -> the texture whose face a top-down render sees
MAP = {
    (1, 0): "stone", (1, 1): "stone_granite", (1, 2): "stone_granite_smooth",
    (1, 3): "stone_diorite", (1, 4): "stone_diorite_smooth",
    (1, 5): "stone_andesite", (1, 6): "stone_andesite_smooth",
    (2, 0): "grass_top", (3, 0): "dirt", (3, 1): "coarse_dirt", (3, 2): "dirt_podzol_top",
    (4, 0): "cobblestone", (5, 0): "planks_oak", (5, 1): "planks_spruce", (5, 2): "planks_birch",
    (5, 3): "planks_jungle", (5, 4): "planks_acacia", (5, 5): "planks_big_oak",
    (12, 0): "sand", (12, 1): "red_sand", (13, 0): "gravel",
    (15, 0): "iron_ore", (16, 0): "coal_ore", (19, 0): "sponge", (19, 1): "sponge_wet",
    (22, 0): "lapis_block", (24, 0): "sandstone_top", (24, 2): "sandstone_smooth",
    (35, 4): "wool_colored_yellow", (35, 5): "wool_colored_lime", (35, 7): "wool_colored_gray",
    (35, 8): "wool_colored_silver", (35, 11): "wool_colored_blue", (35, 12): "wool_colored_brown",
    (35, 13): "wool_colored_green", (35, 15): "wool_colored_black",
    (42, 0): "iron_block", (43, 0): "stone_slab_top", (43, 8): "stone_slab_top",
    (43, 9): "sandstone_top",
    (45, 0): "brick", (48, 0): "cobblestone_mossy", (49, 0): "obsidian",
    (79, 0): "ice", (80, 0): "snow", (82, 0): "clay", (88, 0): "soul_sand",
    (98, 0): "stonebrick", (98, 1): "stonebrick_mossy", (98, 2): "stonebrick_cracked",
    (98, 3): "stonebrick_carved",
    (99, 0): "mushroom_block_skin_brown", (99, 15): "mushroom_block_skin_stem",
    (103, 0): "melon_top", (110, 0): "mycelium_top", (112, 0): "nether_brick",
    (121, 0): "end_stone", (133, 0): "emerald_block", (155, 0): "quartz_block_top",
    (155, 1): "quartz_block_chiseled_top", (159, None): "hardened_clay_stained_",
    (165, 0): "slime", (168, 0): "prismarine_rough", (168, 1): "prismarine_bricks",
    (168, 2): "prismarine_dark", (170, 0): "hay_block_top", (172, 0): "hardened_clay",
    (173, 0): "coal_block", (174, 0): "ice_packed", (179, 0): "red_sandstone_top",
    (181, 8): "red_sandstone_top",
}

DYE = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
       "silver", "cyan", "purple", "blue", "brown", "green", "red", "black"]


def texture_for(bid, data):
    if bid == 159:                                   # stained clay, sixteen shades
        return f"hardened_clay_stained_{DYE[data]}"
    if bid == 35:                                    # wool, sixteen shades
        return f"wool_colored_{DYE[data]}"
    if bid == 95:
        return f"glass_{DYE[data]}"
    return MAP.get((bid, data))
