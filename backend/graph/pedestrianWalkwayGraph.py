"""
pedestrianWalkwayGraph.py
================================================================================
OFFICIAL MICRO-LEVEL PEDESTRIAN WALKWAY GRAPH (WEIGHTED, DIRECTED, NON-COMPLETE)
================================================================================
Single backend source of truth mirroring the real pedestrian sidewalk, corridor,
door portal, crosswalk, ramp, stairwell, and 2nd-floor covered skybridge network
of the UAM Campus (synchronized with campusWalkwaysLayer.js).

Formal Graph Properties G = (V, E, W):
  - Weighted (W: E -> R+): Every directed edge carries physical walking distance
    in meters along the actual pavement/corridor (calibrated against real GPS).
  - Directed (E subset of V x V): Bidirectional walkways are modeled as symmetric
    pairs of opposite directed edges (u -> v) and (v -> u), enabling directional
    semantics (e.g. stairs up/down, enter/exit doors, one-way constraints).
  - Non-Complete (|E| << |V|(|V|-1)): Sparse topology representing strictly
    walkable physical segments while respecting blocked walls and barriers.
================================================================================
"""

from typing import Dict, List, Optional, Tuple
from .directedGraph import DirectedGraph, Node
from .geoUtils import CampusGeoUtils
from data.campusCategories import CampusCategory


# Exact 1200x850 SVG Pedestrian Waypoints (synchronized with campusWalkwaysLayer.js)
WALKWAY_NODES_SPEC: Dict[str, Tuple[float, float]] = {
    # Main Entrance, South Ring Sidewalk & West Avenue East Sidewalk
    "ent_gate":             (274, 768),
    "ent_corner":           (305, 696),
    "south_walk_1":         (420, 696),
    "south_walk_2":         (534, 696),
    "south_walk_3":         (645, 696),
    "south_se_turn":        (718, 696),
    "west_side_low":        (304, 626),
    "west_side_k_south":    (302, 562),
    "west_side_bank":       (296, 518),
    "banpro_entry":         (230, 518),
    "west_side_k_north":    (298, 482),
    "a_front_plaza":        (298, 435),

    # Building K & Plaza Central Ruben Dario
    "k_west_apron":         (323, 484),
    "k_north_walk":         (346, 484),
    "k_south_walk":         (362, 562),
    "k_se_corner":          (404, 562),
    "k_door_east":          (382, 536),
    "plaza_south_mid":      (464, 562),
    "plaza_south_e":        (508, 558),
    "plaza_north_mid":      (444, 478),
    "plaza_north_east":     (516, 478),

    # Building A (East/West doors at y=435; North/South corridors at x=323)
    "a_door_east":          (310, 435),
    "a_center":             (323, 435),
    "a_door_west":          (336, 435),
    "a_corridor_c":         (323, 411),
    "a_corridor_b":         (323, 459),
    "a_north_exit":         (323, 398),
    "a_south_exit":         (323, 472),

    # Building C (Corridor East/West entries only; NO mid-north exit)
    "c_east_entry":         (338, 411),
    "c_mid":                (444, 411),
    "c_west_exit":          (564, 411),

    # Central Courtyard & Central B-C Annex (Level 1 divider + Level 2 covered annex)
    "court_left_end":       (420, 435),
    "court_annex_mid":      (444, 435),
    "court_right_end":      (462, 435),
    "court_right_entry":    (568, 435),

    # Building B (Open 1st floor + Level 2 covered skybridge to E)
    "b_east_entry":         (338, 459),
    "b_k_link":             (346, 459),
    "b_mid":                (444, 459),
    "b_bridge_top":         (530, 459),

    # East End of C/B Hub & Building M
    "cm_corridor_c":        (574, 411),
    "cm_corridor_mid":      (574, 435),
    "m_nw_top":             (598, 390),
    "m_nw_junc":            (598, 414),
    "m_entry_nw":           (606, 414),
    "m_center":             (626, 436),
    "m_exit_west":          (646, 444),
    "m_west_exit_corner":   (660, 444),
    "m_east_top":           (660, 390),
    "m_bushes_top":         (680, 390),
    "m_bushes_bot":         (684, 476),

    # Building E, Vida Estudiantil, Innovacion, G & F
    "e_top":                (534, 504),
    "e_mid":                (534, 556),
    "e_bottom":             (534, 654),
    "e_south_turn":         (546, 668),
    "vida_est_north":       (570, 616),
    "vida_est_east":        (588, 668),
    "se_park_south":        (650, 676),
    "eg_alley_top":         (564, 478),
    "eg_corridor_top":      (574, 478),
    "eg_corridor_g":        (564, 509),
    "eg_corridor_gf":       (564, 536),
    "eg_corridor_mid":      (564, 556),
    "eg_corridor_f_south":  (564, 598),
    "g_north_walk":         (612, 478),
    "g_north_door":         (612, 488),
    "g_entry_east":         (582, 509),
    "g_center":             (603, 509),
    "gf_alley_mid":         (603, 536),
    "gf_plaza_top":         (658, 478),
    "gf_plaza_mid":         (663, 536),
    "f_center":             (603, 566),
    "f_south_door":         (616, 594),
    "f_south_walk":         (616, 598),
    "f_south_east":         (696, 596),

    # Building I (Rectoria & Library)
    "i_sw_corner":          (736, 706),
    "i_se_corner":          (820, 706),
    "i_se_top":             (820, 678),
    "i_west_walk":          (736, 623),
    "i_nw_drop":            (742, 548),
    "i_courtyard_mouth":    (774, 623),
    "i_courtyard":          (776, 646),

    # Spine Road Sidewalk & Gates
    "spine_se_low":         (708, 680),
    "spine_gf_south":       (712, 596),
    "spine_i_north":        (724, 548),
    "spine_g_north":        (708, 476),
    "h_west_spine":         (702, 370),
    "h_se_turn":            (698, 390),
    "jj_spine_entry":       (676, 318),
    "spine_o_north":        (652, 140),
    "north_road_t":         (656, 26),
    "gate_second":          (906, 22),

    # Crosswalk, Plaza Chilamates, West Perimeter, J, D, N & Third Access
    "crosswalk_bot":        (319, 394),
    "crosswalk_mid":        (319, 366),
    "crosswalk_top":        (319, 344),
    "chil_east_bot":        (324, 340),
    "chil_east_kiosk":      (324, 314),
    "chil_east_mid":        (324, 260),
    "chil_east_top":        (324, 222),
    "chil_west_bot":        (275, 340),
    "chil_west_kiosk":      (275, 314),
    "chilamates_mid":       (300, 314),
    "chil_west_top":        (275, 242),
    "chilamates_north":     (275, 222),
    "west_ave_p":           (240, 188),
    "west_ave_gate3":       (218, 74),
    "gate_third":           (176, 74),
    "north_road_nw":        (258, 32),
    "jd_cross_turn":        (385, 366),
    "jd_walk_j":            (361, 338),
    "j_entry":              (361, 326),
    "jd_alley_bot":         (385, 338),
    "jd_walk_d":            (410, 338),
    "d_entry":              (410, 324),
    "n_south_stairs":       (456, 338),
    "n_se_corner":          (520, 340),
    "n_west_sw":            (364, 286),
    "n_jd_junction":        (385, 286),
    "n_courtyard":          (430, 286),
    "n_inner_se":           (456, 286),
    "n_west_mid":           (364, 260),
    "n_west_nw":            (364, 222),
    "n_north_stairs":       (416, 222),
    "n_east_ne":            (520, 222),
    "pon_west":             (324, 198),
    "pon_bot_left":         (336, 214),
    "pon_bot_mid":          (416, 214),
    "pon_bot_east":         (530, 214),
    "p_front_west":         (329, 142),
    "p_front_mid":          (456, 142),
    "p_front_east":         (568, 142),
    "p_east_top":           (574, 88),
    "p_behind_lot":         (546, 68),

    # Building O, Jaguar Jungle, Mi Ranchito, Lab Digital FIA, Area de Mesas & Building H
    "o_west_curb_bot":      (554, 214),
    "o_west_mid":           (554, 194),
    "o_west_door":          (568, 194),
    "o_west_top":           (558, 168),
    "o_nw_corner":          (576, 148),
    "o_terrace_top":        (640, 148),
    "o_terrace_mid":        (642, 204),
    "o_terrace_bot":        (638, 260),
    "jj_north_curve":       (628, 288),
    "jj_center":            (628, 315),
    "jj_south_curve":       (638, 338),
    "jj_west_exit":         (558, 324),
    "n_east_annex":         (520, 270),
    "annex_path_mid":       (530, 270),
    "annex_path_top":       (530, 222),
    "mi_ranchito_north":    (555, 272),
    "mi_ranchito_top_door": (555, 282),
    "n_east_walk":          (520, 296),
    "mi_ranchito_west":     (540, 296),
    "mi_ranchito_entry":    (558, 308),
    "n_east_lab":           (520, 328),
    "lab_fia_entry":        (529, 328),
    "mesas_top_right":      (554, 340),
    "mesas_left_bot":       (520, 392),
    "mesas_corridor":       (554, 366),
    "mesas_pad":            (536, 366),
    "mesas_south_turn":     (554, 390),
    "mesas_cm_corner":      (574, 390),
    "h_north_entry":        (640, 354),
    "h_south_door":         (618, 384),
    "h_south_walk":         (618, 390),

    # Sports Concourse, Jaguar Center, Building L, Fisioterapia, Jaguar Gym & East Sports Complex
    "sports_concourse_w":   (724, 338),
    "sports_concourse_m":   (918, 338),
    "sports_north_park":    (822, 36),
    "sports_baseball_ent":  (918, 318),
    "sports_soccer_north":  (918, 368),
    "soccer_south_west":    (805, 548),
    "soccer_south_west_in": (805, 526),
    "jc_top_left":          (858, 548),
    "jc_entry":             (858, 576),
    "jc_top_right":         (936, 548),
    "jc_entry_right":       (936, 576),
    "jc_ne_hub":            (960, 548),
    "soccer_south_east_in": (960, 522),
    "jc_l_wash":            (960, 560),
    "washrooms_entry":      (978, 560),
    "jc_l_upper":           (960, 598),
    "l_upper_entry":        (978, 598),
    "jc_west_door":         (952, 612),
    "jc_l_mid":             (960, 612),
    "l_entry":              (989, 612),
    "jc_bot_left":          (866, 678),
    "jc_bot_left_door":     (866, 670),
    "jc_bot_right":         (936, 678),
    "jc_bot_right_door":    (936, 670),
    "jc_l_ft":              (960, 678),
    "ft_entry":             (978, 679),
    "gym_park_mid":         (944, 706),
    "gym_top_west":         (960, 698),
    "gym_top_door_junc":    (969, 698),
    "gym_entry":            (969, 706),
    "east_corridor_top":    (1006, 542),
    "east_corridor_l":      (1006, 612),
    "east_corridor_courts": (1006, 647),
    "east_corridor_ft":     (1006, 679),
    "east_corridor_gym":    (1006, 698),
    "east_corridor_gap":    (1006, 774),
    "east_corridor_lunch":  (1006, 836),
    "bodega_north_mid":     (1046, 647),
    "courts_east_junc":     (1080, 647),
    "kiosk_sport_entry":    (1094, 644),
    "bodega_south_mid":     (1046, 679),
    "east_alley_top":       (1080, 679),
    "east_alley_ma":        (1080, 697),
    "east_alley_mp":        (1080, 732),
    "east_alley_bot":       (1080, 774),
    "comedor_entry":        (1086, 804),
}


# Ground-truth real GPS overrides directly from coordenadas.txt for key outdoor walkway anchors
REAL_GPS_OVERRIDES: Dict[str, Tuple[float, float]] = {
    "banpro_entry":         (12.108585, -86.256576),
    "a_front_plaza":        (12.108560, -86.256574),
    "a_door_east":          (12.108543, -86.256496),
    "a_center":             (12.108503, -86.256678),
    "a_north_exit":         (12.108321, -86.256638),
    "crosswalk_bot":        (12.108293, -86.256649),
    "crosswalk_mid":        (12.108248, -86.256610),
    "crosswalk_top":        (12.108248, -86.256610),
    "chilamates_mid":       (12.108027, -86.256705),
    "chil_east_top":        (12.107922, -86.256725),
    "j_entry":              (12.108145, -86.256782),
    "d_entry":              (12.108128, -86.256945),
    "n_west_mid":           (12.107741, -86.256842),
    "n_north_stairs":       (12.107742, -86.257105),
    "pon_bot_left":         (12.107696, -86.256859),
    "pon_bot_mid":          (12.107742, -86.257105),
    "pon_bot_east":         (12.107748, -86.257338),
    "p_front_west":         (12.107584, -86.256779),
    "p_front_mid":          (12.107455, -86.256981),
    "p_front_east":         (12.107453, -86.257413),
    "o_west_door":          (12.107478, -86.257555),
    "o_terrace_mid":        (12.107664, -86.257761),
    "jj_center":            (12.108073, -86.257787),
    "mi_ranchito_entry":    (12.108058, -86.257323),
    "h_north_entry":        (12.108156, -86.257782),
    "h_south_door":         (12.108253, -86.257529),
    "m_center":             (12.108439, -86.257594),
    "m_entry_nw":           (12.108525, -86.257453),
    "c_east_entry":         (12.108528, -86.256743),
    "c_mid":                (12.108446, -86.257021),
    "c_west_exit":          (12.108511, -86.257316),
    "b_east_entry":         (12.108563, -86.256783),
    "b_mid":                (12.108568, -86.256991),
    "b_bridge_top":         (12.108590, -86.257332),
    "g_center":             (12.108695, -86.257600),
    "g_entry_east":         (12.108630, -86.257479),
    "f_center":             (12.108938, -86.257431),
    "f_south_door":         (12.108908, -86.257390),
    "vida_est_north":       (12.109081, -86.257416),
    "e_top":                (12.108805, -86.257210),
    "e_mid":                (12.109062, -86.257375),
    "e_bottom":             (12.109346, -86.257217),
    "i_west_walk":          (12.109096, -86.257858),
    "i_courtyard":          (12.109237, -86.258051),
    "i_sw_corner":          (12.109467, -86.257868),
    "i_se_corner":          (12.109547, -86.257996),
    "sports_concourse_w":   (12.108100, -86.257939),
    "sports_soccer_north":  (12.108181, -86.258504),
    "jc_entry":             (12.109111, -86.258514),
    "jc_west_door":         (12.109111, -86.258514),
    "l_entry":              (12.109123, -86.258504),
    "ft_entry":             (12.109303, -86.258511),
    "gym_entry":            (12.109309, -86.258508),
    "east_alley_ma":        (12.109284, -86.258871),
    "east_alley_mp":        (12.109279, -86.258881),
}


# Walkable Pedestrian Segments (synchronized 1:1 with campusWalkwaysLayer.js)
# Tuple format: (fromId, toId, walkwayType, isAccessible)
WALKWAY_SEGMENTS_SPEC: List[Tuple[str, str, str, bool]] = [
    # Main Entrance & South Ring Sidewalk
    ("ent_gate", "ent_corner", "ground", True),
    ("ent_corner", "south_walk_1", "ground", True),
    ("south_walk_1", "south_walk_2", "ground", True),
    ("south_walk_2", "south_walk_3", "ground", True),
    ("south_walk_3", "south_se_turn", "ground", True),

    # Main Entrance -> Straight toward K, Banpro Bank & Building A
    ("ent_corner", "west_side_low", "ground", True),
    ("west_side_low", "west_side_k_south", "ground", True),
    ("west_side_k_south", "west_side_bank", "ground", True),
    ("west_side_bank", "banpro_entry", "ground", True),
    ("west_side_bank", "west_side_k_north", "ground", True),
    ("west_side_k_north", "a_front_plaza", "ground", True),
    ("a_front_plaza", "a_door_east", "ground", True),

    # Building K & Plaza Central Ruben Dario
    ("west_side_k_south", "k_south_walk", "ground", True),
    ("k_south_walk", "k_se_corner", "ground", True),
    ("k_se_corner", "k_door_east", "ground", True),
    ("k_se_corner", "plaza_south_mid", "ground", True),
    ("plaza_south_mid", "plaza_south_e", "ground", True),
    ("plaza_south_e", "e_mid", "ground", True),
    ("west_side_k_north", "k_west_apron", "ground", True),
    ("k_west_apron", "a_south_exit", "ground", True),
    ("k_west_apron", "k_north_walk", "ground", True),
    ("k_north_walk", "b_k_link", "ground", True),
    ("k_north_walk", "plaza_north_mid", "ground", True),
    ("plaza_north_mid", "b_mid", "ground", True),
    ("plaza_north_mid", "plaza_north_east", "ground", True),
    ("plaza_north_east", "b_bridge_top", "ground", True),
    ("plaza_north_east", "eg_alley_top", "ground", True),
    ("eg_alley_top", "eg_corridor_top", "ground", True),

    # Building A: East/West Door Pass-Through + North/South Corridors
    ("a_door_east", "a_center", "indoor", True),
    ("a_center", "a_door_west", "indoor", True),
    ("a_center", "a_corridor_c", "indoor", True),
    ("a_center", "a_corridor_b", "indoor", True),
    ("a_corridor_c", "a_north_exit", "indoor", True),
    ("a_corridor_b", "a_south_exit", "indoor", True),

    # Building C: Full East-West Corridor (NO mid-north exit — blocked wall respected!)
    ("a_corridor_c", "c_east_entry", "indoor", True),
    ("c_east_entry", "c_mid", "indoor", True),
    ("c_mid", "c_west_exit", "indoor", True),
    ("c_west_exit", "cm_corridor_c", "ground", True),

    # Central Courtyard & Central B-C Annex (Level 2 covered bridge)
    ("a_door_west", "court_left_end", "ground", True),
    ("c_mid", "court_annex_mid", "level2", True),
    ("court_annex_mid", "b_mid", "level2", True),
    ("court_right_end", "court_right_entry", "ground", True),
    ("court_right_entry", "cm_corridor_mid", "ground", True),

    # Building B: Open 1st-Floor Hallway + 2nd-Floor Covered Skybridge to E
    ("a_corridor_b", "b_east_entry", "indoor", True),
    ("b_east_entry", "b_k_link", "indoor", True),
    ("b_k_link", "b_mid", "indoor", True),
    ("b_mid", "b_bridge_top", "indoor", True),
    ("b_bridge_top", "e_top", "level2", True),

    # Right End of C/B Hub & Building M (respecting East Stairwell barrier)
    ("cm_corridor_c", "cm_corridor_mid", "ground", True),
    ("cm_corridor_mid", "eg_corridor_top", "ground", True),
    ("cm_corridor_c", "m_nw_junc", "ground", True),
    ("m_nw_top", "m_nw_junc", "ground", True),
    ("m_nw_junc", "m_entry_nw", "ground", True),
    ("m_entry_nw", "m_center", "indoor", True),
    ("m_center", "m_exit_west", "indoor", True),
    ("m_exit_west", "m_west_exit_corner", "ground", True),
    ("m_west_exit_corner", "m_east_top", "ground", True),
    ("m_bushes_top", "m_bushes_bot", "ground", True),

    # Building E, Vida Estudiantil, G, F & SE Parking
    ("e_top", "e_mid", "indoor", True),
    ("e_mid", "e_bottom", "indoor", True),
    ("e_mid", "eg_corridor_mid", "ground", True),
    ("e_bottom", "e_south_turn", "ground", True),
    ("e_south_turn", "vida_est_east", "ground", True),
    ("vida_est_east", "se_park_south", "ground", True),
    ("se_park_south", "spine_se_low", "ground", True),
    ("eg_corridor_top", "g_north_walk", "ground", True),
    ("g_north_walk", "g_north_door", "ground", True),
    ("g_north_walk", "gf_plaza_top", "ground", True),
    ("gf_plaza_top", "m_bushes_bot", "ground", True),
    ("m_bushes_bot", "spine_g_north", "ground", True),
    ("gf_plaza_top", "gf_plaza_mid", "ground", True),
    ("eg_alley_top", "eg_corridor_g", "ground", True),
    ("eg_corridor_g", "g_entry_east", "ground", True),
    ("g_entry_east", "g_center", "indoor", True),
    ("eg_corridor_g", "eg_corridor_gf", "ground", True),
    ("eg_corridor_gf", "gf_alley_mid", "ground", True),
    ("gf_alley_mid", "gf_plaza_mid", "ground", True),
    ("eg_corridor_gf", "eg_corridor_mid", "ground", True),
    ("eg_corridor_mid", "eg_corridor_f_south", "ground", True),
    ("eg_corridor_f_south", "vida_est_north", "ground", True),
    ("eg_corridor_f_south", "f_south_walk", "ground", True),
    ("f_south_walk", "f_south_door", "ground", True),
    ("f_south_door", "f_center", "indoor", True),
    ("f_south_walk", "f_south_east", "ground", True),
    ("f_south_east", "spine_gf_south", "ground", True),
    ("gf_plaza_mid", "spine_gf_south", "ground", True),

    # Building I Perimeter & Clean Courtyard Entrance
    ("spine_se_low", "south_se_turn", "ground", True),
    ("south_se_turn", "i_sw_corner", "ground", True),
    ("i_sw_corner", "i_west_walk", "ground", True),
    ("i_west_walk", "i_courtyard_mouth", "ground", True),
    ("i_courtyard_mouth", "i_courtyard", "ground", True),
    ("i_west_walk", "i_nw_drop", "ground", True),
    ("i_sw_corner", "i_se_corner", "ground", True),
    ("i_se_corner", "i_se_top", "ground", True),
    ("i_se_top", "jc_bot_left", "ground", True),
    ("i_se_corner", "gym_park_mid", "ground", True),

    # Spine Road Continuous Sidewalk
    ("spine_se_low", "spine_gf_south", "ground", True),
    ("spine_gf_south", "spine_i_north", "ground", True),
    ("spine_i_north", "spine_g_north", "ground", True),
    ("spine_g_north", "h_west_spine", "ground", True),
    ("h_west_spine", "jj_spine_entry", "ground", True),
    ("h_west_spine", "h_se_turn", "ground", True),
    ("o_terrace_top", "spine_o_north", "ground", True),
    ("spine_o_north", "north_road_t", "ground", True),
    ("north_road_t", "gate_second", "ground", True),

    # Crosswalk, Plaza Chilamates, West Perimeter & Third Access
    ("a_north_exit", "crosswalk_bot", "ground", True),
    ("crosswalk_bot", "crosswalk_mid", "crosswalk", True),
    ("crosswalk_mid", "crosswalk_top", "crosswalk", True),
    ("crosswalk_mid", "jd_cross_turn", "ground", True),
    ("jd_cross_turn", "jd_alley_bot", "ground", True),
    ("crosswalk_top", "chil_east_bot", "ground", True),
    ("chil_east_bot", "chil_east_kiosk", "ground", True),
    ("chil_east_kiosk", "chil_east_mid", "ground", True),
    ("chil_east_mid", "chil_east_top", "ground", True),
    ("chil_east_top", "pon_west", "ground", True),
    ("chil_east_bot", "chil_west_bot", "ground", True),
    ("chil_west_bot", "chil_west_kiosk", "ground", True),
    ("chil_west_kiosk", "chilamates_mid", "ground", True),
    ("chilamates_mid", "chil_east_kiosk", "ground", True),
    ("chil_west_kiosk", "chil_west_top", "ground", True),
    ("chil_west_top", "chilamates_north", "ground", True),
    ("chilamates_north", "chil_east_top", "ground", True),
    ("chilamates_north", "west_ave_p", "ground", True),
    ("west_ave_p", "pon_west", "ground", True),
    ("west_ave_p", "west_ave_gate3", "ground", True),
    ("west_ave_gate3", "gate_third", "ground", True),
    ("west_ave_gate3", "north_road_nw", "ground", True),
    ("north_road_nw", "north_road_t", "ground", True),

    # J, D, Alley between J & D -> Building N Perimeter -> Building P
    ("crosswalk_top", "jd_walk_j", "ground", True),
    ("jd_walk_j", "j_entry", "ground", True),
    ("jd_walk_j", "jd_alley_bot", "ground", True),
    ("jd_alley_bot", "jd_walk_d", "ground", True),
    ("jd_alley_bot", "n_jd_junction", "ground", True),
    ("jd_walk_d", "d_entry", "ground", True),
    ("jd_walk_d", "n_south_stairs", "ground", True),
    ("n_south_stairs", "n_inner_se", "ground", True),
    ("n_south_stairs", "n_se_corner", "ground", True),
    ("n_inner_se", "n_courtyard", "ground", True),
    ("n_courtyard", "n_jd_junction", "ground", True),
    ("n_jd_junction", "n_west_sw", "ground", True),
    ("n_west_sw", "n_west_mid", "ground", True),
    ("n_west_mid", "chil_east_mid", "ground", True),
    ("n_west_mid", "n_west_nw", "ground", True),
    ("n_west_nw", "chil_east_top", "ground", True),
    ("n_west_nw", "n_north_stairs", "ground", True),
    # Stairs between Building N and Building P (isAccessible = False!)
    ("n_north_stairs", "pon_bot_mid", "stairs", False),
    ("n_north_stairs", "n_east_ne", "ground", True),
    ("n_east_ne", "annex_path_top", "ground", True),
    ("chil_east_top", "pon_bot_left", "ramp", True),
    ("pon_bot_left", "pon_bot_mid", "ground", True),
    ("pon_bot_mid", "pon_bot_east", "ground", True),
    ("pon_bot_east", "annex_path_top", "ramp", True),
    ("pon_bot_east", "o_west_curb_bot", "ramp", True),
    ("pon_west", "p_front_west", "ground", True),
    ("p_front_west", "p_front_mid", "ground", True),
    ("p_front_mid", "p_front_east", "ground", True),
    ("p_front_east", "p_east_top", "ground", True),
    ("p_east_top", "p_behind_lot", "ground", True),

    # Building O, Jaguar Jungle, Mi Ranchito, Lab Digital FIA, Area de Mesas & Building H
    ("o_west_curb_bot", "o_west_mid", "ground", True),
    ("o_west_mid", "o_west_door", "ground", True),
    ("o_west_mid", "o_west_top", "ground", True),
    ("o_west_top", "o_nw_corner", "ground", True),
    ("p_front_east", "o_nw_corner", "ground", True),
    ("o_nw_corner", "o_terrace_top", "ground", True),
    ("o_terrace_top", "o_terrace_mid", "ground", True),
    ("o_terrace_mid", "o_terrace_bot", "ground", True),
    ("o_terrace_bot", "jj_north_curve", "ground", True),
    ("jj_north_curve", "jj_center", "ground", True),
    ("jj_center", "jj_south_curve", "ground", True),
    ("jj_south_curve", "h_north_entry", "ground", True),
    ("jj_spine_entry", "jj_center", "ground", True),
    ("jj_center", "jj_west_exit", "ground", True),
    ("jj_west_exit", "mi_ranchito_entry", "ground", True),
    ("n_east_ne", "n_east_annex", "ground", True),
    ("n_east_annex", "annex_path_mid", "ground", True),
    ("annex_path_mid", "annex_path_top", "ground", True),
    ("annex_path_mid", "mi_ranchito_north", "ground", True),
    ("mi_ranchito_north", "mi_ranchito_top_door", "ground", True),
    ("n_east_annex", "n_east_walk", "ground", True),
    ("n_east_walk", "mi_ranchito_west", "ground", True),
    ("mi_ranchito_west", "mi_ranchito_entry", "indoor", True),
    ("mi_ranchito_top_door", "mi_ranchito_entry", "indoor", True),
    ("n_east_walk", "n_east_lab", "ground", True),
    ("n_east_lab", "lab_fia_entry", "ground", True),
    ("n_east_lab", "n_se_corner", "ground", True),
    ("n_se_corner", "mesas_top_right", "ground", True),
    ("n_se_corner", "mesas_left_bot", "ground", True),
    ("mesas_left_bot", "mesas_south_turn", "ground", True),
    ("jj_west_exit", "mesas_top_right", "ground", True),
    ("mesas_top_right", "mesas_corridor", "ground", True),
    ("mesas_corridor", "mesas_pad", "ground", True),
    ("mesas_corridor", "mesas_south_turn", "ground", True),
    ("mesas_south_turn", "mesas_cm_corner", "ground", True),
    ("mesas_cm_corner", "cm_corridor_c", "ground", True),
    ("mesas_cm_corner", "m_nw_top", "ground", True),
    ("m_nw_top", "h_south_walk", "ground", True),
    ("h_south_walk", "h_south_door", "ground", True),
    ("h_south_walk", "m_east_top", "ground", True),
    ("m_east_top", "m_bushes_top", "ground", True),
    ("m_bushes_top", "h_se_turn", "ground", True),

    # Sports Concourse, Jaguar Center, Building L, Fisioterapia, Jaguar Gym & East Sports Complex
    ("jj_spine_entry", "sports_concourse_w", "ground", True),
    ("sports_concourse_w", "sports_concourse_m", "ground", True),
    ("sports_concourse_m", "sports_baseball_ent", "ground", True),
    ("sports_concourse_m", "sports_soccer_north", "ground", True),
    ("north_road_t", "sports_north_park", "ground", True),
    ("sports_north_park", "gate_second", "ground", True),
    ("sports_concourse_w", "spine_i_north", "ground", True),

    # Promenade South of Soccer Field -> Building I, Soccer & Jaguar Center
    ("spine_i_north", "i_nw_drop", "ground", True),
    ("i_nw_drop", "soccer_south_west", "ground", True),
    ("soccer_south_west", "soccer_south_west_in", "ground", True),
    ("soccer_south_west", "jc_top_left", "ground", True),
    ("jc_top_left", "jc_entry", "ground", True),
    ("jc_top_left", "jc_top_right", "ground", True),
    ("jc_top_right", "jc_entry_right", "ground", True),
    ("jc_top_right", "jc_ne_hub", "ground", True),
    ("jc_ne_hub", "soccer_south_east_in", "ground", True),
    ("jc_ne_hub", "east_corridor_top", "ground", True),

    # Corridor between Jaguar Center & Building L / Fisioterapia
    ("jc_ne_hub", "jc_l_wash", "ground", True),
    ("jc_l_wash", "washrooms_entry", "ground", True),
    ("jc_l_wash", "jc_l_upper", "ground", True),
    ("jc_l_upper", "l_upper_entry", "ground", True),
    ("jc_l_upper", "jc_l_mid", "ground", True),
    ("jc_west_door", "jc_l_mid", "ground", True),
    ("jc_l_mid", "l_entry", "ground", True),
    ("l_entry", "east_corridor_l", "ground", True),
    ("jc_l_mid", "jc_l_ft", "ground", True),
    ("jc_l_ft", "ft_entry", "ground", True),
    ("ft_entry", "east_corridor_ft", "ground", True),
    ("jc_l_ft", "gym_top_west", "ground", True),

    # Walkways South of Jaguar Center -> Jaguar Gym & East Corridor
    ("jc_bot_left", "jc_bot_left_door", "ground", True),
    ("jc_bot_left", "jc_bot_right", "ground", True),
    ("jc_bot_right", "jc_bot_right_door", "ground", True),
    ("jc_bot_right", "jc_l_ft", "ground", True),
    ("gym_park_mid", "gym_top_west", "ground", True),
    ("gym_top_west", "gym_top_door_junc", "ground", True),
    ("gym_top_door_junc", "gym_entry", "ground", True),
    ("gym_top_door_junc", "east_corridor_gym", "ground", True),

    # East Corridor & Sports Alley
    ("east_corridor_top", "east_corridor_l", "ground", True),
    ("east_corridor_l", "east_corridor_courts", "ground", True),
    ("east_corridor_courts", "east_corridor_ft", "ground", True),
    ("east_corridor_ft", "east_corridor_gym", "ground", True),
    ("east_corridor_gym", "east_corridor_gap", "ground", True),
    ("east_corridor_gap", "east_corridor_lunch", "ground", True),
    ("east_corridor_gap", "east_alley_bot", "ground", True),
    ("east_corridor_courts", "bodega_north_mid", "ground", True),
    ("bodega_north_mid", "courts_east_junc", "ground", True),
    ("courts_east_junc", "kiosk_sport_entry", "ground", True),
    ("east_corridor_ft", "bodega_south_mid", "ground", True),
    ("bodega_south_mid", "east_alley_top", "ground", True),
    ("courts_east_junc", "east_alley_top", "ground", True),
    ("east_alley_top", "east_alley_ma", "ground", True),
    ("east_alley_ma", "east_alley_mp", "ground", True),
    ("east_alley_mp", "east_alley_bot", "ground", True),
    ("east_alley_bot", "comedor_entry", "ground", True),
]


# Visual landmarks & portal metadata for human-friendly turn-by-turn directions
# Format: nodeId -> (spaLabel, engLabel, portalKind, buildingId)
WALKWAY_LANDMARKS: Dict[str, Tuple[str, str, Optional[str], Optional[str]]] = {
    "ent_gate":             ("el Acceso Principal (Caseta Sur)", "the Main Entrance (South Gate)", "gate", "mainParking"),
    "ent_corner":           ("la esquina de la acera principal", "the main sidewalk corner", "junction", "mainParking"),
    "banpro_entry":         ("Banpro", "Banpro bank", "landmark", "buildingK"),
    "west_side_bank":       ("el sector de Banpro", "the Banpro bank area", "landmark", "buildingK"),
    "west_side_k_south":    ("la esquina de la Cafetería (Edificio K)", "the Central Cafeteria (Building K) corner", "landmark", "buildingK"),
    "k_door_east":          ("la Cafetería Central (Edificio K)", "the Central Cafeteria (Building K)", "door", "buildingK"),
    "plaza_south_mid":      ("la Plaza Central Rubén Darío", "Rubén Darío Central Plaza", "plaza", None),
    "plaza_north_mid":      ("la Plaza Central junto al Edificio B", "the Central Plaza by Building B", "plaza", "buildingB"),
    "a_front_plaza":        ("la entrada exterior del Edificio A (cajeros BAC/LAFISE)", "Building A front entrance (ATMs)", "plaza", "buildingA"),
    "a_door_east":          ("la puerta principal del Edificio A", "Building A main entrance", "door", "buildingA"),
    "a_center":             ("el vestíbulo del Edificio A (Atención al Estudiante)", "Building A central lobby (Student Services)", "corridor", "buildingA"),
    "a_door_west":          ("la salida al patio del Edificio A", "Building A courtyard exit", "door", "buildingA"),
    "a_corridor_c":         ("el pasillo de conexión hacia el Edificio C", "the connecting corridor to Building C", "corridor", "buildingA"),
    "a_corridor_b":         ("el pasillo de conexión hacia el Edificio B", "the connecting corridor to Building B", "corridor", "buildingA"),
    "a_north_exit":         ("la salida del Edificio A hacia el paso peatonal", "Building A exit toward the crosswalk", "door", "buildingA"),
    "a_south_exit":         ("la salida del Edificio A hacia el Edificio K", "Building A exit toward Building K", "door", "buildingA"),
    "c_east_entry":         ("la entrada del Edificio C (Auditorio C-101)", "Building C entrance (Auditorium C-101)", "door", "buildingC"),
    "c_mid":                ("el pasillo central del Edificio C (Caja UAM)", "Building C central corridor (Cashier Office)", "corridor", "buildingC"),
    "c_west_exit":          ("la salida del Edificio C hacia el Edificio M", "Building C exit toward Building M", "door", "buildingC"),
    "court_annex_mid":      ("el puente techado entre los Edificios B y C (2.º piso)", "the 2nd-floor covered bridge between Buildings B and C", "skybridge", None),
    "b_east_entry":         ("la entrada del Edificio B (Farmacia)", "Building B entrance (Pharmacy)", "door", "buildingB"),
    "b_mid":                ("el pasillo central del Edificio B", "Building B central hallway", "corridor", "buildingB"),
    "b_bridge_top":         ("el puente techado del 2.º piso hacia el Edificio E", "the 2nd-floor covered skybridge toward Building E", "skybridge", "buildingB"),
    "m_entry_nw":           ("la entrada principal del Edificio M", "Building M main entrance", "door", "buildingM"),
    "m_center":             ("el Edificio M (Auditorios y Posgrados)", "Building M (Auditoriums & Graduate Programs)", "corridor", "buildingM"),
    "m_exit_west":          ("la salida lateral del Edificio M", "Building M side exit", "door", "buildingM"),
    "e_top":                ("el acceso superior del Edificio E (puente desde B)", "Building E upper skybridge entrance", "skybridge", "buildingE"),
    "e_mid":                ("el Edificio E (Facultad de Medicina y Clínicas)", "Building E (Faculty of Medicine & Clinics)", "corridor", "buildingE"),
    "e_bottom":             ("el sector de Decanatura de Medicina (Edificio E)", "the Medicine Deanery area (Building E)", "door", "buildingE"),
    "vida_est_north":       ("Vida Estudiantil (DVE)", "Student Life Office (DVE)", "landmark", "buildingE"),
    "g_north_door":         ("la entrada al Edificio G (Derecho)", "Building G entrance (Law School)", "door", "buildingG"),
    "g_entry_east":         ("la entrada lateral del Edificio G", "Building G side entrance", "door", "buildingG"),
    "g_center":             ("el Edificio G (Derecho y Auditorio Central)", "Building G (Law & Central Auditorium)", "corridor", "buildingG"),
    "f_south_door":         ("la entrada del Edificio F (FCAE / FMDCC)", "Building F entrance (Business & Marketing)", "door", "buildingF"),
    "f_center":             ("el Edificio F (FCAE, FMDCC y Posgrados)", "Building F (Business & Graduate Studies)", "corridor", "buildingF"),
    "i_sw_corner":          ("la esquina del Edificio I (acera hacia Biblioteca)", "the Building I corner (sidewalk toward Library)", "plaza", "buildingI"),
    "i_west_walk":          ("la rampa de acceso al Edificio I (Rectoría)", "the accessible ramp to Building I (Rectorate)", "ramp", "buildingI"),
    "i_courtyard_mouth":    ("la entrada al patio interno del Edificio I", "Building I inner courtyard entrance", "door", "buildingI"),
    "i_courtyard":          ("el Edificio I (Rectoría y Biblioteca Central)", "Building I (Rectorate & Central Library)", "plaza", "buildingI"),
    "i_se_corner":          ("la entrada de la Biblioteca Pablo Antonio Cuadra", "Pablo Antonio Cuadra Central Library entrance", "door", "buildingI"),
    "crosswalk_bot":        ("el inicio del paso peatonal (cebra)", "the start of the pedestrian crosswalk", "crosswalk", None),
    "crosswalk_mid":        ("el paso peatonal (cebra)", "the pedestrian crosswalk", "crosswalk", None),
    "crosswalk_top":        ("el cruce peatonal frente a Plaza Chilamates", "the crosswalk in front of Chilamates Plaza", "crosswalk", "chilamatesPlaza"),
    "chilamates_mid":       ("Plaza Chilamates (Kioskos y Fast Point)", "Chilamates Plaza (Kiosks & Fast Point)", "plaza", "chilamatesPlaza"),
    "chil_east_top":        ("la salida de Plaza Chilamates hacia el Edificio P", "Chilamates Plaza exit toward Building P", "plaza", "chilamatesPlaza"),
    "gate_third":           ("el Tercer Acceso (Portón Copérnico)", "Third Access (Copernicus Gate)", "gate", "northGate"),
    "gate_second":          ("el Segundo Acceso (Camino Estadio Jaguar)", "Second Access (Jaguar Stadium Road)", "gate", "northeastGate"),
    "j_entry":              ("la entrada del Edificio J (Laboratorios de Odontología)", "Building J entrance (Dentistry Labs)", "door", "buildingJ"),
    "d_entry":              ("la entrada del Edificio D (Odontología Digital)", "Building D entrance (Digital Dentistry)", "door", "buildingD"),
    "n_courtyard":          ("la recepción del Edificio N (Clínicas Odontológicas)", "Building N reception (Dental Clinics)", "door", "buildingN"),
    "n_west_mid":           ("los sanitarios junto al Edificio N y Plaza Chilamates", "the restrooms beside Building N and Chilamates Plaza", "landmark", "buildingN"),
    "n_north_stairs":       ("las gradas entre el Edificio N y el Edificio P", "the stairs between Building N and Building P", "stairs", "buildingN"),
    "pon_bot_left":         ("el acceso sin gradas hacia el parqueo del Edificio P", "the step-free walkway toward Building P parking", "ramp", "buildingP"),
    "pon_bot_mid":          ("el andén frente al Edificio P", "the walkway in front of Building P", "plaza", "buildingP"),
    "pon_bot_east":         ("la rampa entre el Edificio O y el Edificio P", "the ramp between Building O and Building P", "ramp", "buildingO"),
    "p_front_west":         ("el acceso oeste del Edificio P (Copérnico)", "Building P west entrance (Copernicus)", "door", "buildingP"),
    "p_front_mid":          ("el frente del Edificio P (Copérnico)", "the front of Building P (Copernicus)", "door", "buildingP"),
    "p_front_east":         ("el acceso del Edificio P junto al Edificio O", "Building P entrance near Building O", "door", "buildingP"),
    "o_west_door":          ("la entrada principal del Edificio O (Ingeniería - FIA)", "Building O main entrance (Engineering - FIA)", "door", "buildingO"),
    "o_terrace_mid":        ("la terraza del Edificio O (FIA)", "Building O terrace (FIA)", "corridor", "buildingO"),
    "jj_center":            ("Jaguar Jungle (sendero arbolado)", "Jaguar Jungle (shaded garden path)", "plaza", "jaguarJungle"),
    "jj_spine_entry":       ("la salida de Jaguar Jungle hacia la vía deportiva", "Jaguar Jungle exit toward the sports road", "plaza", "jaguarJungle"),
    "mi_ranchito_entry":    ("Mi Ranchito (pabellón de comidas y descanso)", "Mi Ranchito (dining & rest pavilion)", "door", "miRanchito"),
    "lab_fia_entry":        ("el Lab Digital FIA", "Digital FIA Laboratory", "door", "labDigitalFia"),
    "mesas_pad":            ("el Área de Mesas", "the Outdoor Tables Area", "plaza", "areaDeMesas"),
    "h_north_entry":        ("la entrada del Edificio H (desde Jaguar Jungle)", "Building H entrance (from Jaguar Jungle)", "door", "buildingH"),
    "h_south_door":         ("la entrada del Edificio H (Laboratorios de Medicina)", "Building H entrance (Medical Labs)", "door", "buildingH"),
    "sports_concourse_w":   ("el Kiosko Jaguarcito y corredor deportivo", "Jaguarcito Kiosk and sports concourse", "landmark", "sportsZone"),
    "sports_concourse_m":   ("los Campos Deportivos (Estadio y Cancha)", "the Sports Fields (Stadium & Soccer Field)", "plaza", "sportsZone"),
    "sports_baseball_ent":  ("el Estadio de Béisbol Jaguar", "Jaguar Baseball Stadium", "door", "sportsZone"),
    "sports_soccer_north":  ("la Cancha de Fútbol", "the Soccer Field", "door", "sportsZone"),
    "jc_entry":             ("la entrada del Complejo Jaguar Center", "Jaguar Center main entrance", "door", "jaguarCenter"),
    "jc_entry_right":       ("el acceso lateral del Complejo Jaguar Center", "Jaguar Center side entrance", "door", "jaguarCenter"),
    "jc_west_door":         ("el acceso entre Jaguar Center y el Edificio L", "the passage between Jaguar Center and Building L", "door", "jaguarCenter"),
    "l_entry":              ("el Edificio L (Cultura y Música)", "Building L (Culture & Music)", "door", "buildingL"),
    "ft_entry":             ("el Edificio de Fisioterapia", "the Physiotherapy Building", "door", "physiotherapy"),
    "gym_entry":            ("Jaguar Gym", "Jaguar Gym", "door", "jaguarGym"),
    "kiosk_sport_entry":    ("el Kiosko Jaguar Sport", "Jaguar Sport Kiosk", "landmark", "jaguarCenter"),
    "east_alley_ma":        ("el Salón de Artes Marciales", "the Martial Arts Hall", "door", "jaguarCenter"),
    "east_alley_mp":        ("el Salón de Usos Múltiples y Psicología Deportiva", "the Multipurpose Hall & Sports Psychology", "door", "jaguarCenter"),
    "comedor_entry":        ("el Comedor de Colaboradores", "the Staff Dining Hall", "door", "jaguarCenter"),
}


# Mapping from Macro Building/Zone IDs -> Primary Walkable Micro-Node (synced with campusWalkwaysLayer.js)
MACRO_TO_MICRO_NODE: Dict[str, str] = {
    "mainParking":     "ent_gate",
    "buildingK":       "k_door_east",
    "chilamatesPlaza": "chilamates_mid",
    "buildingA":       "a_center",
    "buildingB":       "b_mid",
    "buildingC":       "c_mid",
    "buildingD":       "d_entry",
    "buildingJ":       "j_entry",
    "buildingN":       "n_courtyard",
    "buildingO":       "o_west_door",
    "buildingP":       "p_front_mid",
    "buildingM":       "m_center",
    "buildingG":       "g_center",
    "buildingF":       "f_center",
    "buildingE":       "e_mid",
    "buildingI":       "i_courtyard",
    "buildingH":       "h_south_door",
    "sportsZone":      "sports_concourse_m",
    "jaguarCenter":    "jc_entry",
    "jaguarGym":       "gym_entry",
    "physiotherapy":   "ft_entry",
    "buildingL":       "l_entry",
    "jaguarJungle":    "jj_center",
    "miRanchito":      "mi_ranchito_entry",
    "labDigitalFia":   "lab_fia_entry",
    "areaDeMesas":     "mesas_pad",
    "northGate":       "gate_third",
    "northeastGate":   "gate_second",
}


# Multi-portal entrances per building for optimal outdoor<->indoor handoff
BUILDING_PORTALS: Dict[str, List[str]] = {
    "buildingA":       ["a_door_east", "a_center", "a_north_exit", "a_south_exit"],
    "buildingB":       ["b_east_entry", "b_mid", "b_bridge_top"],
    "buildingC":       ["c_east_entry", "c_mid", "c_west_exit"],
    "buildingD":       ["d_entry"],
    "buildingE":       ["e_top", "e_mid", "e_bottom", "vida_est_north"],
    "buildingF":       ["f_south_door", "f_center"],
    "buildingG":       ["g_north_door", "g_entry_east", "g_center"],
    "buildingH":       ["h_south_door", "h_north_entry"],
    "buildingI":       ["i_west_walk", "i_courtyard", "i_se_corner", "i_sw_corner"],
    "buildingJ":       ["j_entry"],
    "buildingK":       ["k_door_east", "west_side_k_south", "k_north_walk"],
    "buildingL":       ["l_entry", "l_upper_entry"],
    "buildingM":       ["m_entry_nw", "m_center", "m_exit_west"],
    "buildingN":       ["n_courtyard", "n_west_mid", "n_south_stairs"],
    "buildingO":       ["o_west_door", "o_terrace_mid", "o_nw_corner"],
    "buildingP":       ["p_front_west", "p_front_mid", "p_front_east"],
    "jaguarCenter":    ["jc_entry", "jc_entry_right", "jc_west_door", "jc_bot_left_door"],
    "jaguarGym":       ["gym_entry"],
    "physiotherapy":   ["ft_entry"],
    "sportsZone":      ["sports_concourse_w", "sports_concourse_m", "sports_soccer_north"],
    "chilamatesPlaza": ["chilamates_mid", "crosswalk_top", "chil_east_top"],
    "mainParking":     ["ent_gate"],
    "jaguarJungle":    ["jj_center"],
    "miRanchito":      ["mi_ranchito_entry"],
    "labDigitalFia":   ["lab_fia_entry"],
    "areaDeMesas":     ["mesas_pad"],
    "northGate":       ["gate_third"],
    "northeastGate":   ["gate_second"],
}


BARRIERS: List[dict] = [
    {"x": 429, "y": 435, "reason": "Paso bloqueado lado izquierdo anexo B-C"},
    {"x": 412, "y": 397, "reason": "Muro norte Edificio C (sin salida directa al parqueo)"},
    {"x": 598, "y": 438, "reason": "Caja de escaleras Este Edificio M (sin cruce horizontal)"},
    {"x": 444, "y": 274, "reason": "Acceso restringido Clínicas Edificio N (solo personal de odontología)"},
]


def buildPedestrianWalkwayGraph() -> DirectedGraph:
    """
    Constructs the official weighted, directed, non-complete micro-level
    pedestrian walkway graph G = (V, E, W) of the UAM campus.
    """
    g = DirectedGraph()

    for nodeId, (xSvg, ySvg) in WALKWAY_NODES_SPEC.items():
        if nodeId in REAL_GPS_OVERRIDES:
            lat, lng = REAL_GPS_OVERRIDES[nodeId]
        else:
            lat, lng = CampusGeoUtils.svgToGps(xSvg, ySvg)

        meta = WALKWAY_LANDMARKS.get(nodeId)
        spaName = meta[0] if meta else None
        engName = meta[1] if meta else None
        portalKind = meta[2] if meta else None
        buildingId = meta[3] if meta else None
        defaultName = engName or nodeId

        category = CampusCategory.ADMINISTRATIVE
        if portalKind == "stairs":
            category = CampusCategory.STAIRS
        elif portalKind == "ramp":
            category = CampusCategory.ACCESSIBLE_RAMP
        elif portalKind == "gate":
            category = CampusCategory.PARKING_LOT

        g.addNode(Node(
            nodeId=nodeId,
            name=defaultName,
            category=category,
            xPercent=round((xSvg / 1200.0) * 100.0, 2),
            yPercent=round((ySvg / 850.0) * 100.0, 2),
            latitude=lat,
            longitude=lng,
            floorLevel=2 if portalKind == "skybridge" else 1,
            isOutdoorAccessPoint=True,
            xSvg=float(xSvg),
            ySvg=float(ySvg),
            portalKind=portalKind,
            buildingId=buildingId,
            landmarkNameSpa=spaName,
            landmarkNameEng=engName,
        ))

    for fromId, toId, walkwayType, isAccessible in WALKWAY_SEGMENTS_SPEC:
        nA = g.getNode(fromId)
        nB = g.getNode(toId)
        if not nA or not nB:
            continue
        # Weight = physical pavement walking distance in meters derived from calibrated SVG geometry
        weightMeters = CampusGeoUtils.svgDistanceToMeters(nA.xSvg, nA.ySvg, nB.xSvg, nB.ySvg)
        # Level-2 skybridges involve vertical climb/descent unless accessed at level 2
        if walkwayType == "level2":
            weightMeters = round(weightMeters + 4.0, 1)
        g.addBidirectionalWalkway(
            fromId,
            toId,
            distanceMeters=weightMeters,
            isAccessible=isAccessible,
            walkwayType=walkwayType,
            landmarkRef=nB.landmarkNameSpa or "",
        )

    return g


# Singleton instance
globalPedestrianWalkwayGraph = buildPedestrianWalkwayGraph()
