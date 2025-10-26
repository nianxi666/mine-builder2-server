// ====================================================================
// Constants and Data
// ====================================================================
const VOXEL_RESOLUTION = 32;
const GRID_SIZE = 10;
const VOXEL_SIZE = GRID_SIZE / VOXEL_RESOLUTION;
const DEFAULT_VOXEL_PROPERTIES = { blockId: 1, metaData: 0 };
const FLASH_MODEL_NAME = 'gemini-2.5-flash';
const PRO_MODEL_NAME = 'gemini-2.5-pro';
const AGENT_MAX_RETRIES_PER_PART = 2;
const DEFAULT_BLOCK_ID_LIST = { "1": { "0": "stone", "1": "granite", "2": "polished_granite", "3": "stone_diorite", "4": "polished_diorite", "5": "andersite", "6": "polished_andersite" }, "2": { "0": { "top": "dirt", "bottom": "dirt", "*": "dirt" } }, "3": { "0": "dirt", "1": "coarse_dirt", "2": "podzol" }, "4": { "0": "cobblestone" }, "5": { "0": "planks_oak", "1": "planks_spruce", "3": "planks_jungle", "4": "planks_acacia", "5": "planks_big_oak" }, "7": { "0": "cobblestone" }, "12": { "0": "sand", "1": "red_sand" }, "13": { "0": "gravel" }, "14": { "0": "gold_ore" }, "15": { "0": "iron_ore" }, "16": { "0": "coal_ore" }, "17": { "0": { "top": "log_oak_top", "bottom": "log_oak_top", "*": "log_oak" }, "1": { "top": "log_spruce_top", "bottom": "log_spruce_top", "*": "log_spruce" }, "2": { "top": "log_birch_top", "bottom": "log_birch_top", "*": "log_birch" }, "3": { "top": "log_jungle_top", "bottom": "log_jungle_top", "*": "log_jungle" }, "4": { "east": "log_oak_top:180", "west": "log_oak_top", "top": "log_oak:270", "bottom": "log_oak:270", "north": "log_oak:90", "south": "log_oak:270" }, "5": { "east": "log_spruce_top:180", "west": "log_spruce_top", "top": "log_spruce:270", "bottom": "log_spruce:270", "north": "log_spruce:90", "south": "log_spruce:270" }, "6": { "east": "log_birch_top:180", "west": "log_birch_top", "top": "log_birch:270", "bottom": "log_birch:270", "north": "log_birch:90", "south": "log_birch:270" }, "7": { "east": "log_jungle_top:180", "west": "log_jungle_top", "top": "log_jungle:270", "bottom": "log_jungle:270", "north": "log_jungle:90", "south": "log_jungle:270" }, "8": { "north": "log_oak_top:180", "south": "log_oak_top", "top": "log_oak", "bottom": "log_oak:180", "east": "log_oak:270", "west": "log_oak:90" }, "9": { "north": "log_spruce_top:180", "south": "log_spruce_top", "top": "log_spruce", "bottom": "log_spruce:180", "east": "log_spruce:270", "west": "log_spruce:90" }, "10": { "north": "log_birch_top:180", "south": "log_birch_top", "top": "log_birch", "bottom": "log_birch:180", "east": "log_birch:270", "west": "log_birch:90" }, "11": { "north": "log_jungle_top:180", "south": "log_jungle_top", "top": "log_jungle", "bottom": "log_jungle:180", "east": "log_jungle:270", "west": "log_jungle:90" }, "12": { "*": "log_oak" }, "13": { "*": "log_spruce" }, "14": { "*": "log_birch" }, "15": { "*": "log_jungle" } }, "19": { "0": "sponge", "1": "wet_sponge" }, "21": { "0": "lapis_ore" }, "22": { "0": "lapis_block" }, "23": { "0": { "bottom": "dispenser_front_vertical", "top": "furnace_top", "*": "furnace_side:180" }, "1": { "top": "dispenser_front_vertical", "bottom": "furnace_top", "*": "furnace_side" }, "2": { "north": "dispenser_front_horizontal:0", "south": "furnace_top:0", "top": "furnace_side:0", "east": "furnace_side:270", "bottom": "furnace_side:180", "west": "furnace_side:90" }, "3": { "south": "dispenser_front_horizontal:180", "north": "furnace_top:180", "top": "furnace_side:180", "east": "furnace_side:90", "bottom": "furnace_side:0", "west": "furnace_side:270" }, "4": { "east": "dispenser_front_horizontal:270", "west": "furnace_top:90", "top": "furnace_side:90", "bottom": "furnace_side:270", "north": "furnace_side:90", "south": "furnace_side:270" }, "5": { "west": "dispenser_front_horizontal:90", "east": "furnace_top:270", "top": "furnace_side:270", "bottom": "furnace_side:90", "north": "furnace_side:270", "south": "furnace_side:90" } }, "24": { "0": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_normal" }, "1": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_carved" }, "2": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_smooth" } }, "25": { "0": "noteblock" }, "29": { "0": { "bottom": "piston_top_normal", "top": "piston_bottom", "*": "piston_side:180" }, "1": { "top": "piston_top_normal", "bottom": "piston_bottom", "*": "piston_side" }, "2": { "north": "piston_top_normal:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "3": { "south": "piston_top_normal:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "4": { "east": "piston_top_normal:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "5": { "west": "piston_top_normal:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" }, "8": { "bottom": "piston_inner", "top": "piston_bottom", "*": "piston_side:180" }, "9": { "top": "piston_inner", "bottom": "piston_bottom", "*": "piston_side" }, "10": { "north": "piston_inner:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "11": { "south": "piston_inner:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "12": { "east": "piston_inner:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "13": { "west": "piston_inner:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" } }, "33": { "0": { "bottom": "piston_top_sticky", "top": "piston_bottom", "*": "piston_side:180" }, "1": { "top": "piston_top_sticky", "bottom": "piston_bottom", "*": "piston_side" }, "2": { "north": "piston_top_sticky:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "3": { "south": "piston_top_sticky:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "4": { "east": "piston_top_sticky:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "5": { "west": "piston_top_sticky:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" }, "8": { "bottom": "piston_inner", "top": "piston_bottom", "*": "piston_side:180" }, "9": { "top": "piston_inner", "bottom": "piston_bottom", "*": "piston_side" }, "10": { "north": "piston_inner:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "11": { "south": "piston_inner:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "12": { "east": "piston_inner:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "13": { "west": "piston_inner:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" } }, "35": { "0": "wool_colored_white", "1": "wool_colored_orange", "2": "wool_colored_magenta", "3": "wool_colored_light_blue", "4": "wool_colored_yellow", "5": "wool_colored_lime", "6": "wool_colored_pink", "7": "wool_colored_gray", "8": "wool_colored_silver", "9": "wool_colored_cyan", "10": "wool_colored_purple", "11": "wool_colored_blue", "12": "wool_colored_brown", "13": "wool_colored_green", "14": "wool_colored_red", "15": "wool_colored_black" }, "41": { "0": "gold_block" }, "42": { "0": "iron_block" }, "43": { "0": { "top": "stone_slab_top", "bottom": "stone_slab_top", "*": "stone_slab_side" }, "1": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_normal" }, "2": "planks_oak", "3": "cobblestone", "4": "brick", "5": "stonebrick", "6": "nether_brick", "7": "quartz_block_side" }, "45": { "0": "brick" }, "46": { "*": { "top": "tnt_top", "bottom": "tnt_bottom", "*": "tnt_side" } }, "47": { "0": { "top": "planks_oak", "bottom": "planks_oak", "*": "bookshelf" } }, "48": { "0": "cobblestone_mossy" }, "49": { "0": "obsidian" }, "56": { "0": "diamond_ore" }, "57": { "0": "diamond_block" }, "58": { "0": { "north": "crafting_table_side", "west": "crafting_table_side", "east": "crafting_table_front", "south": "crafting_table_front", "top": "crafting_table_top", "bottom": "planks_oak" } }, "60": { "0": "dirt" }, "61": { "2": { "top": "furnace_top", "bottom": "furnace_top", "north": "furnace_front_off", "*": "furnace_side" }, "3": { "top": "furnace_top", "bottom": "furnace_top", "south": "furnace_front_off", "*": "furnace_side" }, "4": { "top": "furnace_top", "bottom": "furnace_top", "west": "furnace_front_off", "*": "furnace_side" }, "5": { "top": "furnace_top", "bottom": "furnace_top", "east": "furnace_front_off", "*": "furnace_side" } }, "62": { "2": { "top": "furnace_top", "bottom": "furnace_top", "north": "furnace_front_on", "*": "furnace_side" }, "3": { "top": "furnace_top", "bottom": "furnace_top", "south": "furnace_front_on", "*": "furnace_side" }, "4": { "top": "furnace_top", "bottom": "furnace_top", "west": "furnace_front_on", "*": "furnace_side" }, "5": { "top": "furnace_top", "bottom": "furnace_top", "east": "furnace_front_on", "*": "furnace_side" } }, "73": { "0": "redstone_ore" }, "74": { "0": "redstone_ore" }, "78": { "0": "snow" }, "79": { "0": "ice" }, "80": { "0": "snow" }, "81": { "*": { "top": "cactus_top", "bottom": "cactus_bottom", "*": "cactus_side" } }, "82": { "0": "clay" }, "84": { "0": { "top": "jukebox_top", "*": "jukebox_side" }, "1": { "top": "jukebox_top", "*": "jukebox_side" } }, "86": { "0": { "top": "pumpkin_top", "bottom": "pumpkin_top", "south": "pumpkin_face_off", "*": "pumpkin_side" }, "1": { "top": "pumpkin_top", "bottom": "pumpkin_top", "west": "pumpkin_face_off", "*": "pumpkin_side" }, "2": { "top": "pumpkin_top", "bottom": "pumpkin_top", "north": "pumpkin_face_off", "*": "pumpkin_side" }, "3": { "top": "pumpkin_top", "bottom": "pumpkin_top", "east": "pumpkin_face_off", "*": "pumpkin_side" } }, "87": { "0": "netherrack" }, "88": { "0": "soul_sand" }, "89": { "0": "glowstone" }, "91": { "0": { "top": "pumpkin_top", "bottom": "pumpkin_top", "south": "pumpkin_face_on", "*": "pumpkin_side" }, "1": { "top": "pumpkin_top", "bottom": "pumpkin_top", "west": "pumpkin_face_on", "*": "pumpkin_side" }, "2": { "top": "pumpkin_top", "bottom": "pumpkin_top", "north": "pumpkin_face_on", "*": "pumpkin_side" }, "3": { "top": "pumpkin_top", "bottom": "pumpkin_top", "east": "pumpkin_face_on", "*": "pumpkin_side" } }, "95": { "0": "glass_white", "1": "glass_orange", "2": "glass_magenta", "3": "glass_light_blue", "4": "glass_yellow", "5": "glass_lime", "6": "glass_pink", "7": "glass_gray", "8": "glass_silver", "9": "glass_cyan", "10": "glass_purple", "11": "glass_blue", "12": "glass_brown", "13": "glass_green", "14": "glass_red", "15": "glass_black" }, "97": { "0": "stone", "1": "cobblestone", "2": "stonebrick", "3": "stonebrick_mossy", "4": "stonebrick_cracked", "5": "stonebrick_carved" }, "98": { "0": "stonebrick", "1": "stonebrick_mossy", "2": "stonebrick_cracked", "3": "stonebrick_carved" }, "99": { "0": "mushroom_block_skin_brown" }, "100": { "0": "mushroom_block_skin_red" }, "103": { "0": { "top": "melon_top", "bottom": "melon_bottom", "*": "melon_side" } }, "110": { "0": { "top": "mycelium_top", "bottom": "dirt", "*": "mycelium_side" } }, "112": { "0": "nether_brick" }, "120": { "0": { "top": "endframe_top", "bottom": "end_stone", "*": "endframe_side" } }, "123": { "0": "redstone_lamp_off" }, "124": { "0": "redstone_lamp_on" }, "125": { "0": "planks_oak", "1": "planks_spruce", "3": "planks_jungle", "4": "planks_acacia", "5": "planks_big_oak" }, "129": { "0": "emerald_ore" }, "133": { "0": "emerald_block" }, "152": { "0": "redstone_block" }, "153": { "0": "quartz_ore" }, "155": { "0": { "top": "quartz_block_top", "bottom": "quartz_block_bottom", "*": "quartz_block_side" }, "1": { "top": "quartz_block_chiseled_top", "bottom": "quartz_block_bottom", "*": "quartz_block_chiseled" }, "2": { "top": "quartz_block_lines_top", "bottom": "quartz_block_lines_top", "*": "quartz_block_lines" } }, "159": { "0": "hardened_clay_stained_white", "1": "hardened_clay_stained_orange", "2": "hardened_clay_stained_magenta", "3": "hardened_clay_stained_light_blue", "4": "hardened_clay_stained_yellow", "5": "hardened_clay_stained_lime", "6": "hardened_clay_stained_pink", "7": "hardened_clay_stained_gray", "8": "hardened_clay_stained_silver", "9": "hardened_clay_stained_cyan", "10": "hardened_clay_stained_purple", "11": "hardened_clay_stained_blue", "12": "hardened_clay_stained_brown", "13": "hardened_clay_stained_green", "14": "hardened_clay_stained_red", "15": "hardened_clay_stained_black" }, "160": { "0": "glass_white", "1": "glass_orange", "2": "glass_magenta", "3": "glass_light_blue", "4": "glass_yellow", "5": "glass_lime", "6": "glass_pink", "7": "glass_gray", "8": "glass_silver", "9": "glass_cyan", "10": "glass_purple", "11": "glass_blue", "12": "glass_brown", "13": "glass_green", "14": "glass_red", "15": "glass_black" }, "162": { "0": { "top": "log_acacia_top", "bottom": "log_acacia_top", "*": "log_acacia" }, "1": { "top": "log_big_oak_top", "bottom": "log_big_oak_top", "*": "log_big_oak" }, "4": { "east": "log_acacia_top:180", "west": "log_acacia_top", "top": "log_acacia:90", "bottom": "log_acacia:270", "north": "log_acacia:90", "south": "log_acacia:270" }, "5": { "east": "log_big_oak_top:180", "west": "log_big_oak_top", "top": "log_big_oak:90", "bottom": "log_big_oak:270", "north": "log_big_oak:90", "south": "log_big_oak:270" }, "8": { "north": "log_acacia_top:180", "south": "log_acacia_top", "top": "log_acacia", "bottom": "log_acacia:180", "east": "log_acacia:90", "west": "log_acacia:270" }, "9": { "north": "log_big_oak_top:180", "south": "log_big_oak_top", "top": "log_big_oak", "bottom": "log_big_oak:180", "east": "log_big_oak:90", "west": "log_big_oak:270" }, "12": { "*": "log_acacia" }, "13": { "*": "log_big_oak" } }, "168": { "0": "prismarine_rough", "1": "prismarine_bricks", "2": "prismarine_dark" }, "170": { "0": { "top": "hay_block_top", "bottom": "hay_block_top", "*": "hay_block_side" } }, "172": { "0": "hardened_clay" }, "173": { "0": "coal_block" }, "174": { "0": "ice_packed" }, "179": { "0": { "top": "red_sandstone_top", "bottom": "red_sandstone_bottom", "*": "red_sandstone_normal" }, "1": { "top": "red_sandstone_top", "bottom": "red_sandstone_bottom", "*": "red_sandstone_carved" }, "2": { "top": "red_sandstone_top", "bottom": "red_sandstone_bottom", "*": "red_sandstone_smooth" } }, "198": { "0": "end_rod" }, "201": { "0": "purpur_block" }, "202": { "0": { "top": "purpur_pillar_top", "bottom": "purpur_pillar_top", "*": "purpur_pillar" } }, "203": { "0": "purpur_block" }, "206": { "0": "end_bricks" }, "207": { "0": "beetroots_stage_3" }, "208": { "0": { "top": "grass_path_top", "bottom": "dirt", "*": "grass_path_side" } }, "209": { "0": "repeating_command_block" }, "210": { "0": "chain_command_block" }, "211": { "0": "command_block" }, "213": { "is_animated": "true", "0": "magma" }, "214": { "0": "nether_wart_block" }, "215": { "0": "red_nether_brick" }, "216": { "0": "bone_block" }, "218": { "0": { "bottom": "observer_front", "top": "observer_back", "north": "observer_top:180", "south": "observer_top:180", "east": "observer_side:180", "west": "observer_side:180" }, "1": { "top": "observer_front", "bottom": "observer_back", "north": "observer_top", "south": "observer_top", "east": "observer_side", "west": "observer_side" }, "2": { "north": "observer_front:180", "south": "observer_back:180", "top": "observer_top:0", "east": "observer_side:270", "bottom": "observer_top:180", "west": "observer_side:90" }, "3": { "south": "observer_front:0", "north": "observer_back:0", "top": "observer_top:180", "east": "observer_side:90", "bottom": "observer_top:0", "west": "observer_side:270" }, "4": { "east": "observer_front:90", "west": "observer_back:270", "top": "observer_top:90", "bottom": "observer_top:270", "north": "observer_side:90", "south": "observer_side:270" }, "5": { "west": "observer_front:270", "east": "observer_back:90", "top": "observer_top:270", "bottom": "observer_top:90", "north": "observer_side:270", "south": "observer_side:90" }, "8": { "bottom": "observer_front", "top": "observer_back_lit", "north": "observer_top:180", "south": "observer_top:180", "east": "observer_side:180", "west": "observer_side:180" }, "9": { "top": "observer_front", "bottom": "observer_back_lit", "north": "observer_top", "south": "observer_top", "east": "observer_side", "west": "observer_side" }, "10": { "north": "observer_front:180", "south": "observer_back_lit:180", "top": "observer_top:0", "east": "observer_side:270", "bottom": "observer_top:180", "west": "observer_side:90" }, "11": { "south": "observer_front:0", "north": "observer_back_lit:0", "top": "observer_top:180", "east": "observer_side:90", "bottom": "observer_top:0", "west": "observer_side:270" }, "12": { "east": "observer_front:90", "west": "observer_back_lit:270", "top": "observer_top:90", "bottom": "observer_top:270", "north": "observer_side:90", "south": "observer_side:270" }, "13": { "west": "observer_front:270", "east": "observer_back_lit:90", "top": "observer_top:270", "bottom": "observer_top:90", "north": "observer_side:270", "south": "observer_side:90" } }, "219": { "0": "shulker_box_white" }, "220": { "0": "shulker_box_orange" }, "221": { "0": "shulker_box_magenta" }, "222": { "0": "shulker_box_light_blue" }, "223": { "0": "shulker_box_yellow" }, "224": { "0": "shulker_box_lime" }, "225": { "0": "shulker_box_pink" }, "226": { "0": "shulker_box_gray" }, "227": { "0": "shulker_box_silver" }, "228": { "0": "shulker_box_cyan" }, "229": { "0": "shulker_box_purple" }, "230": { "0": "shulker_box_blue" }, "231": { "0": "shulker_box_brown" }, "232": { "0": "shulker_box_green" }, "233": { "0": "shulker_box_red" }, "234": { "0": "shulker_box_black" }, "235": { "0": "shulker_box" }, "251": { "0": "concrete_white", "1": "concrete_orange", "2": "concrete_magenta", "3": "concrete_light_blue", "4": "concrete_yellow", "5": "concrete_lime", "6": "concrete_pink", "7": "concrete_gray", "8": "concrete_silver", "9": "concrete_cyan", "10": "concrete_purple", "11": "concrete_blue", "12": "concrete_brown", "13": "concrete_green", "14": "concrete_red", "15": "concrete_black" }, "252": { "0": "concrete_powder_white", "1": "concrete_powder_orange", "2": "concrete_powder_magenta", "3": "concrete_powder_light_blue", "4": "concrete_powder_yellow", "5": "concrete_powder_lime", "6": "concrete_powder_pink", "7": "concrete_powder_gray", "8": "concrete_powder_silver", "9": "concrete_powder_cyan", "10": "concrete_powder_purple", "11": "concrete_powder_blue", "12": "concrete_powder_brown", "13": "concrete_powder_green", "14": "concrete_powder_red", "15": "concrete_powder_black" } };
const TEXTURE_KEY_TO_COLOR_MAP = { 'stone': 0x888888, 'grass_top': 0x74b44a, 'grass_side': 0x90ac50, 'dirt': 0x8d6b4a, 'cobblestone': 0x7a7a7a, 'planks_oak': 0xaf8f58, 'planks_spruce': 0x806038, 'planks_birch': 0xdace9b, 'planks_jungle': 0xac7d5a, 'planks_acacia': 0xad6c49, 'planks_dark_oak': 0x4c331e, 'bedrock': 0x555555, 'sand': 0xe3dbac, 'gravel': 0x84807b, 'log_oak': 0x685133, 'log_oak_top': 0x9e8054, 'log_spruce': 0x513f27, 'log_spruce_top': 0x716041, 'log_birch': 0xd0cbb0, 'log_birch_top': 0xe0d6b5, 'log_jungle': 0x584c24, 'log_jungle_top': 0x84733c, 'log_acacia': 0x645c50, 'log_acacia_top': 0x918877, 'log_dark_oak': 0x3c2d1b, 'log_big_oak_top': 0x5f4931, 'leaves_oak': 0x44aa44, 'leaves_spruce': 0x4c784c, 'leaves_birch': 0x6aac6a, 'leaves_jungle': 0x48a048, 'leaves_acacia': 0x4c8c4c, 'leaves_dark_oak': 0x4c784c, 'glass': 0xeeeeff, 'glass_pane_top': 0xddddf0, 'brick': 0xa05050, 'obsidian': 0x1c1824, 'diamond_block': 0x7dedde, 'netherrack': 0x883333, 'glowstone': 0xfff055, 'unknown': 0xff00ff };

// ====================================================================
// Global State
// ====================================================================
let scene, camera, renderer, controls, raycaster;
let voxelContainerGroup, selectionHighlightMesh;
let loadedModel = null;
let referenceImage = null;
let modelParts = [];
let currentVoxelCoords = new Set();
let voxelProperties = new Map();
let selectedVoxelCoords = new Set();
let selectedPartId = null;
let selectedMaterial = null;
let loadedTextures = new Map();
let geminiApiKey = '';
let currentAiModel = FLASH_MODEL_NAME;
const textureLoader = new THREE.TextureLoader();
const mouseNdc = new THREE.Vector2();
let isolateTimer = null;
let allMaterialsCache = null;

// --- Agent State ---
let isAgentRunning = false;
let isAgentPaused = false;
let agentAbortController = null;
let agentCurrentPartIndex = 0;
let agentOverallAnalysis = "";
let isAnimationPlaying = false;

// ====================================================================
// NEW: Automated Loading and Data Processing
// ====================================================================

/**
 * 页面加载时调用，从后端API获取并加载初始文件。
 */
async function loadInitialFilesFromServer(skipModel = false) {
    console.log(`Attempting to load initial files... (skipModel: ${skipModel})`);
    try {
        const response = await fetch('/api/files');
        if (!response.ok) throw new Error(`Server responded with ${response.status}`);
        const files = await response.json();
        console.log("Received file data:", files);

        // 总是尝试加载材质包和参考图
        if (files.texture && files.texture.data) {
            addAiChatMessage('system', `正在自动加载材质包: ${files.texture.name}`);
            const data = await fetch(`data:${files.texture.mimeType};base64,${files.texture.data}`).then(res => res.arrayBuffer());
            await processTexturePackData(data);
        } else {
            addAiChatMessage('system', `未找到 .zip 材质包，请手动加载。`);
        }

        if (files.reference && files.reference.data) {
            addAiChatMessage('system', `正在自动加载参考图: ${files.reference.name}`);
            const dataUrl = `data:${files.reference.mimeType};base64,${files.reference.data}`;
            processReferenceImageData(dataUrl);
        } else {
            addAiChatMessage('system', `未找到参考图，请手动上传。`);
        }

        // 仅在需要时加载模型
        if (!skipModel) {
            if (files.model && files.model.data) {
                addAiChatMessage('system', `正在自动加载模型: ${files.model.name}`);
                const data = await fetch(`data:${files.model.mimeType};base64,${files.model.data}`).then(res => res.arrayBuffer());
                processModelData(data);
            } else {
                addAiChatMessage('system', `未在 'input' 文件夹找到模型，请手动加载。`);
            }
        }
    } catch (error) {
        console.error("Failed to load initial files:", error);
        addAiChatMessage('system', `自动加载文件失败: ${error.message}`);
    }
}

/**
 * 核心逻辑：处理GLB/GLTF模型数据 (ArrayBuffer)
 */
function processModelData(arrayBuffer) {
    const loader = new THREE.GLTFLoader();
    loader.parse(arrayBuffer, '', (gltf) => {
        currentVoxelCoords.clear();
        voxelProperties.clear();
        loadedModel = gltf.scene;
        const parts = [];
        let partIndex = 1;
        gltf.scene.traverse((child) => {
            if (child instanceof THREE.Mesh && child.geometry && child.geometry.attributes.position) {
                parts.push({
                    uuid: child.uuid,
                    name: child.name || `部件 ${partIndex++}`,
                    visible: true,
                });
            }
        });
        modelParts = parts;
        voxelizeAndDisplay(gltf.scene);
        updateSceneInspector();
        updateAgentButtonState();
        addAiChatMessage('system', `模型已成功加载。它包含以下部件: ${modelParts.map(p => `"${p.name}"`).join(', ')}.`);
    }, (error) => {
        console.error('解析GLTF模型时出错:', error);
        alert('加载GLTF模型失败。');
        addAiChatMessage('system', `加载GLTF模型失败: ${error}`);
    });
}

/**
 * 核心逻辑：处理材质包数据 (ArrayBuffer)
 */
async function processTexturePackData(arrayBuffer) {
    if (typeof JSZip === 'undefined') return;
    try {
        const zip = await JSZip.loadAsync(arrayBuffer);
        const newTextures = new Map();
        const texturePromises = [];
        const texturePathPrefix = 'assets/minecraft/textures/blocks/';
        loadedTextures.forEach(texture => texture.dispose());
        zip.forEach((relativePath, zipEntry) => {
            if (relativePath.startsWith(texturePathPrefix) && relativePath.toLowerCase().endsWith('.png') && !zipEntry.dir) {
                const textureName = relativePath.substring(texturePathPrefix.length).replace(/\\.png$/i, '');
                if (textureName) {
                    texturePromises.push(
                        zipEntry.async('blob').then(blob => {
                            const url = URL.createObjectURL(blob);
                            return new Promise((resolve) => {
                                textureLoader.load(url, (texture) => {
                                    texture.magFilter = THREE.NearestFilter;
                                    texture.minFilter = THREE.NearestFilter;
                                    newTextures.set(textureName, texture);
                                    URL.revokeObjectURL(url);
                                    resolve();
                                }, undefined, (err) => { console.error(err); resolve(); });
                            });
                        })
                    );
                }
            }
        });
        await Promise.all(texturePromises);
        loadedTextures = newTextures;
        allMaterialsCache = null;
        populateMaterialInventory();
        updateAgentButtonState();
        if (currentVoxelCoords.size > 0) displayVoxels();
        addAiChatMessage('system', '材质包已成功加载。');
    } catch (error) {
        console.error('加载材质包时出错:', error);
        alert('加载材质包失败。');
        addAiChatMessage('system', `加载材质包失败: ${error}`);
    }
}

/**
 * 核心逻辑：处理参考图数据 (DataURL)
 */
function processReferenceImageData(dataUrl) {
    referenceImage = dataUrl;
    addAiChatMessage('system', '参考图已成功加载。', [{src: referenceImage, label: '参考图'}]);
    updateAgentButtonState();
}


// ====================================================================
// Utility Functions
// ====================================================================
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function getTextureKeyForVoxel(blockId, metaData, blockDefs) {
    const blockEntry = blockDefs[blockId.toString()];
    if (!blockEntry) return 'unknown';
    const metaEntry = blockEntry[metaData.toString()];
    if (!metaEntry) return 'unknown';
    if (typeof metaEntry === 'string') return metaEntry.split(':')[0];
    if (typeof metaEntry === 'object' && metaEntry !== null) {
        const key = metaEntry['*'] || metaEntry.top || metaEntry.side || 'unknown';
        return key.split(':')[0];
    }
    return 'unknown';
}

function getAllMinecraftMaterials() {
     if (allMaterialsCache) return allMaterialsCache;

    const materials = new Set();
    const uniqueMaterials = [];
    for (const blockIdStr in DEFAULT_BLOCK_ID_LIST) {
        const blockId = parseInt(blockIdStr, 10);
        const blockEntry = DEFAULT_BLOCK_ID_LIST[blockIdStr];
        for (const metaDataStr in blockEntry) {
            if (isNaN(parseInt(metaDataStr))) continue;
            const metaData = parseInt(metaDataStr, 10);
            const metaEntry = blockEntry[metaDataStr];
            let name = '';
            let textureKey = '';
            if (typeof metaEntry === 'string') {
                textureKey = metaEntry;
            } else if (typeof metaEntry === 'object' && metaEntry !== null) {
                textureKey = metaEntry['*'] || metaEntry.top || metaEntry.side || 'unknown';
            }
            if (textureKey) {
                textureKey = textureKey.split(':')[0]; // Remove rotation info
                name = textureKey.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                if (!materials.has(name)) {
                    materials.add(name);
                    const isAvailable = loadedTextures.has(textureKey);
                    uniqueMaterials.push({ name, id: blockId, meta: metaData, textureKey, isAvailable });
                }
            }
        }
    }
    allMaterialsCache = uniqueMaterials;
    return uniqueMaterials;
}

// ====================================================================
// Core 3D and Voxelization Logic
// ====================================================================

function init() {
    const mount = document.getElementById('mount');
    if (!mount) return;
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1f2937);
    camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 1000);
    camera.position.set(GRID_SIZE * 0.8, GRID_SIZE * 0.8, GRID_SIZE * 0.8);
    renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    // --- Enable Shadows ---
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mount.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0, GRID_SIZE / 2, 0);
    controls.update();

    scene.add(new THREE.AmbientLight(0xffffff, 0.8)); // Reduce ambient light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
    directionalLight.position.set(GRID_SIZE, GRID_SIZE * 1.5, GRID_SIZE * 0.5);
    // --- Enable Shadows on Light ---
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    const d = GRID_SIZE * 1.5;
    directionalLight.shadow.camera.left = -d;
    directionalLight.shadow.camera.right = d;
    directionalLight.shadow.camera.top = d;
    directionalLight.shadow.camera.bottom = -d;
    directionalLight.shadow.camera.far = GRID_SIZE * 5;
    directionalLight.shadow.bias = -0.0001;
    scene.add(directionalLight);

    const gridHelper = new THREE.GridHelper(GRID_SIZE, VOXEL_RESOLUTION, 0x555555, 0x333333);
    scene.add(gridHelper);

    // --- Add Ground Plane to Receive Shadows ---
    const groundPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(GRID_SIZE * 2, GRID_SIZE * 2),
        new THREE.ShadowMaterial({ opacity: 0.3 })
    );
    groundPlane.rotation.x = -Math.PI / 2;
    groundPlane.position.y = -0.01;
    groundPlane.receiveShadow = true;
    scene.add(groundPlane);

    voxelContainerGroup = new THREE.Group();
    scene.add(voxelContainerGroup);

    const highlightGeometry = new THREE.BoxGeometry(VOXEL_SIZE, VOXEL_SIZE, VOXEL_SIZE);
    const highlightMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.4, side: THREE.DoubleSide });
    selectionHighlightMesh = new THREE.InstancedMesh(highlightGeometry, highlightMaterial, VOXEL_RESOLUTION ** 3);
    selectionHighlightMesh.count = 0;
    scene.add(selectionHighlightMesh);
    raycaster = new THREE.Raycaster();
    window.addEventListener('resize', onWindowResize);
    mount.addEventListener('click', onCanvasClick);
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    const mount = document.getElementById('mount');
    if (!mount) return;
    const width = mount.clientWidth;
    const height = mount.clientHeight;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
}

function displayVoxels() {
    if (!voxelContainerGroup) return;
    while (voxelContainerGroup.children.length > 0) {
        const child = voxelContainerGroup.children[0];
        voxelContainerGroup.remove(child);
        child.geometry.dispose();
        if (Array.isArray(child.material)) child.material.forEach(m => m.dispose());
        else child.material.dispose();
    }
    const exportBtn = document.getElementById('export-txt-btn');
    const animationBtn = document.getElementById('play-animation-btn');
    const animationSlider = document.getElementById('animation-speed-slider');

    const hasVoxels = currentVoxelCoords.size > 0;
    if(exportBtn) exportBtn.disabled = !hasVoxels;
    if(animationBtn) animationBtn.disabled = !hasVoxels;
    if(animationSlider) animationSlider.disabled = !hasVoxels;

    if (!hasVoxels) {
        updateSelectionUI();
        return;
    }

    const materialToInstancesMap = new Map();
    currentVoxelCoords.forEach(coordString => {
        const voxelProps = voxelProperties.get(coordString) || DEFAULT_VOXEL_PROPERTIES;
        const textureKey = getTextureKeyForVoxel(voxelProps.blockId, voxelProps.metaData, DEFAULT_BLOCK_ID_LIST);
        if (!materialToInstancesMap.has(textureKey)) materialToInstancesMap.set(textureKey, []);
        const [x, y, z] = coordString.split(',').map(Number);
        const halfGrid = GRID_SIZE / 2;
        const posX = -halfGrid + (x + 0.5) * VOXEL_SIZE;
        const posY = (y + 0.5) * VOXEL_SIZE;
        const posZ = -halfGrid + (z + 0.5) * VOXEL_SIZE;
        const matrix = new THREE.Matrix4().setPosition(posX, posY, posZ);
        materialToInstancesMap.get(textureKey).push({ matrix, coord: coordString });
    });
    const baseVoxelGeometry = new THREE.BoxGeometry(VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98);
    materialToInstancesMap.forEach((instances, textureKey) => {
        if (instances.length === 0) return;
        let material;
        const texture = loadedTextures.get(textureKey);
        if (texture) {
            material = new THREE.MeshStandardMaterial({ map: texture, metalness: 0.1, roughness: 0.8 });
        } else {
            const color = TEXTURE_KEY_TO_COLOR_MAP[textureKey] || TEXTURE_KEY_TO_COLOR_MAP['unknown'];
            material = new THREE.MeshLambertMaterial({ color });
        }
        const instancedMesh = new THREE.InstancedMesh(baseVoxelGeometry, material, instances.length);
        instancedMesh.castShadow = true;
        instancedMesh.receiveShadow = true;
        const coordMapForMesh = [];
        instances.forEach((instanceData, i) => {
            instancedMesh.setMatrixAt(i, instanceData.matrix);
            coordMapForMesh[i] = instanceData.coord;
        });
        instancedMesh.instanceMatrix.needsUpdate = true;
        instancedMesh.userData = { coordMap: coordMapForMesh };
        voxelContainerGroup.add(instancedMesh);
    });
    const newSelectedCoords = new Set();
    selectedVoxelCoords.forEach(coord => {
        if (currentVoxelCoords.has(coord)) newSelectedCoords.add(coord);
    });
    selectedVoxelCoords = newSelectedCoords;
    if (selectedVoxelCoords.size === 0) selectedPartId = null;
    updateSelectionHighlight();
    updateSelectionUI();
}

function voxelizeAndDisplay(model) {
    selectedVoxelCoords.clear();
    selectedPartId = null;
    const newVoxelCoords = new Set();
    const newVoxelProps = new Map();
    const worldToVoxelIndex = (worldPos, outVector) => {
        const halfGrid = GRID_SIZE / 2;
        const idx = Math.floor(((worldPos.x + halfGrid) / GRID_SIZE) * VOXEL_RESOLUTION);
        const idy = Math.floor((worldPos.y / GRID_SIZE) * VOXEL_RESOLUTION);
        const idz = Math.floor(((worldPos.z + halfGrid) / GRID_SIZE) * VOXEL_RESOLUTION);
        return outVector.set(idx, idy, idz);
    };
    const voxelizeTriangle = (vA, vB, vC, partId) => {
        const triBox = new THREE.Box3().setFromPoints([vA, vB, vC]);
        const minVoxelIndex = worldToVoxelIndex(triBox.min, new THREE.Vector3());
        const maxVoxelIndex = worldToVoxelIndex(triBox.max, new THREE.Vector3());
        minVoxelIndex.clampScalar(0, VOXEL_RESOLUTION - 1);
        maxVoxelIndex.clampScalar(0, VOXEL_RESOLUTION - 1);
        for (let x = minVoxelIndex.x; x <= maxVoxelIndex.x; x++) {
            for (let y = minVoxelIndex.y; y <= maxVoxelIndex.y; y++) {
                for (let z = minVoxelIndex.z; z <= maxVoxelIndex.z; z++) {
                    const coordString = `${x},${y},${z}`;
                    newVoxelCoords.add(coordString);
                    if (!newVoxelProps.has(coordString)) {
                        newVoxelProps.set(coordString, { ...DEFAULT_VOXEL_PROPERTIES, partId });
                    }
                }
            }
        }
    };
    const tempMatrix = new THREE.Matrix4();
    const tempVectorA = new THREE.Vector3();
    const tempVectorB = new THREE.Vector3();
    const tempVectorC = new THREE.Vector3();
    const modelBoundingBox = new THREE.Box3();
    model.updateMatrixWorld(true);
    modelBoundingBox.setFromObject(model, true);
    if (modelBoundingBox.isEmpty()) {
        currentVoxelCoords = newVoxelCoords;
        voxelProperties = newVoxelProps;
        displayVoxels();
        return;
    }
    const modelSize = modelBoundingBox.getSize(new THREE.Vector3());
    const modelCenter = modelBoundingBox.getCenter(new THREE.Vector3());
    const maxDim = Math.max(modelSize.x, modelSize.y, modelSize.z);
    const scaleFactor = maxDim > 0 ? GRID_SIZE / maxDim : 1;
    const translationMatrix = new THREE.Matrix4().makeTranslation(-modelCenter.x, -modelBoundingBox.min.y, -modelCenter.z);
    const scaleMatrix = new THREE.Matrix4().makeScale(scaleFactor, scaleFactor, scaleFactor);
    const finalTransform = new THREE.Matrix4().multiply(scaleMatrix).multiply(translationMatrix);
    model.traverse((child) => {
        if (child instanceof THREE.Mesh && child.visible && child.geometry.isBufferGeometry) {
            const geometry = child.geometry;
            const positionAttribute = geometry.attributes.position;
            const indexAttribute = geometry.index;
            const partId = child.uuid;
            tempMatrix.multiplyMatrices(finalTransform, child.matrixWorld);
            if (positionAttribute) {
                if (indexAttribute) {
                    for (let i = 0; i < indexAttribute.count; i += 3) {
                        const a = indexAttribute.getX(i);
                        const b = indexAttribute.getX(i + 1);
                        const c = indexAttribute.getX(i + 2);
                        tempVectorA.fromBufferAttribute(positionAttribute, a).applyMatrix4(tempMatrix);
                        tempVectorB.fromBufferAttribute(positionAttribute, b).applyMatrix4(tempMatrix);
                        tempVectorC.fromBufferAttribute(positionAttribute, c).applyMatrix4(tempMatrix);
                        voxelizeTriangle(tempVectorA, tempVectorB, tempVectorC, partId);
                    }
                } else {
                    for (let i = 0; i < positionAttribute.count; i += 3) {
                        tempVectorA.fromBufferAttribute(positionAttribute, i).applyMatrix4(tempMatrix);
                        tempVectorB.fromBufferAttribute(positionAttribute, i + 1).applyMatrix4(tempMatrix);
                        tempVectorC.fromBufferAttribute(positionAttribute, i + 2).applyMatrix4(tempMatrix);
                        voxelizeTriangle(tempVectorA, tempVectorB, tempVectorC, partId);
                    }
                }
            }
        }
    });
    currentVoxelCoords = newVoxelCoords;
    voxelProperties = newVoxelProps;
    saveAppStateToLocalStorage(); // 保存状态

    if (modelParts.length > 0) {
        const partInfo = new Map();
        modelParts.forEach(p => {
            partInfo.set(p.uuid, { name: p.name, count: 0, isOccluded: true, voxels: [] });
        });

        for (const [coord, props] of voxelProperties.entries()) {
            if (partInfo.has(props.partId)) {
                const info = partInfo.get(props.partId);
                info.count++;
                info.voxels.push(coord.split(',').map(Number));
            }
        }

        const isVoxelVisible = (x, y, z) => {
            return !currentVoxelCoords.has(`${x+1},${y},${z}`) || !currentVoxelCoords.has(`${x-1},${y},${z}`) ||
                   !currentVoxelCoords.has(`${x},${y+1},${z}`) || !currentVoxelCoords.has(`${x},${y-1},${z}`) ||
                   !currentVoxelCoords.has(`${x},${y},${z+1}`) || !currentVoxelCoords.has(`${x},${y},${z-1}`);
        };

        for (const info of partInfo.values()) {
            let isAnyVoxelVisible = false;
            for (const [x, y, z] of info.voxels) {
                if (isVoxelVisible(x, y, z)) {
                    isAnyVoxelVisible = true;
                    break;
                }
            }
            info.isOccluded = !isAnyVoxelVisible;
        }

        modelParts.forEach(p => {
            const info = partInfo.get(p.uuid);
            p.voxelCount = info ? info.count : 0;
            p.isOccluded = info ? info.isOccluded : false;
        });

        modelParts.sort((a, b) => (b.voxelCount || 0) - (a.voxelCount || 0));
    }
    displayVoxels();
}

function playFallingAnimation() {
    if (isAnimationPlaying || currentVoxelCoords.size === 0) return;

    isAnimationPlaying = true;
    document.getElementById('play-animation-btn').disabled = true;

    const animationSpeed = parseFloat(document.getElementById('animation-speed-slider').value) || 1.0;
    const voxels = [];
    const halfGrid = GRID_SIZE / 2;

    // 1. 收集并排序所有体素
    currentVoxelCoords.forEach(coordString => {
        const [x, y, z] = coordString.split(',').map(Number);
        const voxelProps = voxelProperties.get(coordString) || DEFAULT_VOXEL_PROPERTIES;
        const targetPosition = new THREE.Vector3(
            -halfGrid + (x + 0.5) * VOXEL_SIZE,
            (y + 0.5) * VOXEL_SIZE,
            -halfGrid + (z + 0.5) * VOXEL_SIZE
        );
        voxels.push({ coordString, voxelProps, targetPosition });
    });

    // 从下到上排序，这样底部的方块先掉落
    voxels.sort((a, b) => a.targetPosition.y - b.targetPosition.y);

    // 2. 隐藏原始模型
    voxelContainerGroup.visible = false;

    // 3. 为动画创建专用的体素
    const animationGroup = new THREE.Group();
    scene.add(animationGroup);
    const baseVoxelGeometry = new THREE.BoxGeometry(VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98);
    const materialCache = new Map();

    voxels.forEach(voxel => {
        const textureKey = getTextureKeyForVoxel(voxel.voxelProps.blockId, voxel.voxelProps.metaData, DEFAULT_BLOCK_ID_LIST);
        let material;
        if (materialCache.has(textureKey)) {
            material = materialCache.get(textureKey);
        } else {
            const texture = loadedTextures.get(textureKey);
            if (texture) {
                material = new THREE.MeshStandardMaterial({ map: texture, metalness: 0.1, roughness: 0.8 });
            } else {
                const color = TEXTURE_KEY_TO_COLOR_MAP[textureKey] || TEXTURE_KEY_TO_COLOR_MAP['unknown'];
                material = new THREE.MeshLambertMaterial({ color });
            }
            materialCache.set(textureKey, material);
        }

        const mesh = new THREE.Mesh(baseVoxelGeometry, material);
        mesh.castShadow = true;
        // 将方块放置在场景上方的一个随机起始位置
        mesh.position.copy(voxel.targetPosition);
        mesh.position.y += GRID_SIZE * 1.5; // 从上方掉落
        mesh.position.x += (Math.random() - 0.5) * GRID_SIZE * 0.5;
        mesh.position.z += (Math.random() - 0.5) * GRID_SIZE * 0.5;

        voxel.mesh = mesh;
        voxel.startTime = -1; // 动画开始时间
        animationGroup.add(mesh);
    });

    // 4. 动画循环
    let startTime = null;
    const fallDuration = 1000 / animationSpeed;
    const staggerDelay = 50 / animationSpeed;

    function animationLoop(timestamp) {
        if (startTime === null) startTime = timestamp;
        const elapsedTime = timestamp - startTime;

        let allFinished = true;
        voxels.forEach((voxel, index) => {
            if (voxel.startTime < 0) {
                // 如果到了这个方块的开始时间
                if (elapsedTime > index * staggerDelay) {
                    voxel.startTime = timestamp;
                } else {
                     allFinished = false; // 还有方块没开始掉落
                }
            }

            if (voxel.startTime >= 0) {
                const voxelElapsedTime = timestamp - voxel.startTime;
                const progress = Math.min(voxelElapsedTime / fallDuration, 1);

                // 使用 easeOutBounce 缓动函数
                const t = progress;
                const c = 1.0;
                let newY;
                if (t < (1 / 2.75)) {
                    newY = c * (7.5625 * t * t);
                } else if (t < (2 / 2.75)) {
                    newY = c * (7.5625 * (t -= (1.5 / 2.75)) * t + 0.75);
                } else if (t < (2.5 / 2.75)) {
                    newY = c * (7.5625 * (t -= (2.25 / 2.75)) * t + 0.9375);
                } else {
                    newY = c * (7.5625 * (t -= (2.625 / 2.75)) * t + 0.984375);
                }

                const startY = voxel.targetPosition.y + GRID_SIZE * 1.5;
                const endY = voxel.targetPosition.y;
                voxel.mesh.position.y = startY - (startY - endY) * newY;

                // 简单的水平移动插值
                const startX = voxel.mesh.userData.startX || voxel.mesh.position.x;
                const startZ = voxel.mesh.userData.startZ || voxel.mesh.position.z;
                if (!voxel.mesh.userData.startX) {
                    voxel.mesh.userData.startX = startX;
                    voxel.mesh.userData.startZ = startZ;
                }
                voxel.mesh.position.x = THREE.MathUtils.lerp(startX, voxel.targetPosition.x, progress);
                voxel.mesh.position.z = THREE.MathUtils.lerp(startZ, voxel.targetPosition.z, progress);


                if (progress < 1) {
                    allFinished = false;
                } else {
                    voxel.mesh.position.copy(voxel.targetPosition); // 确保最终位置精确
                }
            }
        });

        if (allFinished) {
            // 5. 清理
            scene.remove(animationGroup);
            baseVoxelGeometry.dispose();
            materialCache.forEach(material => material.dispose());
            voxelContainerGroup.visible = true;
            isAnimationPlaying = false;
             // 重新启用按钮，但要检查模型是否存在
            document.getElementById('play-animation-btn').disabled = currentVoxelCoords.size === 0;
            console.log("Animation finished.");
        } else {
            requestAnimationFrame(animationLoop);
        }
    }

    requestAnimationFrame(animationLoop);
}


// ====================================================================
// UI Interaction Handlers
// ====================================================================

// 改为调用核心处理函数
function handleModelLoad(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        if (e.target?.result) {
            addAiChatMessage('system', `正在从文件输入加载模型: ${file.name}`);
            processModelData(e.target.result);
        }
    };
    reader.readAsArrayBuffer(file);
    event.target.value = '';
}

// 改为调用核心处理函数
function handleReferenceImageLoad(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        if (e.target?.result) {
            addAiChatMessage('system', `正在从文件输入加载参考图: ${file.name}`);
            processReferenceImageData(e.target.result);
        }
    };
    reader.readAsDataURL(file);
    event.target.value = '';
}

// 改为调用核心处理函数
async function handleTexturePackLoad(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (e) => {
        if (e.target?.result) {
            addAiChatMessage('system', `正在从文件输入加载材质包: ${file.name}`);
            await processTexturePackData(e.target.result);
        }
    };
    reader.readAsArrayBuffer(file);
    event.target.value = '';
}


function setCameraView(view) {
    if (!camera || !controls) return;
    const distance = GRID_SIZE * 1.5;
    const center = new THREE.Vector3(0, GRID_SIZE / 2, 0);
    switch (view) {
        case 'front': camera.position.set(0, GRID_SIZE / 2, distance); break;
        case 'back': camera.position.set(0, GRID_SIZE / 2, -distance); break;
        case 'left': camera.position.set(-distance, GRID_SIZE / 2, 0); break;
        case 'right': camera.position.set(distance, GRID_SIZE / 2, 0); break;
        case 'top': camera.position.set(0, distance + GRID_SIZE / 2, 0); break;
        case 'bottom': camera.position.set(0, -distance + GRID_SIZE / 2, 0); break;
    }
    camera.lookAt(center);
    controls.target.copy(center);
    controls.update();
}

function handleScreenshot() {
    if (renderer?.domElement) {
        renderer.render(scene, camera);
        const dataURL = renderer.domElement.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = 'voxel-view-screenshot.png';
        link.click();
    }
}

async function createCollage(viewsToCapture = []) {
    if (!renderer || viewsToCapture.length === 0) return null;

    const originalState = {
        position: camera.position.clone(),
        quaternion: camera.quaternion.clone(),
        target: controls.target.clone()
    };

    const singleViewWidth = renderer.domElement.width;
    const singleViewHeight = renderer.domElement.height;

    const cols = Math.ceil(Math.sqrt(viewsToCapture.length));
    const rows = Math.ceil(viewsToCapture.length / cols);

    const collageCanvas = document.createElement('canvas');
    collageCanvas.width = cols * singleViewWidth;
    collageCanvas.height = rows * singleViewHeight;
    const ctx = collageCanvas.getContext('2d');
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, collageCanvas.width, collageCanvas.height);

    ctx.font = '24px sans-serif';
    ctx.fillStyle = 'white';
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 4;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    for (let i = 0; i < viewsToCapture.length; i++) {
        const viewName = viewsToCapture[i];

        if (viewName === 'current') {
            camera.position.copy(originalState.position);
            camera.quaternion.copy(originalState.quaternion);
            controls.target.copy(originalState.target);
            controls.update();
        } else {
            setCameraView(viewName);
        }

        renderer.render(scene, camera);
        await sleep(10);
        const dataURL = renderer.domElement.toDataURL();

        const img = new Image();
        const promise = new Promise(resolve => img.onload = resolve);
        img.src = dataURL;
        await promise;

        const col = i % cols;
        const row = Math.floor(i / cols);
        const dx = col * singleViewWidth;
        const dy = row * singleViewHeight;

        ctx.drawImage(img, dx, dy);
        const label = viewName.charAt(0).toUpperCase() + viewName.slice(1);
        ctx.strokeText(label, dx + singleViewWidth / 2, dy + 10);
        ctx.fillText(label, dx + singleViewWidth / 2, dy + 10);
    }

    camera.position.copy(originalState.position);
    camera.quaternion.copy(originalState.quaternion);
    controls.target.copy(originalState.target);
    controls.update();

    return collageCanvas.toDataURL('image/jpeg', 0.9);
}

async function handleMultiViewScreenshot() {
    const btn = document.getElementById('multi-screenshot-btn');
    btn.disabled = true;
    btn.textContent = '生成中...';

    const collageDataUrl = await createCollage(['front', 'back', 'left', 'right', 'top', 'bottom']);

    if (collageDataUrl) {
        const link = document.createElement('a');
        link.href = collageDataUrl;
        link.download = 'multi-view-collage.jpg';
        link.click();
    }

    btn.disabled = false;
    btn.textContent = '多视角拼贴图';
}

function handleExportToTxt() {
    if (voxelProperties.size === 0) {
        alert("没有体素数据可导出。");
        return;
    }

    const outputLines = [];
    outputLines.push("# Voxel Export Data");
    outputLines.push("# Format: x y z blockId metaData");

    voxelProperties.forEach((props, coordString) => {
        const [x, y, z] = coordString.split(',');
        const blockId = props.blockId || 0;
        const metaData = props.metaData || 0;
        outputLines.push(`${x} ${y} ${z} ${blockId} ${metaData}`);
    });

    const textContent = outputLines.join('\\n');
    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'voxel_output.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


function handleDeleteSelection() {
    if (selectedVoxelCoords.size > 0) {
        selectedVoxelCoords.forEach(coord => {
            currentVoxelCoords.delete(coord);
            voxelProperties.delete(coord);
        });
        selectedVoxelCoords.clear();
        selectedPartId = null;
        displayVoxels();
        saveAppStateToLocalStorage(); // 保存状态
    }
}

function handleApplyMaterialToSelection() {
    if (selectedVoxelCoords.size > 0 && selectedMaterial) {
        selectedVoxelCoords.forEach(coord => {
            if (currentVoxelCoords.has(coord)) {
                const currentProps = voxelProperties.get(coord);
                voxelProperties.set(coord, {
                    ...currentProps,
                    blockId: selectedMaterial.id,
                    metaData: selectedMaterial.meta,
                });
            }
        });
        displayVoxels();
        saveAppStateToLocalStorage(); // 保存状态
    }
}

function unhideAllParts() {
    if (isolateTimer) {
        clearTimeout(isolateTimer);
        isolateTimer = null;
    }
    if (!loadedModel) return;
    modelParts.forEach(p => {
        const partObject = loadedModel.getObjectByProperty('uuid', p.uuid);
        if (partObject) {
            partObject.visible = true;
            p.visible = true;
        }
    });
    voxelizeAndDisplay(loadedModel);
    updateSceneInspector();
}

function onCanvasClick(event) {
    if (isAgentRunning) return;
    const mount = document.getElementById('mount');
    if (!mount || !raycaster || !camera || !voxelContainerGroup || currentVoxelCoords.size === 0) return;
    const rect = mount.getBoundingClientRect();
    mouseNdc.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseNdc.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouseNdc, camera);
    const instancedMeshes = voxelContainerGroup.children.filter(child => child instanceof THREE.InstancedMesh);
    if (instancedMeshes.length === 0) {
        selectedVoxelCoords.clear();
        selectedPartId = null;
        updateSelectionUI();
        return;
    }
    const intersects = raycaster.intersectObjects(instancedMeshes, false);
    if (intersects.length > 0 && intersects[0].instanceId !== undefined) {
        const intersection = intersects[0];
        const instancedMesh = intersection.object;
        const instanceId = intersection.instanceId;
        const coordString = instancedMesh.userData.coordMap?.[instanceId];
        if (coordString) {
            selectedVoxelCoords.clear();
            selectedVoxelCoords.add(coordString);
            const voxelProps = voxelProperties.get(coordString);
            selectedPartId = voxelProps?.partId || null;
        } else {
            selectedVoxelCoords.clear();
            selectedPartId = null;
        }
    } else {
        selectedVoxelCoords.clear();
        selectedPartId = null;
    }
    updateSelectionHighlight();
    updateSelectionUI();
}

// ====================================================================
// UI Update Functions
// ====================================================================
function updateAgentButtonState() {
    const btn = document.getElementById('ai-agent-btn');
    if (btn) {
        const isReady = loadedModel !== null && loadedTextures.size > 0 && referenceImage !== null;
        btn.disabled = !isReady;
        if (!isReady) {
            let title = "请按顺序完成：";
            if (!loadedModel) title += " 1.加载模型";
            else if (loadedTextures.size === 0) title += " 2.加载材质包";
            else if (!referenceImage) title += " 3.上传参考图";
            btn.title = title;
        } else {
            btn.title = "让 AI 自动为所有部件添加材质";
        }
    }
}

function updateSelectionHighlight() {
    if (!selectionHighlightMesh) return;
    const coordsArray = Array.from(selectedVoxelCoords);
    selectionHighlightMesh.count = coordsArray.length;
    if (coordsArray.length > 0) {
        const matrix = new THREE.Matrix4();
        const halfGrid = GRID_SIZE / 2;
        coordsArray.forEach((coord, i) => {
            const [x, y, z] = coord.split(',').map(Number);
            matrix.setPosition(-halfGrid + (x + 0.5) * VOXEL_SIZE, (y + 0.5) * VOXEL_SIZE, -halfGrid + (z + 0.5) * VOXEL_SIZE);
            selectionHighlightMesh.setMatrixAt(i, matrix);
        });
        selectionHighlightMesh.instanceMatrix.needsUpdate = true;
    }
}

function updateSelectionUI() {
    const hasSelection = selectedVoxelCoords.size > 0;
    const canApplyMaterial = hasSelection && !!selectedMaterial;
    document.getElementById('delete-selection-btn').disabled = !hasSelection;
    document.getElementById('apply-material-btn').disabled = !canApplyMaterial;
    const partItems = document.querySelectorAll('#model-parts-list li');
    partItems.forEach(item => {
        if (item.dataset.uuid === selectedPartId) {
            item.classList.add('ring-2', 'ring-yellow-400');
        } else {
            item.classList.remove('ring-2', 'ring-yellow-400');
        }
    });
}

function populateMaterialInventory() {
    const materialGrid = document.getElementById('material-grid');
    const allMaterials = getAllMinecraftMaterials();
    materialGrid.innerHTML = '';
    allMaterials.forEach(material => {
        const button = document.createElement('button');
        button.className = 'p-2 rounded-md text-xs font-medium transition-all bg-gray-700 hover:bg-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500';
        button.textContent = material.name;

        if (!material.isAvailable) {
            button.classList.add('opacity-40', 'cursor-not-allowed');
            button.classList.remove('hover:bg-gray-600');
            button.disabled = true;
            button.title = '材质包中未找到此贴图';
        }

        button.onclick = () => {
            if (isAgentRunning) return;
            selectedMaterial = material;
            document.querySelectorAll('#material-grid button').forEach(btn => btn.classList.remove('bg-blue-600', 'ring-2', 'ring-blue-300'));
            button.classList.add('bg-blue-600', 'ring-2', 'ring-blue-300');
            document.getElementById('material-inventory-btn').textContent = `编辑 (${material.name})`;
            updateSelectionUI();
        };
        materialGrid.appendChild(button);
    });
}

function updateSceneInspector() {
    const listContainer = document.getElementById('model-parts-list');
    listContainer.innerHTML = '';
    if (modelParts.length === 0) {
        listContainer.textContent = '加载模型以查看其部件。';
        return;
    }
    const ul = document.createElement('ul');
    ul.className = 'space-y-1';
    modelParts.forEach(part => {
        const li = document.createElement('li');
        li.dataset.uuid = part.uuid;
        li.className = `w-full text-left flex items-center justify-between p-2 rounded-md text-xs transition-all ${part.visible ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-900 hover:bg-gray-800 text-gray-400'}`;

        const leftSide = document.createElement('div');
        leftSide.className = 'flex-grow flex flex-col items-start truncate';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'truncate cursor-pointer font-semibold text-gray-200';
        nameSpan.textContent = part.name;
        nameSpan.title = `选择 ${part.name} 中的所有体素`;
        nameSpan.onclick = () => {
            if (isAgentRunning) return;
            selectPartProgrammatically(part.uuid);
        };

        const tagsContainer = document.createElement('div');
        tagsContainer.className = 'flex items-center space-x-1 mt-1';

        const countTag = document.createElement('span');
        countTag.className = 'text-xs bg-gray-600 text-gray-300 px-1.5 py-0.5 rounded';
        countTag.textContent = `${part.voxelCount || 0} 方块`;
        tagsContainer.appendChild(countTag);

        if (part.isOccluded) {
            const occludedTag = document.createElement('span');
            occludedTag.className = 'text-xs bg-red-800 text-red-200 px-1.5 py-0.5 rounded font-semibold';
            occludedTag.textContent = '不可见';
            tagsContainer.appendChild(occludedTag);
        }

        leftSide.appendChild(nameSpan);
        leftSide.appendChild(tagsContainer);

        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'flex-shrink-0 flex items-center space-x-2';

        const isolateBtn = document.createElement('button');
        isolateBtn.className = 'bg-transparent border-none p-0 text-gray-400 hover:text-white';
        isolateBtn.title = `仅显示 ${part.name}`;
        isolateBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>`;
        isolateBtn.onclick = () => {
            if (isAgentRunning) return;
            if (!loadedModel) return;
            if (isolateTimer) clearTimeout(isolateTimer);

            modelParts.forEach(p => {
                const partObject = loadedModel.getObjectByProperty('uuid', p.uuid);
                if (partObject) {
                    const shouldBeVisible = p.uuid === part.uuid;
                    partObject.visible = shouldBeVisible;
                    p.visible = shouldBeVisible;
                }
            });
            voxelizeAndDisplay(loadedModel);
            updateSceneInspector();

            isolateTimer = setTimeout(unhideAllParts, 5000);
        };

        const visibilityBtn = document.createElement('button');
        visibilityBtn.className = 'bg-transparent border-none p-0 text-gray-400 hover:text-white';
        visibilityBtn.title = `点击以${part.visible ? '隐藏' : '显示'} ${part.name}`;
        visibilityBtn.innerHTML = part.visible ? `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>` : `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7 1.274 4.057 5.064 7 9.542 7 .847 0 1.67.11 2.454.316m5.097 5.097a10.02 10.02 0 01-1.34 2.456M18 12a6 6 0 11-12 0 6 6 0 0112 0z" /><path stroke-linecap="round" stroke-linejoin="round" d="M1 1l22 22" /></svg>`;
        visibilityBtn.onclick = () => {
            if (isAgentRunning) return;
            if (!loadedModel) return;
            if (isolateTimer) {
                clearTimeout(isolateTimer);
                isolateTimer = null;
            }
            const partObject = loadedModel.getObjectByProperty('uuid', part.uuid);
            if (partObject) {
                partObject.visible = !partObject.visible;
                part.visible = partObject.visible;
                voxelizeAndDisplay(loadedModel);
                updateSceneInspector();
            }
        };

        li.appendChild(leftSide);
        buttonGroup.appendChild(isolateBtn);
        buttonGroup.appendChild(visibilityBtn);
        li.appendChild(buttonGroup);
        ul.appendChild(li);
    });
    listContainer.appendChild(ul);
}

// ====================================================================
// AI Assistant & Agent Functions
// ====================================================================

async function handleAiChatSend() {
    const userInput = document.getElementById('ai-user-input');
    const sendBtn = document.getElementById('ai-send-btn');
    const message = userInput.value.trim();

    if (!message || sendBtn.disabled) return;

    addAiChatMessage('user', message);
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;

    const thinkingMsgId = `thinking-${Date.now()}`;
    addAiChatMessage('ai', '思考中...', [], [], thinkingMsgId);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                apiKey: geminiApiKey,
                model: currentAiModel
            })
        });

        const result = await response.json();

        const thinkingBubble = document.getElementById(thinkingMsgId);
        if (thinkingBubble) {
            thinkingBubble.remove();
        }

        if (!response.ok) {
            const errorMessage = result.error || `HTTP error! status: ${response.status}`;
            throw new Error(errorMessage);
        }

        addAiChatMessage('ai', result.reply);

    } catch (error) {
        const thinkingBubble = document.getElementById(thinkingMsgId);
        if (thinkingBubble) {
            thinkingBubble.remove();
        }
        console.error('AI Chat Error:', error);
        addAiChatMessage('system', `抱歉，与 AI 通信时发生错误: ${error.message}`);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function selectPartProgrammatically(uuid) {
    selectedVoxelCoords.clear();
    voxelProperties.forEach((props, coord) => {
        if (props.partId === uuid) selectedVoxelCoords.add(coord);
    });
    selectedPartId = uuid;
    updateSelectionHighlight();
    updateSelectionUI();
}

function addAiChatMessage(sender, text, images = [], actions = [], elementId = null) {
    const chatHistory = document.getElementById('ai-chat-history');
    const msgContainer = document.createElement('div');
    if (elementId) {
        msgContainer.id = elementId;
    }
    const bubbleDiv = document.createElement('div');

    msgContainer.className = `flex flex-col ${sender === 'user' ? 'items-end' : 'items-start'}`;
    bubbleDiv.className = `max-w-[90%] p-2.5 rounded-lg text-sm whitespace-pre-wrap ${
        sender === 'user' ? 'bg-blue-600 text-white' :
        sender === 'ai' ? 'bg-gray-600 text-gray-100' :
        'bg-yellow-600 bg-opacity-50 text-yellow-100 italic'
    }`;

    const validImages = images.filter(Boolean);
    if (validImages.length > 0) {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'mb-2 flex flex-col space-y-1';

        validImages.forEach(imgData => {
            const img = document.createElement('img');
            img.src = imgData.src;
            img.className = "rounded-md w-full h-auto bg-gray-700";

            const label = document.createElement('span');
            label.className = "text-xs text-center text-gray-400 font-semibold";
            label.textContent = imgData.label;

            const container = document.createElement('div');
            container.appendChild(img);
            container.appendChild(label);
            imageContainer.appendChild(container);
        });
        bubbleDiv.appendChild(imageContainer);
    }

    const textNode = document.createElement('span');
    text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="font-semibold">$1</strong>');
    text = text.replace(/_reasoning: (.*)_/g, '<br><em class="text-xs text-gray-400 block mt-1">理由: $1</em>');
    textNode.innerHTML = text;
    bubbleDiv.appendChild(textNode);
    msgContainer.appendChild(bubbleDiv);

    if (actions.length > 0) {
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'flex space-x-2 mt-2';
        actions.forEach(action => {
            const button = document.createElement('button');
            button.textContent = action.label;
            button.className = 'bg-blue-600 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded-md text-sm';
            button.onclick = () => {
                action.callback();
                buttonsContainer.remove();
            };
            buttonsContainer.appendChild(button);
        });
        msgContainer.appendChild(buttonsContainer);
    }

    chatHistory.appendChild(msgContainer);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function startAiAgent() {
    if (isAgentRunning) return;
    agentCurrentPartIndex = 0;
    agentOverallAnalysis = "";
    isAgentRunning = true;
    isAgentPaused = false;

    document.getElementById('ai-agent-btn').classList.add('hidden');
    document.getElementById('ai-agent-controls').classList.remove('hidden');
    document.getElementById('ai-agent-pause-btn').classList.remove('hidden');
    document.getElementById('ai-agent-continue-btn').classList.add('hidden');
    document.getElementById('ai-send-btn').disabled = true;

    addAiChatMessage('system', `🤖 AI 代理已启动，使用模型 **${currentAiModel}**。`);
    runAiAgentLoop();
}

function pauseAiAgent() {
    if (!isAgentRunning || isAgentPaused) return;
    isAgentPaused = true;
    if (agentAbortController) {
        agentAbortController.abort();
    }
    document.getElementById('ai-agent-pause-btn').classList.add('hidden');
    document.getElementById('ai-agent-continue-btn').classList.remove('hidden');
    addAiChatMessage('system', '⏸️ 代理已暂停。点击“继续”以恢复。');
}

function continueAiAgent() {
    if (!isAgentRunning || !isAgentPaused) return;
    isAgentPaused = false;
    document.getElementById('ai-agent-pause-btn').classList.remove('hidden');
    document.getElementById('ai-agent-continue-btn').classList.add('hidden');
    addAiChatMessage('system', '▶️ 代理已恢复运行...');
    runAiAgentLoop();
}

function stopAiAgent(reason = '用户手动停止') {
    if (!isAgentRunning && !isAgentPaused) return;
     if (agentAbortController) {
        agentAbortController.abort();
    }
    isAgentRunning = false;
    isAgentPaused = false;
    agentCurrentPartIndex = 0;
    agentOverallAnalysis = "";

    document.getElementById('ai-agent-btn').classList.remove('hidden');
    document.getElementById('ai-agent-controls').classList.add('hidden');
    document.getElementById('ai-send-btn').disabled = false;

    addAiChatMessage('system', `⏹️ AI 代理已停止。原因: ${reason}。`);
}

async function runAiAgentLoop() {
    try {
        if (agentCurrentPartIndex === 0 && !agentOverallAnalysis) {
            addAiChatMessage('system', '正在进行初步分析...');
            const fullModelCollage = await createCollage(['front', 'back', 'left', 'right', 'top', 'bottom']);
            if (isAgentPaused) return;
            addAiChatMessage('system', '正在请求 AI 建立总体艺术风格...', [{src: referenceImage, label: "参考图 (艺术风格)"}, {src: fullModelCollage, label: "3D模型 (当前结构)"}]);
            const analysisPrompt = `您是一位顶级的艺术鉴赏家。请仔细研究“参考图”和“3D模型”。
**您的唯一任务是**: 用一句话捕捉并描述出参考图的**核心感觉**。
这句话应该包含关键的**材质/纹理**和**整体氛围**。
例如：“一个由风化石砖和深色木头构成的古老图书馆，氛围庄严而神秘”，或者“一个由闪亮金属和霓虹灯组成的赛博朋克城市，感觉混乱而充满活力”。
**请只使用以下JSON格式响应**: '{"analysis": "您总结的核心感觉"}'`;
            const userParts = [ { text: analysisPrompt }, { text: "\\n这是 [参考图 (艺术风格)]:" }, { inlineData: { mimeType: 'image/jpeg', data: referenceImage.split(',')[1] } }, { text: "\\n这是 [3D模型 (当前结构)]:" }, { inlineData: { mimeType: 'image/jpeg', data: fullModelCollage.split(',')[1] } } ];
            agentAbortController = new AbortController();
            const analysisResult = await callGeminiAPI(userParts, agentAbortController.signal);
            agentOverallAnalysis = analysisResult.analysis || "一个标准的 Minecraft 风格建筑";
            addAiChatMessage('system', `AI 已确立核心感觉: **${agentOverallAnalysis}**`);
            await sleep(1500);
            addAiChatMessage('system', '分析完成。现在将根据此方向逐个为部件应用材质...');
            await sleep(1500);
        }

        const allMaterials = getAllMinecraftMaterials().filter(m => m.isAvailable);
        const materialListString = allMaterials.map(m => `"${m.name}"`).join(', ');
        const visibleParts = modelParts.filter(p => !p.isOccluded && p.voxelCount > 0);
        const materialHistory = [];

        while (agentCurrentPartIndex < visibleParts.length) {
            if (isAgentPaused) return;
            const part = visibleParts[agentCurrentPartIndex];
            addAiChatMessage('system', `处理中 (${agentCurrentPartIndex + 1}/${visibleParts.length}): **${part.name}**`);

            let isPartCompleted = false;
            let retryCount = 0;
            let lastActionResult = null;

            while (!isPartCompleted && retryCount <= AGENT_MAX_RETRIES_PER_PART) {
                if (isAgentPaused) return;

                let actionResult;
                if (retryCount === 0) {
                    const historyString = materialHistory.length > 0
                        ? `**近期历史**: 您最近的材质选择是：${materialHistory.map(h => `对'${h.partName}'使用了'${h.materialName}'`).join('; ')}。`
                        : ``;

                    const actionPrompt = `您是一位富有灵感的艺术家。
**核心感觉**: "**${agentOverallAnalysis}**"。
**当前焦点**: 名为“**${part.name}**”的部件。
${historyString}
**您的任务**: 基于“核心感觉”和“近期历史”，从“可用材质”列表中选择一个最合适的材质，并解释原因。
**可用材质**: [${materialListString}]
请**只**使用以下JSON格式响应: '{"materialName": "选择的材质名", "reasoning": "您的艺术理由"}'`;

                    const partCollage = await createIsolatedPartCollage(part.uuid);
                    if (isAgentPaused) return;
                    addAiChatMessage('system', `正在为 **${part.name}** 请求材质建议...`, [{src: referenceImage, label: "参考图"}, {src: partCollage, label: `当前部件: ${part.name}`}]);
                    const userParts = [ { text: actionPrompt }, { text: "\\n[参考图]:" }, { inlineData: { mimeType: 'image/jpeg', data: referenceImage.split(',')[1] } }, { text: `\\n[当前部件: ${part.name}]:` }, { inlineData: { mimeType: 'image/jpeg', data: partCollage.split(',')[1] } } ];
                    agentAbortController = new AbortController();
                    actionResult = await callGeminiAPI(userParts, agentAbortController.signal);
                } else {
                    actionResult = lastActionResult;
                }

                const targetMaterial = allMaterials.find(m => m.name.toLowerCase() === actionResult?.materialName?.toLowerCase());
                if (targetMaterial) {
                    const lastMaterialName = targetMaterial.name;
                    const reasoning = actionResult.reasoning ? `_reasoning: ${actionResult.reasoning}_` : "";
                    addAiChatMessage('ai', `**应用**: 为 **${part.name}** 应用 **${targetMaterial.name}**。${reasoning}`);
                    selectPartProgrammatically(part.uuid);
                    selectedMaterial = targetMaterial;
                    handleApplyMaterialToSelection();
                    await sleep(1500);

                    // 简化审核，信任AI的“感觉”
                    addAiChatMessage('system', `✅ 应用完成`);
                    materialHistory.push({ partName: part.name, materialName: lastMaterialName });
                    if (materialHistory.length > 5) materialHistory.shift();
                    isPartCompleted = true;
                } else {
                   addAiChatMessage('system', `⚠️ **材质无效**，跳过部件 **${part.name}**...`);
                   isPartCompleted = true;
                }
            }
            if (retryCount > AGENT_MAX_RETRIES_PER_PART) {
                 addAiChatMessage('system', `⚠️ **重试次数过多**，强制继续处理下一个部件...`);
            }
            agentCurrentPartIndex++;
        }
        stopAiAgent('任务完成');
    } catch (error) {
         if (error.name === 'AbortError') {
             console.log('Agent fetch aborted by user control.');
         } else {
             addAiChatMessage('system', `代理在执行过程中遇到错误: ${error.message}`);
             stopAiAgent('执行出错');
         }
    }
}

async function createIsolatedPartCollage(partUuid) {
    voxelContainerGroup.visible = false;
    selectionHighlightMesh.visible = false;
    const isolatedGroup = new THREE.Group();
    const materialToInstancesMap = new Map();
    voxelProperties.forEach((props, coordString) => {
        if (props.partId === partUuid) {
            const textureKey = getTextureKeyForVoxel(props.blockId, props.metaData, DEFAULT_BLOCK_ID_LIST);
            if (!materialToInstancesMap.has(textureKey)) materialToInstancesMap.set(textureKey, []);
            const [x, y, z] = coordString.split(',').map(Number);
            const halfGrid = GRID_SIZE / 2;
            const posX = -halfGrid + (x + 0.5) * VOXEL_SIZE;
            const posY = (y + 0.5) * VOXEL_SIZE;
            const posZ = -halfGrid + (z + 0.5) * VOXEL_SIZE;
            materialToInstancesMap.get(textureKey).push({ matrix: new THREE.Matrix4().setPosition(posX, posY, posZ) });
        }
    });
    const baseVoxelGeometry = new THREE.BoxGeometry(VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98);
    materialToInstancesMap.forEach((instances, textureKey) => {
        const texture = loadedTextures.get(textureKey);
        const material = texture ? new THREE.MeshStandardMaterial({ map: texture }) : new THREE.MeshLambertMaterial({ color: TEXTURE_KEY_TO_COLOR_MAP[textureKey] || 0xff00ff });
        const instancedMesh = new THREE.InstancedMesh(baseVoxelGeometry, material, instances.length);
        instancedMesh.castShadow = true;
        instances.forEach((d, i) => instancedMesh.setMatrixAt(i, d.matrix));
        instancedMesh.instanceMatrix.needsUpdate = true;
        isolatedGroup.add(instancedMesh);
    });
    scene.add(isolatedGroup);
    const partCollage = await createCollage(['front', 'back', 'left', 'right', 'top', 'bottom']);
    scene.remove(isolatedGroup);
    isolatedGroup.children.forEach(c => { c.geometry.dispose(); if(Array.isArray(c.material)) c.material.forEach(m=>m.dispose()); else c.material.dispose(); });
    voxelContainerGroup.visible = true;
    selectionHighlightMesh.visible = true;
    renderer.render(scene, camera);
    return partCollage;
}

async function callGeminiAPI(userParts, signal) {
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${currentAiModel}:generateContent?key=${geminiApiKey}`;
    const payload = { contents: [{ role: "user", parts: userParts }], generationConfig: { responseMimeType: "application/json" } };
    const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: signal });
    if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error Response:", errorText);
        throw new Error(`API 调用失败: ${response.status} ${response.statusText}`);
    }
    const result = await response.json();
    if(!result.candidates || !result.candidates[0].content?.parts?.[0]?.text){
        console.error("Invalid API response structure:", result);
        throw new Error("API返回了无效的数据结构。");
    }
    try {
         return JSON.parse(result.candidates[0].content.parts[0].text);
    } catch (e) {
         console.error("Failed to parse JSON from AI response:", result.candidates[0].content.parts[0].text);
         throw new Error("AI返回了非法的JSON格式。");
    }
}

// ====================================================================
// State Persistence
// ====================================================================

function saveAppStateToLocalStorage() {
    if (voxelProperties.size === 0) {
        localStorage.removeItem('appState');
        console.log("No voxel data to save, cleared localStorage.");
        return;
    }

    const appState = {
        voxelProperties: Object.fromEntries(voxelProperties),
        modelParts: modelParts,
        timestamp: new Date().toISOString()
    };

    try {
        localStorage.setItem('appState', JSON.stringify(appState));
        console.log(`App state saved to localStorage at ${appState.timestamp}`);
    } catch (e) {
        console.error("Error saving state to localStorage:", e);
        // 尝试清除旧的存储并重试
        localStorage.removeItem('appState');
        try {
            localStorage.setItem('appState', JSON.stringify(appState));
            console.log("Cleared old state and successfully saved app state.");
        } catch (e2) {
            console.error("Failed to save state even after clearing:", e2);
        }
    }
}

function loadAppStateFromLocalStorage() {
    const savedStateJSON = localStorage.getItem('appState');
    if (!savedStateJSON) {
        console.log("No saved state found in localStorage.");
        return false;
    }

    try {
        const savedState = JSON.parse(savedStateJSON);
        console.log(`Found saved state from ${savedState.timestamp}`);

        // 恢复 Voxel 数据
        voxelProperties.clear();
        currentVoxelCoords.clear();

        const savedVoxelProps = savedState.voxelProperties || {};
        for (const coordString in savedVoxelProps) {
            if (Object.hasOwnProperty.call(savedVoxelProps, coordString)) {
                currentVoxelCoords.add(coordString);
                voxelProperties.set(coordString, savedVoxelProps[coordString]);
            }
        }

        // 恢复模型部件
        modelParts = savedState.modelParts || [];

        if (currentVoxelCoords.size > 0) {
            // 模拟一个已加载的模型以启用依赖于它的功能
            if (!loadedModel) {
                loadedModel = new THREE.Group();
                loadedModel.name = "Restored from LocalStorage";
            }
            displayVoxels();
            updateSceneInspector();
            updateAgentButtonState();
            addAiChatMessage('system', `✅ 成功从浏览器缓存恢复了您上次的编辑。`);
            return true;
        }
        return false;

    } catch (e) {
        console.error("Error loading state from localStorage:", e);
        localStorage.removeItem('appState'); // 清除损坏的数据
        return false;
    }
}

// ====================================================================
// Initial Setup and Event Binding
// ====================================================================

function unlockUI() {
    const mainContainer = document.getElementById('main-container');
    const apiKeyModal = document.getElementById('api-key-modal');

    apiKeyModal.classList.add('hidden');
    mainContainer.classList.remove('opacity-20', 'pointer-events-none');

    document.querySelectorAll('button, input, textarea').forEach(el => {
        el.disabled = false;
    });
    // Re-disable buttons that should be initially disabled
    updateAgentButtonState();
    updateSelectionUI();
}

async function initializeApp() {
    console.log("Initializing application...");
    init(); // Init 3D scene & UI bindings

    // --- 智能加载顺序 ---
    // 1. 优先从命令行传入的存档文件加载
    if (window.initialSaveData) {
        console.log("Applying initial save data from command line...");
        await applySaveData(window.initialSaveData);
         // 加载后，加载任何非模型的辅助文件（如材质包）
        await loadInitialFilesFromServer(true); // skipModel=true
        console.log("Initialization complete (loaded from save file).");
        return;
    }

    // 2. 其次，尝试从浏览器本地存储恢复
    const loadedFromStorage = loadAppStateFromLocalStorage();
    if (loadedFromStorage) {
        // 加载后，加载任何非模型的辅助文件（如材质包）
        await loadInitialFilesFromServer(true); // skipModel=true
        console.log("Initialization complete (restored from localStorage).");
        return;
    }

    // 3. 最后，如果都没有，则从 input 文件夹加载默认模型
    console.log("No save data or local state found, loading default files...");
    await loadInitialFilesFromServer(false); // skipModel=false
    console.log("Application initialization complete (loaded default files).");
}

// Make key functions globally available for testing
window.init = init;
window.initializeApp = initializeApp;
window.displayVoxels = displayVoxels;
window.unlockUI = unlockUI;
window.playFallingAnimation = playFallingAnimation;

async function handleApiKeyValidation() {
    const modalInput = document.getElementById('modal-api-key-input');
    const errorMsg = document.getElementById('api-key-error-msg');
    const validateBtn = document.getElementById('validate-api-key-btn');
    const btnText = document.getElementById('validate-btn-text');
    const btnSpinner = document.getElementById('validate-btn-spinner');

    const key = modalInput.value;
    if (!key) {
        errorMsg.textContent = 'API 密钥不能为空。';
        return;
    }

    validateBtn.disabled = true;
    btnText.classList.add('hidden');
    btnSpinner.classList.remove('hidden');
    errorMsg.textContent = '';

    try {
        const response = await fetch('/api/validate_key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ apiKey: key })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            geminiApiKey = key;
            localStorage.setItem('geminiApiKey', key);
            document.getElementById('api-key-input').value = key;
            unlockUI();
            initializeApp(); // Centralized initialization
        } else {
            errorMsg.textContent = result.message || '验证失败，请重试。';
        }
    } catch (error) {
        console.error('Validation fetch error:', error);
        errorMsg.textContent = '无法连接到服务器进行验证。';
    } finally {
        validateBtn.disabled = false;
        btnText.classList.remove('hidden');
        btnSpinner.classList.add('hidden');
    }
}


document.addEventListener('DOMContentLoaded', () => {
    // 首先检查密钥是否已在服务器端预先验证
    if (window.isKeyPreValidated && window.apiKeyFromFile) {
        console.log("Key was pre-validated on server. Unlocking UI.");
        geminiApiKey = window.apiKeyFromFile;
        localStorage.setItem('geminiApiKey', geminiApiKey); // Store the valid key
        document.getElementById('api-key-input').value = geminiApiKey;
        unlockUI();
        initializeApp(); // Use centralized init
    } else {
        // 如果没有预先验证的密钥，则回退到手动输入流程
        console.log("No pre-validated key. Starting manual validation flow.");
        const validateBtn = document.getElementById('validate-api-key-btn');
        const modalInput = document.getElementById('modal-api-key-input');

        validateBtn.addEventListener('click', handleApiKeyValidation);
        modalInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleApiKeyValidation();
            }
        });

        // 自动验证存储在 localStorage 中的密钥
        const storedKey = localStorage.getItem('geminiApiKey');
         if (storedKey) {
            modalInput.value = storedKey;
            handleApiKeyValidation(); // This will now call initializeApp on success
        } else if (window.initialSaveData) {
            // This case handles when there's save data but no API key yet.
            // We can unlock the UI to show the model, but AI features will wait for a key.
            console.log("Initial save data found, but no API key. Unlocking UI to show model.");
            unlockUI();
            init();
            applySaveData(window.initialSaveData);
            // AI features will remain locked until a key is entered manually.
        }
    }

    // --- 其他事件监听器 ---
    const modelNameDisplay = document.getElementById('ai-model-name-display');
    modelNameDisplay.textContent = currentAiModel;
    document.getElementById('ai-model-toggle-btn').addEventListener('click', () => {
        if(isAgentRunning || isAgentPaused) return;
        currentAiModel = currentAiModel === FLASH_MODEL_NAME ? PRO_MODEL_NAME : FLASH_MODEL_NAME;
        modelNameDisplay.textContent = currentAiModel;
        addAiChatMessage('system', `AI 模型已切换为 **${currentAiModel}**。`);
    });

    const toggleInspectorBtn = document.getElementById('toggle-inspector-btn');
    const modelPartsList = document.getElementById('model-parts-list');
    const chevronUp = document.getElementById('inspector-chevron-up');
    const chevronDown = document.getElementById('inspector-chevron-down');
    toggleInspectorBtn.addEventListener('click', () => {
        modelPartsList.classList.toggle('hidden');
        chevronUp.classList.toggle('hidden');
        chevronDown.classList.toggle('hidden');
    });
    document.getElementById('modelInput').addEventListener('change', handleModelLoad);
    document.getElementById('texturePackInput').addEventListener('change', handleTexturePackLoad);
    document.getElementById('reference-image-input').addEventListener('change', handleReferenceImageLoad);
    document.getElementById('view-front').addEventListener('click', () => setCameraView('front'));
    document.getElementById('view-back').addEventListener('click', () => setCameraView('back'));
    document.getElementById('view-left').addEventListener('click', () => setCameraView('left'));
    document.getElementById('view-right').addEventListener('click', () => setCameraView('right'));
    document.getElementById('view-top').addEventListener('click', () => setCameraView('top'));
    document.getElementById('view-bottom').addEventListener('click', () => setCameraView('bottom'));
    document.getElementById('screenshot-btn').addEventListener('click', handleScreenshot);
    document.getElementById('multi-screenshot-btn').addEventListener('click', handleMultiViewScreenshot);
    document.getElementById('export-txt-btn').addEventListener('click', handleExportToTxt);
    document.getElementById('delete-selection-btn').addEventListener('click', handleDeleteSelection);
    document.getElementById('apply-material-btn').addEventListener('click', handleApplyMaterialToSelection);
    const materialPanel = document.getElementById('material-inventory-panel');
    document.getElementById('material-inventory-btn').addEventListener('click', () => materialPanel.classList.remove('hidden'));
    document.getElementById('close-material-panel-btn').addEventListener('click', () => materialPanel.classList.add('hidden'));
    materialPanel.addEventListener('click', (e) => { if (e.target === materialPanel) materialPanel.classList.add('hidden'); });
    const aiPanel = document.getElementById('ai-assistant-panel');
    document.getElementById('ai-assistant-btn').addEventListener('click', () => aiPanel.classList.toggle('hidden'));
    document.getElementById('ai-panel-close-btn').addEventListener('click', () => aiPanel.classList.add('hidden'));
    document.getElementById('ai-clear-chat-btn').addEventListener('click', () => {
        document.getElementById('ai-chat-history').innerHTML = '';
         addAiChatMessage('system', '欢迎！请按左上角的步骤加载模型、材质和参考图以开始。');
    });
    document.getElementById('ai-send-btn').addEventListener('click', handleAiChatSend);
    document.getElementById('ai-user-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAiChatSend();
        }
    });
    document.getElementById('ai-agent-btn').addEventListener('click', startAiAgent);
    document.getElementById('ai-agent-pause-btn').addEventListener('click', pauseAiAgent);
    document.getElementById('ai-agent-continue-btn').addEventListener('click', continueAiAgent);
    document.getElementById('ai-agent-stop-btn').addEventListener('click', () => stopAiAgent('用户手动停止'));
    const apiKeyPopup = document.getElementById('api-key-popup');
    document.getElementById('api-key-manager-btn').addEventListener('click', () => apiKeyPopup.classList.toggle('hidden'));
    document.getElementById('api-key-save').addEventListener('click', () => {
        geminiApiKey = document.getElementById('api-key-input').value;
        localStorage.setItem('geminiApiKey', geminiApiKey);
        apiKeyPopup.classList.add('hidden');
        addAiChatMessage('system', 'API 密钥已保存。');
    });
    document.getElementById('api-key-cancel').addEventListener('click', () => apiKeyPopup.classList.add('hidden'));

    // --- 存档功能事件监听器 ---
    document.getElementById('export-save-btn').addEventListener('click', handleExportSave);
    document.getElementById('import-save-btn').addEventListener('click', () => {
        document.getElementById('import-save-input').click();
    });
    document.getElementById('import-save-input').addEventListener('change', handleImportSave);
    document.getElementById('import-url-btn').addEventListener('click', handleImportFromUrl);

    // --- 动画功能事件监听器 ---
    document.getElementById('play-animation-btn').addEventListener('click', playFallingAnimation);
    const animationSpeedSlider = document.getElementById('animation-speed-slider');
    const animationSpeedValue = document.getElementById('animation-speed-value');
    animationSpeedSlider.addEventListener('input', () => {
        animationSpeedValue.textContent = parseFloat(animationSpeedSlider.value).toFixed(1);
    });
});

// --- 存档功能函数 ---

function getCurrentVoxelData() {
    const voxelData = {};
    voxelProperties.forEach((props, coordString) => {
        voxelData[coordString] = props;
    });
    return voxelData;
}

function getCurrentChatHistory() {
    const chatMessages = [];
    const chatHistory = document.getElementById('ai-chat-history');
    if (chatHistory) {
        const messages = chatHistory.querySelectorAll('div[class*="flex"]');
        messages.forEach(msg => {
            const text = msg.textContent || '';
            if (text.trim()) {
                chatMessages.push({
                    content: text.trim(),
                    timestamp: new Date().toISOString()
                });
            }
        });
    }
    return chatMessages;
}

function getCurrentAgentState() {
    return {
        is_running: isAgentRunning,
        is_paused: isAgentPaused,
        current_part_index: agentCurrentPartIndex,
        overall_analysis: agentOverallAnalysis,
        model_name: currentAiModel
    };
}

async function handleExportSave() {
    try {
        const voxelData = getCurrentVoxelData();
        const chatHistory = getCurrentChatHistory();
        const agentState = getCurrentAgentState();

        const response = await fetch('/api/save/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                voxelData: voxelData,
                chatHistory: chatHistory,
                agentState: agentState
            })
        });

        if (response.ok) {
            // 触发文件下载
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'mine_builder_save.zip';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            addAiChatMessage('system', '✅ 存档导出成功！');
        } else {
            const result = await response.json();
            throw new Error(result.message || '导出失败');
        }
    } catch (error) {
        console.error('Export save error:', error);
        addAiChatMessage('system', `❌ 导出存档失败: ${error.message}`);
    }
}

async function handleImportSave(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/save/import', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.success) {
            await applySaveData(result.data);
            addAiChatMessage('system', '✅ 存档导入成功！');
        } else {
            throw new Error(result.message || '导入失败');
        }
    } catch (error) {
        console.error('Import save error:', error);
        addAiChatMessage('system', `❌ 导入存档失败: ${error.message}`);
    }

    // 清空文件输入
    event.target.value = '';
}

async function handleImportFromUrl() {
    const urlInput = document.getElementById('save-url-input');
    const url = urlInput.value.trim();

    if (!url) {
        addAiChatMessage('system', '请输入存档URL');
        return;
    }

    try {
        const response = await fetch('/api/save/import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            await applySaveData(result.data);
            addAiChatMessage('system', '✅ 从URL导入存档成功！');
            urlInput.value = '';
        } else {
            throw new Error(result.message || '导入失败');
        }
    } catch (error) {
        console.error('Import from URL error:', error);
        addAiChatMessage('system', `❌ 从URL导入存档失败: ${error.message}`);
    }
}

async function applySaveData(saveData) {
    try {
        // 恢复体素数据
        if (saveData.voxel_data && Object.keys(saveData.voxel_data).length > 0) {
            currentVoxelCoords.clear();
            voxelProperties.clear();

            Object.entries(saveData.voxel_data).forEach(([coordString, props]) => {
                currentVoxelCoords.add(coordString);
                voxelProperties.set(coordString, props);
            });

            // 关键修复：当从存档加载时，我们没有真实的GLTF模型。
            // 我们需要模拟一个已加载的模型，以解锁依赖于它的UI功能（例如AI代理）。
            if (!loadedModel) {
                loadedModel = new THREE.Group(); // 使用一个空的Group作为占位符
                loadedModel.name = "Loaded from Save";
                 addAiChatMessage('system', `从存档恢复了体素模型。AI功能已解锁。`);
            }

            displayVoxels();
            updateAgentButtonState(); // 确保在模型“加载”后更新按钮状态
        }

        // 恢复AI聊天记录
        if (saveData.chat_history && Array.isArray(saveData.chat_history)) {
            const chatHistory = document.getElementById('ai-chat-history');
            if (chatHistory) {
                chatHistory.innerHTML = '';
                saveData.chat_history.forEach(msg => {
                    if (msg.content) {
                        addAiChatMessage('system', `[已恢复] ${msg.content}`);
                    }
                });
            }
        }

        // 恢复AI代理状态
        if (saveData.agent_state) {
            isAgentRunning = saveData.agent_state.is_running || false;
            isAgentPaused = saveData.agent_state.is_paused || false;
            agentCurrentPartIndex = saveData.agent_state.current_part_index || 0;
            agentOverallAnalysis = saveData.agent_state.overall_analysis || '';
            currentAiModel = saveData.agent_state.model_name || FLASH_MODEL_NAME;

            // 更新UI状态
            document.getElementById('ai-model-name-display').textContent = currentAiModel;

            if (isAgentRunning || isAgentPaused) {
                document.getElementById('ai-agent-btn').classList.add('hidden');
                document.getElementById('ai-agent-controls').classList.remove('hidden');

                if (isAgentPaused) {
                    document.getElementById('ai-agent-pause-btn').classList.add('hidden');
                    document.getElementById('ai-agent-continue-btn').classList.remove('hidden');
                } else {
                    document.getElementById('ai-agent-pause-btn').classList.remove('hidden');
                    document.getElementById('ai-agent-continue-btn').classList.add('hidden');
                }
            }
        }

        addAiChatMessage('system', `📁 存档数据已成功恢复 (版本: ${saveData.version || '未知'})`);
        saveAppStateToLocalStorage(); // 保存状态
    } catch (error) {
        console.error('Apply save data error:', error);
        addAiChatMessage('system', `❌ 应用存档数据时出错: ${error.message}`);
    }
}
