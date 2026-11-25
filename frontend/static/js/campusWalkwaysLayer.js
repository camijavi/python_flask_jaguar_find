/**
 * ================================================================================
 * CAMPUSWALKWAYSLAYER.JS - MICRO-LEVEL PEDESTRIAN WALKWAY NETWORK & TOGGLE LAYER
 * ================================================================================
 * Defines the true micro-level walkable pedestrian network of the UAM campus:
 *  - Sidewalks, crosswalks, plazas, and building perimeter detours (Level 1)
 *  - Covered 2nd-floor skybridges & upper connectors (A-C-B, B-C annex, B-E bridge)
 *  - Actual building entry doors, open pass-through corridors, and stairwells
 *  - Blocked walls & non-passable barriers (C north wall, C-B left wall, M east
 *    stairwell box, Building I west & north solid facades)
 *
 * Exposes:
 *  - window.CAMPUS_MICRO_WALKWAYS : declarative graph & obstacle specification
 *  - window.resolveMicroCampusRoute(pathCoords, opts) : Dijkstra micro-path router
 *  - window.renderCampusWalkwaysLayer() : renders toggleable #pedestrianWalkwaysLayer
 * ================================================================================
 */

(function () {
    const SVG_NS = "http://www.w3.org/2000/svg";

    // ----------------------------------------------------------------------------
    // 1. Micro-Level Pedestrian Waypoints (1200 x 850 Official Campus SVG Space)
    // ----------------------------------------------------------------------------
    const NODES = {
        // Main Entrance, South Ring Sidewalk & West Avenue East Sidewalk
        ent_gate:            { x: 305, y: 778 },
        ent_corner:          { x: 305, y: 696 },
        south_walk_1:        { x: 420, y: 696 },
        south_walk_2:        { x: 534, y: 696 },
        south_walk_3:        { x: 645, y: 696 },
        south_se_turn:       { x: 718, y: 696 },
        west_side_low:       { x: 304, y: 626 },
        west_side_k_south:   { x: 302, y: 562 },
        west_side_bank:      { x: 296, y: 518 },
        banpro_entry:        { x: 230, y: 518 },
        west_side_k_north:   { x: 298, y: 482 },
        a_front_plaza:       { x: 298, y: 435 },
        a_front_north:       { x: 298, y: 394 },

        // Building K & Plaza Central Ruben Dario
        k_west_apron:        { x: 323, y: 484 },
        k_north_walk:        { x: 346, y: 484 },
        k_north_door:        { x: 346, y: 498 },
        k_south_walk:        { x: 362, y: 562 },
        k_se_corner:         { x: 404, y: 562 },
        k_door_east:         { x: 382, y: 536 },
        plaza_south_mid:     { x: 464, y: 562 },
        plaza_south_e:       { x: 508, y: 558 },
        plaza_north_mid:     { x: 444, y: 478 },
        plaza_north_east:    { x: 516, y: 478 },

        // Building A (East/West doors at y=435; North/South corridors at x=323; 3F stairs only)
        a_door_east:         { x: 310, y: 435 },
        a_center:            { x: 323, y: 435 },
        a_door_west:         { x: 336, y: 435 },
        a_corridor_c:        { x: 323, y: 411 },
        a_corridor_b:        { x: 323, y: 459 },
        a_north_exit:        { x: 323, y: 398 },
        a_south_exit:        { x: 323, y: 472 },

        // Building C (Corridor on every floor; East/West entries only, NO mid-north exit)
        c_east_entry:        { x: 338, y: 411 },
        c_mid:               { x: 444, y: 411 },
        c_west_exit:         { x: 564, y: 411 },

        // Central Courtyard & Central B-C Annex (Level 1 divider corridor + Level 2 covered annex)
        court_left_end:      { x: 420, y: 435 },
        court_annex_mid:     { x: 444, y: 435 },
        court_right_end:     { x: 462, y: 435 },
        court_right_entry:   { x: 568, y: 435 },

        // Building B (Open 1st floor — walk anywhere; Level 2 connects A-C-B & B-E skybridge)
        b_east_entry:        { x: 338, y: 459 },
        b_k_link:            { x: 346, y: 459 },
        b_mid:               { x: 444, y: 459 },
        b_bridge_top:        { x: 530, y: 459 },

        // East End of C/B Hub & Building M (East box = stairs; West side mid-partition)
        cm_corridor_c:       { x: 574, y: 411 },
        cm_corridor_mid:     { x: 574, y: 435 },
        m_nw_top:            { x: 598, y: 390 },
        m_nw_junc:           { x: 598, y: 414 },
        m_entry_nw:          { x: 606, y: 414 },
        m_center:            { x: 626, y: 436 },
        m_exit_west:         { x: 646, y: 444 },
        m_west_exit_corner:  { x: 660, y: 444 },
        m_east_top:          { x: 660, y: 390 },
        m_bushes_top:        { x: 680, y: 390 },
        m_bushes_bot:        { x: 684, y: 476 },

        // Building E, Vida Estudiantil, Innovacion, G & F
        e_top:               { x: 534, y: 504 },
        e_mid:               { x: 534, y: 556 },
        e_bottom:            { x: 534, y: 654 },
        e_south_turn:        { x: 546, y: 668 },
        vida_est_north:      { x: 570, y: 616 },
        vida_est_east:       { x: 588, y: 668 },
        se_park_south:       { x: 650, y: 676 },
        eg_alley_top:        { x: 564, y: 478 },
        eg_corridor_top:     { x: 574, y: 478 },
        eg_corridor_g:       { x: 564, y: 509 },
        eg_corridor_gf:      { x: 564, y: 536 },
        eg_corridor_mid:     { x: 564, y: 556 },
        eg_corridor_f_south: { x: 564, y: 598 },
        g_north_walk:        { x: 612, y: 478 },
        g_north_door:        { x: 612, y: 488 },
        g_entry_east:        { x: 582, y: 509 },
        g_center:            { x: 603, y: 509 },
        gf_alley_mid:        { x: 603, y: 536 },
        gf_plaza_top:        { x: 658, y: 478 },
        gf_plaza_mid:        { x: 663, y: 536 },
        f_center:            { x: 603, y: 566 },
        f_south_door:        { x: 616, y: 594 },
        f_south_walk:        { x: 616, y: 598 },
        f_south_east:        { x: 696, y: 596 },

        // Building I (Rectoria & Library — perimeter around bottom/right to Jaguar Center parking, open east courtyard y=618..630)
        i_sw_corner:         { x: 736, y: 706 },
        i_se_corner:         { x: 820, y: 706 },
        i_se_top:            { x: 820, y: 678 },
        i_west_walk:         { x: 736, y: 623 },
        i_nw_drop:           { x: 742, y: 548 },
        i_courtyard_mouth:   { x: 774, y: 623 },
        i_courtyard:         { x: 776, y: 646 },

        // Spine Road Sidewalk & East Sports / Wellness Complex
        spine_se_low:        { x: 708, y: 680 },
        spine_gf_south:      { x: 712, y: 596 },
        spine_i_north:       { x: 724, y: 548 },
        spine_g_north:       { x: 708, y: 476 },
        h_west_spine:        { x: 702, y: 370 },
        h_se_turn:           { x: 698, y: 390 },
        jj_spine_entry:      { x: 676, y: 318 },
        spine_o_north:       { x: 652, y: 140 },
        north_road_t:        { x: 656, y: 26 },
        gate_second:         { x: 906, y: 22 },

        // Crosswalk, Plaza Chilamates (internal paths + direct link to N & P), West Perimeter, J, D, N & Third Access
        crosswalk_bot:       { x: 319, y: 394 },
        crosswalk_mid:       { x: 319, y: 366 },
        crosswalk_top:       { x: 319, y: 344 },
        chil_east_bot:       { x: 324, y: 340 },
        chil_east_kiosk:     { x: 324, y: 314 },
        chil_east_mid:       { x: 324, y: 260 },
        chil_east_top:       { x: 324, y: 222 },
        chil_west_bot:       { x: 275, y: 340 },
        chil_west_kiosk:     { x: 275, y: 314 },
        chilamates_mid:      { x: 300, y: 314 },
        chil_west_top:       { x: 275, y: 242 },
        chilamates_north:    { x: 275, y: 222 },
        west_ave_p:          { x: 240, y: 188 },
        west_ave_gate3:      { x: 218, y: 74 },
        gate_third:          { x: 176, y: 74 },
        north_road_nw:       { x: 258, y: 32 },
        jd_cross_turn:       { x: 385, y: 366 },
        jd_walk_j:           { x: 361, y: 338 },
        j_entry:             { x: 361, y: 326 },
        jd_alley_bot:        { x: 385, y: 338 },
        jd_walk_d:           { x: 410, y: 338 },
        d_entry:             { x: 410, y: 324 },
        n_south_stairs:      { x: 456, y: 338 },
        n_se_corner:         { x: 520, y: 340 },
        n_west_sw:           { x: 364, y: 286 },
        n_jd_junction:       { x: 385, y: 286 },
        n_courtyard:         { x: 430, y: 286 },
        n_inner_se:          { x: 456, y: 286 },
        n_west_mid:          { x: 364, y: 260 },
        n_west_nw:           { x: 364, y: 222 },
        n_north_stairs:      { x: 416, y: 222 },
        n_east_ne:           { x: 520, y: 222 },
        pon_west:            { x: 324, y: 198 },
        pon_bot_left:        { x: 336, y: 214 },
        pon_bot_mid:         { x: 416, y: 214 },
        pon_bot_east:        { x: 530, y: 214 },
        p_front_west:        { x: 329, y: 142 },
        p_front_mid:         { x: 456, y: 142 },
        p_front_east:        { x: 568, y: 142 },
        p_east_top:          { x: 574, y: 88 },
        p_behind_lot:        { x: 546, y: 68 },

        // Building O, Jaguar Jungle, Mi Ranchito, Lab Digital FIA, Area de Mesas & Building H
        o_west_curb_bot:     { x: 554, y: 214 },
        o_west_mid:          { x: 554, y: 194 },
        o_west_door:         { x: 568, y: 194 },
        o_west_top:          { x: 558, y: 168 },
        o_nw_corner:         { x: 576, y: 148 },
        o_terrace_top:       { x: 640, y: 148 },
        o_terrace_mid:       { x: 642, y: 204 },
        o_spine_shoulder:    { x: 655, y: 258 },
        o_terrace_bot:       { x: 638, y: 260 },
        jj_spine_shoulder:   { x: 666, y: 304 },
        jj_north_curve:      { x: 628, y: 288 },
        jj_center:           { x: 628, y: 315 },
        jj_south_curve:      { x: 638, y: 338 },
        jj_west_exit:        { x: 558, y: 324 },
        n_east_annex:        { x: 520, y: 270 },
        annex_path_mid:      { x: 530, y: 270 },
        annex_path_top:      { x: 530, y: 222 },
        mi_ranchito_north:   { x: 555, y: 272 },
        mi_ranchito_top_door:{ x: 555, y: 282 },
        n_east_walk:         { x: 520, y: 296 },
        mi_ranchito_west:    { x: 540, y: 296 },
        mi_ranchito_entry:   { x: 558, y: 308 },
        n_east_lab:          { x: 520, y: 328 },
        lab_fia_entry:       { x: 529, y: 328 },
        mesas_top_right:     { x: 554, y: 340 },
        mesas_left_bot:      { x: 520, y: 392 },
        mesas_corridor:      { x: 554, y: 366 },
        mesas_pad:           { x: 536, y: 366 },
        mesas_south_turn:    { x: 554, y: 390 },
        mesas_cm_corner:     { x: 574, y: 390 },
        h_north_entry:       { x: 640, y: 354 },
        h_south_door:        { x: 618, y: 384 },
        h_south_walk:        { x: 618, y: 390 },

        // Sports Concourse, Jaguar Center, Building L, Fisioterapia, Jaguar Gym & East Sports Complex
        sports_concourse_w:  { x: 724, y: 338 },
        sports_concourse_m:  { x: 918, y: 338 },
        sports_north_park:   { x: 822, y: 36 },
        sports_baseball_ent: { x: 918, y: 318 },
        sports_soccer_north: { x: 918, y: 368 },
        soccer_south_west:   { x: 805, y: 548 },
        soccer_south_west_in:{ x: 805, y: 526 },
        jc_top_left:         { x: 858, y: 548 },
        jc_entry:            { x: 858, y: 576 },
        jc_top_right:        { x: 936, y: 548 },
        jc_entry_right:      { x: 936, y: 576 },
        jc_ne_hub:           { x: 960, y: 548 },
        soccer_south_east_in:{ x: 960, y: 522 },
        jc_l_wash:           { x: 960, y: 560 },
        washrooms_entry:     { x: 978, y: 560 },
        jc_l_upper:          { x: 960, y: 598 },
        l_upper_entry:       { x: 978, y: 598 },
        jc_west_door:        { x: 952, y: 612 },
        jc_l_mid:            { x: 960, y: 612 },
        l_entry:             { x: 989, y: 612 },
        jc_bot_left:         { x: 866, y: 678 },
        jc_bot_left_door:    { x: 866, y: 670 },
        jc_bot_right:        { x: 936, y: 678 },
        jc_bot_right_door:   { x: 936, y: 670 },
        jc_l_ft:             { x: 960, y: 678 },
        ft_entry:            { x: 978, y: 679 },
        gym_park_mid:        { x: 944, y: 706 },
        gym_top_west:        { x: 960, y: 698 },
        gym_top_door_junc:   { x: 969, y: 698 },
        gym_entry:           { x: 969, y: 706 },
        east_corridor_top:   { x: 1006, y: 542 },
        east_corridor_l:     { x: 1006, y: 612 },
        east_corridor_courts:{ x: 1006, y: 647 },
        east_corridor_ft:    { x: 1006, y: 679 },
        east_corridor_gym:   { x: 1006, y: 698 },
        east_corridor_gap:   { x: 1006, y: 774 },
        east_corridor_lunch: { x: 1006, y: 836 },
        bodega_north_mid:    { x: 1046, y: 647 },
        courts_east_junc:    { x: 1080, y: 647 },
        kiosk_sport_entry:   { x: 1094, y: 644 },
        bodega_south_mid:    { x: 1046, y: 679 },
        east_alley_top:      { x: 1080, y: 679 },
        east_alley_ma:       { x: 1080, y: 697 },
        east_alley_mp:       { x: 1080, y: 732 },
        east_alley_bot:      { x: 1080, y: 774 },
        comedor_entry:       { x: 1086, y: 804 }
    };

    // ----------------------------------------------------------------------------
    // 2. Walkable Micro-Segments (type: "ground" | "indoor" | "level2")
    // ----------------------------------------------------------------------------
    const SEGMENTS = [
        // Main Entrance & South Ring Sidewalk (Main access -> right toward Library/Gym)
        { from: "ent_gate",          to: "ent_corner",          type: "ground", accessible: true },
        { from: "ent_corner",        to: "south_walk_1",        type: "ground", accessible: true },
        { from: "south_walk_1",      to: "south_walk_2",        type: "ground", accessible: true },
        { from: "south_walk_2",      to: "south_walk_3",        type: "ground", accessible: true },
        { from: "south_walk_3",      to: "south_se_turn",       type: "ground", accessible: true },

        // Main Entrance -> Straight up toward K, Banpro Bank & Building A
        { from: "ent_corner",        to: "west_side_low",       type: "ground", accessible: true },
        { from: "west_side_low",     to: "west_side_k_south",   type: "ground", accessible: true },
        { from: "west_side_k_south", to: "west_side_bank",      type: "ground", accessible: true },
        { from: "west_side_bank",    to: "banpro_entry",        type: "ground", accessible: true },
        { from: "west_side_bank",    to: "west_side_k_north",   type: "ground", accessible: true },
        { from: "west_side_k_north", to: "a_front_plaza",       type: "ground", accessible: true },
        { from: "a_front_plaza",     to: "a_door_east",         type: "ground", accessible: true },
        { from: "a_front_plaza",     to: "a_front_north",       type: "ground", accessible: true },
        { from: "a_front_north",     to: "crosswalk_bot",       type: "ground", accessible: true },

        // Building K & Plaza Central Ruben Dario
        { from: "west_side_k_south", to: "k_south_walk",        type: "ground", accessible: true },
        { from: "k_south_walk",      to: "k_se_corner",         type: "ground", accessible: true },
        { from: "k_se_corner",       to: "k_door_east",         type: "ground", accessible: true },
        { from: "k_se_corner",       to: "plaza_south_mid",     type: "ground", accessible: true },
        { from: "plaza_south_mid",   to: "plaza_south_e",       type: "ground", accessible: true },
        { from: "plaza_south_e",     to: "e_mid",               type: "ground", accessible: true },
        { from: "west_side_k_north", to: "k_west_apron",        type: "ground", accessible: true },
        { from: "k_west_apron",      to: "a_south_exit",        type: "ground", accessible: true },
        { from: "k_west_apron",      to: "k_north_walk",        type: "ground", accessible: true },
        { from: "k_north_walk",      to: "k_north_door",        type: "ground", accessible: true },
        { from: "k_north_walk",      to: "b_k_link",            type: "ground", accessible: true },
        { from: "k_north_walk",      to: "plaza_north_mid",     type: "ground", accessible: true },
        { from: "plaza_north_mid",   to: "b_mid",               type: "ground", accessible: true },
        { from: "plaza_north_mid",   to: "plaza_north_east",    type: "ground", accessible: true },
        { from: "plaza_north_east",  to: "b_bridge_top",        type: "ground", accessible: true },
        { from: "plaza_north_east",  to: "eg_alley_top",        type: "ground", accessible: true },
        { from: "eg_alley_top",      to: "eg_corridor_top",     type: "ground", accessible: true },

        // Building A: East/West Door Pass-Through + North/South Corridors
        { from: "a_door_east",       to: "a_center",            type: "indoor", accessible: true },
        { from: "a_center",          to: "a_door_west",         type: "indoor", accessible: true },
        { from: "a_center",          to: "a_corridor_c",        type: "indoor", accessible: true },
        { from: "a_center",          to: "a_corridor_b",        type: "indoor", accessible: true },
        { from: "a_corridor_c",      to: "a_north_exit",        type: "indoor", accessible: true },
        { from: "a_corridor_b",      to: "a_south_exit",        type: "indoor", accessible: true },

        // Building C: Full East-West Corridor (East & West access only; NO mid-north exit)
        { from: "a_corridor_c",      to: "c_east_entry",        type: "indoor", accessible: true },
        { from: "c_east_entry",      to: "c_mid",               type: "indoor", accessible: true },
        { from: "c_mid",             to: "c_west_exit",         type: "indoor", accessible: true },
        { from: "c_west_exit",       to: "cm_corridor_c",       type: "ground", accessible: true },

        // Central Courtyard & Central B-C Annex (Level 1 divider + Level 2 covered annex)
        // Note: court_left_end stops before the blocked left wall of the annex!
        { from: "a_door_west",       to: "court_left_end",      type: "ground", accessible: true },
        { from: "c_mid",             to: "court_annex_mid",     type: "level2", accessible: true },
        { from: "court_annex_mid",   to: "b_mid",               type: "level2", accessible: true },
        { from: "court_right_end",   to: "court_right_entry",   type: "ground", accessible: true },
        { from: "court_right_entry", to: "cm_corridor_mid",     type: "ground", accessible: true },

        // Building B: Open 1st-Floor Hallway + 2nd-Floor Covered Skybridge to E (closed east end wall; access via south Plaza Central)
        { from: "a_corridor_b",      to: "b_east_entry",        type: "indoor", accessible: true },
        { from: "b_east_entry",      to: "b_k_link",            type: "indoor", accessible: true },
        { from: "b_k_link",          to: "b_mid",               type: "indoor", accessible: true },
        { from: "b_mid",             to: "b_bridge_top",        type: "indoor", accessible: true },
        { from: "b_bridge_top",      to: "e_top",               type: "level2", accessible: true },

        // Right End of C/B Hub & Building M (NW vertical entry + West mid-partition L-corridor up to H; no diagonal/bush cuts!)
        { from: "cm_corridor_c",     to: "cm_corridor_mid",     type: "ground", accessible: true },
        { from: "cm_corridor_mid",   to: "eg_corridor_top",     type: "ground", accessible: true },
        { from: "cm_corridor_c",     to: "m_nw_junc",           type: "ground", accessible: true },
        { from: "m_nw_top",          to: "m_nw_junc",           type: "ground", accessible: true },
        { from: "m_nw_junc",         to: "m_entry_nw",          type: "ground", accessible: true },
        { from: "m_entry_nw",        to: "m_center",            type: "indoor", accessible: true },
        { from: "m_center",          to: "m_exit_west",         type: "indoor", accessible: true },
        { from: "m_exit_west",       to: "m_west_exit_corner",  type: "ground", accessible: true },
        { from: "m_west_exit_corner",to: "m_east_top",          type: "ground", accessible: true },
        { from: "m_bushes_top",      to: "m_bushes_bot",        type: "ground", accessible: true },

        // Building E, Vida Estudiantil, G, F & SE Parking
        { from: "e_top",             to: "e_mid",               type: "indoor", accessible: true },
        { from: "e_mid",             to: "e_bottom",            type: "indoor", accessible: true },
        { from: "e_mid",             to: "eg_corridor_mid",     type: "ground", accessible: true },
        { from: "e_bottom",          to: "e_south_turn",        type: "ground", accessible: true },
        { from: "e_south_turn",      to: "vida_est_east",       type: "ground", accessible: true },
        { from: "vida_est_east",     to: "se_park_south",       type: "ground", accessible: true },
        { from: "se_park_south",     to: "spine_se_low",        type: "ground", accessible: true },
        { from: "eg_corridor_top",   to: "g_north_walk",        type: "ground", accessible: true },
        { from: "g_north_walk",      to: "g_north_door",        type: "ground", accessible: true },
        { from: "g_north_walk",      to: "gf_plaza_top",        type: "ground", accessible: true },
        { from: "gf_plaza_top",      to: "m_bushes_bot",        type: "ground", accessible: true },
        { from: "m_bushes_bot",      to: "spine_g_north",       type: "ground", accessible: true },
        { from: "gf_plaza_top",      to: "gf_plaza_mid",        type: "ground", accessible: true },
        { from: "eg_alley_top",      to: "eg_corridor_g",       type: "ground", accessible: true },
        { from: "eg_corridor_g",     to: "g_entry_east",        type: "ground", accessible: true },
        { from: "g_entry_east",      to: "g_center",            type: "indoor", accessible: true },
        { from: "eg_corridor_g",     to: "eg_corridor_gf",      type: "ground", accessible: true },
        { from: "eg_corridor_gf",    to: "gf_alley_mid",        type: "ground", accessible: true },
        { from: "gf_alley_mid",      to: "gf_plaza_mid",        type: "ground", accessible: true },
        { from: "eg_corridor_gf",    to: "eg_corridor_mid",     type: "ground", accessible: true },
        { from: "eg_corridor_mid",   to: "eg_corridor_f_south", type: "ground", accessible: true },
        { from: "eg_corridor_f_south", to: "vida_est_north",    type: "ground", accessible: true },
        { from: "eg_corridor_f_south", to: "f_south_walk",      type: "ground", accessible: true },
        { from: "f_south_walk",      to: "f_south_door",        type: "ground", accessible: true },
        { from: "f_south_door",      to: "f_center",            type: "indoor", accessible: true },
        { from: "f_south_walk",      to: "f_south_east",        type: "ground", accessible: true },
        { from: "f_south_east",      to: "spine_gf_south",      type: "ground", accessible: true },
        { from: "gf_plaza_mid",      to: "spine_gf_south",      type: "ground", accessible: true },

        // Building I Perimeter & Clean Courtyard Entrance (links straight up to y=548 promenade & right to Jaguar Center / Gym)
        { from: "spine_se_low",      to: "south_se_turn",       type: "ground", accessible: true },
        { from: "south_se_turn",     to: "i_sw_corner",         type: "ground", accessible: true },
        { from: "i_sw_corner",       to: "i_west_walk",         type: "ground", accessible: true },
        { from: "i_west_walk",       to: "i_courtyard_mouth",   type: "ground", accessible: true },
        { from: "i_courtyard_mouth", to: "i_courtyard",         type: "ground", accessible: true },
        { from: "i_west_walk",       to: "i_nw_drop",           type: "ground", accessible: true },
        { from: "i_sw_corner",       to: "i_se_corner",         type: "ground", accessible: true },
        { from: "i_se_corner",       to: "i_se_top",            type: "ground", accessible: true },
        { from: "i_se_top",          to: "jc_bot_left",         type: "ground", accessible: true },
        { from: "i_se_corner",       to: "gym_park_mid",        type: "ground", accessible: true },

        // Spine Road Continuous North-South Sidewalk (no diagonal cut across Jaguar Jungle lawn!)
        { from: "spine_se_low",      to: "spine_gf_south",      type: "ground", accessible: true },
        { from: "spine_gf_south",    to: "spine_i_north",       type: "ground", accessible: true },
        { from: "spine_i_north",     to: "spine_g_north",       type: "ground", accessible: true },
        { from: "spine_g_north",     to: "h_west_spine",        type: "ground", accessible: true },
        { from: "h_west_spine",      to: "jj_spine_entry",      type: "ground", accessible: true },
        { from: "jj_spine_entry",    to: "jj_spine_shoulder",   type: "ground", accessible: true },
        { from: "jj_spine_shoulder", to: "o_spine_shoulder",    type: "ground", accessible: true },
        { from: "o_spine_shoulder",  to: "o_terrace_mid",       type: "ground", accessible: true },
        { from: "h_west_spine",      to: "h_se_turn",           type: "ground", accessible: true },
        { from: "o_terrace_top",     to: "spine_o_north",       type: "ground", accessible: true },
        { from: "spine_o_north",     to: "north_road_t",        type: "ground", accessible: true },
        { from: "north_road_t",      to: "gate_second",         type: "ground", accessible: true },

        // Crosswalk, Plaza Chilamates Internal Walkways, Direct Link to N & P, J-D Alley & Building N Perimeter
        { from: "a_north_exit",      to: "crosswalk_bot",       type: "ground", accessible: true },
        { from: "crosswalk_bot",     to: "crosswalk_mid",       type: "ground", accessible: true },
        { from: "crosswalk_mid",     to: "crosswalk_top",       type: "ground", accessible: true },
        { from: "crosswalk_mid",     to: "jd_cross_turn",       type: "ground", accessible: true },
        { from: "jd_cross_turn",     to: "jd_alley_bot",        type: "ground", accessible: true },
        { from: "crosswalk_top",     to: "chil_east_bot",       type: "ground", accessible: true },
        { from: "chil_east_bot",     to: "chil_east_kiosk",     type: "ground", accessible: true },
        { from: "chil_east_kiosk",   to: "chil_east_mid",       type: "ground", accessible: true },
        { from: "chil_east_mid",     to: "chil_east_top",       type: "ground", accessible: true },
        { from: "chil_east_top",     to: "pon_west",            type: "ground", accessible: true },
        { from: "chil_east_bot",     to: "chil_west_bot",       type: "ground", accessible: true },
        { from: "chil_west_bot",     to: "chil_west_kiosk",     type: "ground", accessible: true },
        { from: "chil_west_kiosk",   to: "chilamates_mid",      type: "ground", accessible: true },
        { from: "chilamates_mid",    to: "chil_east_kiosk",     type: "ground", accessible: true },
        { from: "chil_west_kiosk",   to: "chil_west_top",       type: "ground", accessible: true },
        { from: "chil_west_top",     to: "chilamates_north",    type: "ground", accessible: true },
        { from: "chilamates_north",  to: "chil_east_top",       type: "ground", accessible: true },
        { from: "chilamates_north",  to: "west_ave_p",          type: "ground", accessible: true },
        { from: "west_ave_p",        to: "pon_west",            type: "ground", accessible: true },
        { from: "west_ave_p",        to: "west_ave_gate3",      type: "ground", accessible: true },
        { from: "west_ave_gate3",    to: "gate_third",          type: "ground", accessible: true },
        { from: "west_ave_gate3",    to: "north_road_nw",       type: "ground", accessible: true },
        { from: "north_road_nw",     to: "north_road_t",        type: "ground", accessible: true },

        // J, D, Alley between J & D -> Building N Courtyard -> Wrap-Around Building N Perimeter (NO cut through N!)
        { from: "crosswalk_top",     to: "jd_walk_j",           type: "ground", accessible: true },
        { from: "jd_walk_j",         to: "j_entry",             type: "ground", accessible: true },
        { from: "jd_walk_j",         to: "jd_alley_bot",        type: "ground", accessible: true },
        { from: "jd_alley_bot",      to: "jd_walk_d",           type: "ground", accessible: true },
        { from: "jd_alley_bot",      to: "n_jd_junction",       type: "ground", accessible: true },
        { from: "jd_walk_d",         to: "d_entry",             type: "ground", accessible: true },
        { from: "jd_walk_d",         to: "n_south_stairs",      type: "ground", accessible: true },
        { from: "n_south_stairs",    to: "n_inner_se",          type: "ground", accessible: true },
        { from: "n_south_stairs",    to: "n_se_corner",         type: "ground", accessible: true },
        { from: "n_inner_se",        to: "n_courtyard",         type: "ground", accessible: true },
        { from: "n_courtyard",       to: "n_jd_junction",       type: "ground", accessible: true },
        { from: "n_jd_junction",     to: "n_west_sw",           type: "ground", accessible: true },
        { from: "n_west_sw",         to: "n_west_mid",          type: "ground", accessible: true },
        { from: "n_west_mid",        to: "chil_east_mid",       type: "ground", accessible: true },
        { from: "n_west_mid",        to: "n_west_nw",           type: "ground", accessible: true },
        { from: "n_west_nw",         to: "chil_east_top",       type: "ground", accessible: true },
        { from: "n_west_nw",         to: "n_north_stairs",      type: "ground", accessible: true },
        { from: "n_north_stairs",    to: "pon_bot_mid",         type: "ground", accessible: false },
        { from: "n_north_stairs",    to: "n_east_ne",           type: "ground", accessible: true },
        { from: "n_east_ne",         to: "annex_path_top",      type: "ground", accessible: true },
        { from: "chil_east_top",     to: "pon_bot_left",        type: "ground", accessible: true },
        { from: "pon_bot_left",      to: "pon_bot_mid",         type: "ground", accessible: true },
        { from: "pon_bot_mid",       to: "pon_bot_east",        type: "ground", accessible: true },
        { from: "pon_bot_east",      to: "annex_path_top",      type: "ground", accessible: true },
        { from: "pon_bot_east",      to: "o_west_curb_bot",     type: "ground", accessible: true },
        { from: "pon_west",          to: "p_front_west",        type: "ground", accessible: true },
        { from: "p_front_west",      to: "p_front_mid",         type: "ground", accessible: true },
        { from: "p_front_mid",       to: "p_front_east",        type: "ground", accessible: true },
        { from: "p_front_east",      to: "p_east_top",          type: "ground", accessible: true },
        { from: "p_east_top",        to: "p_behind_lot",        type: "ground", accessible: true },

        // Building O (clean west & north wrap — no cuts across PON parking), Jaguar Jungle, Mi Ranchito, Lab FIA, Mesas & H
        { from: "o_west_curb_bot",   to: "o_west_mid",          type: "ground", accessible: true },
        { from: "o_west_mid",        to: "o_west_door",         type: "ground", accessible: true },
        { from: "o_west_mid",        to: "o_west_top",          type: "ground", accessible: true },
        { from: "o_west_top",        to: "o_nw_corner",         type: "ground", accessible: true },
        { from: "p_front_east",      to: "o_nw_corner",         type: "ground", accessible: true },
        { from: "o_nw_corner",       to: "o_terrace_top",       type: "ground", accessible: true },
        { from: "o_terrace_top",     to: "o_terrace_mid",       type: "ground", accessible: true },
        { from: "o_terrace_mid",     to: "o_terrace_bot",       type: "ground", accessible: true },
        { from: "o_terrace_bot",     to: "jj_north_curve",      type: "ground", accessible: true },
        { from: "jj_north_curve",    to: "jj_center",           type: "ground", accessible: true },
        { from: "jj_center",         to: "jj_south_curve",      type: "ground", accessible: true },
        { from: "jj_south_curve",    to: "h_north_entry",       type: "ground", accessible: true },
        { from: "jj_spine_entry",    to: "jj_center",           type: "ground", accessible: true },
        { from: "jj_center",         to: "jj_west_exit",        type: "ground", accessible: true },
        { from: "jj_west_exit",      to: "mi_ranchito_entry",   type: "ground", accessible: true },
        { from: "n_east_ne",         to: "n_east_annex",        type: "ground", accessible: true },
        { from: "n_east_annex",      to: "annex_path_mid",      type: "ground", accessible: true },
        { from: "annex_path_mid",    to: "annex_path_top",      type: "ground", accessible: true },
        { from: "annex_path_mid",    to: "mi_ranchito_north",   type: "ground", accessible: true },
        { from: "mi_ranchito_north", to: "mi_ranchito_top_door",type: "ground", accessible: true },
        { from: "n_east_annex",      to: "n_east_walk",         type: "ground", accessible: true },
        { from: "n_east_walk",       to: "mi_ranchito_west",    type: "ground", accessible: true },
        { from: "mi_ranchito_west",  to: "mi_ranchito_entry",   type: "indoor", accessible: true },
        { from: "mi_ranchito_top_door", to: "mi_ranchito_entry",type: "indoor", accessible: true },
        { from: "n_east_walk",       to: "n_east_lab",          type: "ground", accessible: true },
        { from: "n_east_lab",        to: "lab_fia_entry",       type: "ground", accessible: true },
        { from: "n_east_lab",        to: "n_se_corner",         type: "ground", accessible: true },
        { from: "n_se_corner",       to: "mesas_top_right",     type: "ground", accessible: true },
        { from: "n_se_corner",       to: "mesas_left_bot",      type: "ground", accessible: true },
        { from: "mesas_left_bot",    to: "mesas_south_turn",    type: "ground", accessible: true },
        { from: "jj_west_exit",      to: "mesas_top_right",     type: "ground", accessible: true },
        { from: "mesas_top_right",   to: "mesas_corridor",      type: "ground", accessible: true },
        { from: "mesas_corridor",    to: "mesas_pad",           type: "ground", accessible: true },
        { from: "mesas_corridor",    to: "mesas_south_turn",    type: "ground", accessible: true },
        { from: "mesas_south_turn",  to: "mesas_cm_corner",     type: "ground", accessible: true },
        { from: "mesas_cm_corner",   to: "cm_corridor_c",       type: "ground", accessible: true },
        { from: "mesas_cm_corner",   to: "m_nw_top",            type: "ground", accessible: true },
        { from: "m_nw_top",          to: "h_south_walk",        type: "ground", accessible: true },
        { from: "h_south_walk",      to: "h_south_door",        type: "ground", accessible: true },
        { from: "h_south_walk",      to: "m_east_top",          type: "ground", accessible: true },
        { from: "m_east_top",        to: "m_bushes_top",        type: "ground", accessible: true },
        { from: "m_bushes_top",      to: "h_se_turn",           type: "ground", accessible: true },

        // Sports Concourse, Jaguar Center, Building L, Fisioterapia, Jaguar Gym & East Sports Complex
        { from: "jj_spine_entry",    to: "sports_concourse_w",  type: "ground", accessible: true },
        { from: "sports_concourse_w", to: "sports_concourse_m", type: "ground", accessible: true },
        { from: "sports_concourse_m", to: "sports_baseball_ent", type: "ground", accessible: true },
        { from: "sports_concourse_m", to: "sports_soccer_north", type: "ground", accessible: true },
        { from: "north_road_t",      to: "sports_north_park",   type: "ground", accessible: true },
        { from: "sports_north_park", to: "gate_second",         type: "ground", accessible: true },
        { from: "sports_concourse_w", to: "spine_i_north",      type: "ground", accessible: true },

        // Straight Horizontal Promenade South of Soccer Field (y=548) -> Building I, Soccer & Jaguar Center
        { from: "spine_i_north",     to: "i_nw_drop",           type: "ground", accessible: true },
        { from: "i_nw_drop",         to: "soccer_south_west",   type: "ground", accessible: true },
        { from: "soccer_south_west", to: "soccer_south_west_in",type: "ground", accessible: true },
        { from: "soccer_south_west", to: "jc_top_left",         type: "ground", accessible: true },
        { from: "jc_top_left",       to: "jc_entry",            type: "ground", accessible: true },
        { from: "jc_top_left",       to: "jc_top_right",        type: "ground", accessible: true },
        { from: "jc_top_right",      to: "jc_entry_right",      type: "ground", accessible: true },
        { from: "jc_top_right",      to: "jc_ne_hub",           type: "ground", accessible: true },
        { from: "jc_ne_hub",         to: "soccer_south_east_in",type: "ground", accessible: true },
        { from: "jc_ne_hub",         to: "east_corridor_top",   type: "ground", accessible: true },

        // Vertical Corridor between Jaguar Center & Washrooms / Building L / Fisioterapia (x=960)
        { from: "jc_ne_hub",         to: "jc_l_wash",           type: "ground", accessible: true },
        { from: "jc_l_wash",         to: "washrooms_entry",     type: "ground", accessible: true },
        { from: "jc_l_wash",         to: "jc_l_upper",          type: "ground", accessible: true },
        { from: "jc_l_upper",        to: "l_upper_entry",       type: "ground", accessible: true },
        { from: "jc_l_upper",        to: "jc_l_mid",            type: "ground", accessible: true },
        { from: "jc_west_door",      to: "jc_l_mid",            type: "ground", accessible: true },
        { from: "jc_l_mid",          to: "l_entry",             type: "ground", accessible: true },
        { from: "l_entry",           to: "east_corridor_l",     type: "ground", accessible: true },
        { from: "jc_l_mid",          to: "jc_l_ft",             type: "ground", accessible: true },
        { from: "jc_l_ft",           to: "ft_entry",            type: "ground", accessible: true },
        { from: "ft_entry",          to: "east_corridor_ft",    type: "ground", accessible: true },
        { from: "jc_l_ft",           to: "gym_top_west",        type: "ground", accessible: true },

        // Dual Horizontal Walkways South of Jaguar Center -> Jaguar Gym Top Entrance & East Corridor
        { from: "jc_bot_left",       to: "jc_bot_left_door",    type: "ground", accessible: true },
        { from: "jc_bot_left",       to: "jc_bot_right",        type: "ground", accessible: true },
        { from: "jc_bot_right",      to: "jc_bot_right_door",   type: "ground", accessible: true },
        { from: "jc_bot_right",      to: "jc_l_ft",             type: "ground", accessible: true },
        { from: "gym_park_mid",      to: "gym_top_west",        type: "ground", accessible: true },
        { from: "gym_top_west",      to: "gym_top_door_junc",   type: "ground", accessible: true },
        { from: "gym_top_door_junc", to: "gym_entry",           type: "ground", accessible: true },
        { from: "gym_top_door_junc", to: "east_corridor_gym",   type: "ground", accessible: true },

        // East Corridor (x=1006) & Courts / Bodega / Jaguar Sport Kiosk / Martial Arts / Multipurpose Alley (x=1080)
        { from: "east_corridor_top",   to: "east_corridor_l",     type: "ground", accessible: true },
        { from: "east_corridor_l",     to: "east_corridor_courts",type: "ground", accessible: true },
        { from: "east_corridor_courts",to: "east_corridor_ft",    type: "ground", accessible: true },
        { from: "east_corridor_ft",    to: "east_corridor_gym",   type: "ground", accessible: true },
        { from: "east_corridor_gym",   to: "east_corridor_gap",   type: "ground", accessible: true },
        { from: "east_corridor_gap",   to: "east_corridor_lunch", type: "ground", accessible: true },
        { from: "east_corridor_gap",   to: "east_alley_bot",      type: "ground", accessible: true },
        { from: "east_corridor_courts",to: "bodega_north_mid",    type: "ground", accessible: true },
        { from: "bodega_north_mid",    to: "courts_east_junc",    type: "ground", accessible: true },
        { from: "courts_east_junc",    to: "kiosk_sport_entry",   type: "ground", accessible: true },
        { from: "east_corridor_ft",    to: "bodega_south_mid",    type: "ground", accessible: true },
        { from: "bodega_south_mid",    to: "east_alley_top",      type: "ground", accessible: true },
        { from: "courts_east_junc",    to: "east_alley_top",      type: "ground", accessible: true },
        { from: "east_alley_top",      to: "east_alley_ma",       type: "ground", accessible: true },
        { from: "east_alley_ma",       to: "east_alley_mp",       type: "ground", accessible: true },
        { from: "east_alley_mp",       to: "east_alley_bot",      type: "ground", accessible: true },
        { from: "east_alley_bot",      to: "comedor_entry",       type: "ground", accessible: true }
    ];

    // ----------------------------------------------------------------------------
    // 3. Key Doors / Portals & Non-Passable Wall Barriers
    // ----------------------------------------------------------------------------
    const PORTALS = [
        { x: 310, y: 435, kind: "door",     id: "buildingA_east_door" },
        { x: 336, y: 435, kind: "door",     id: "buildingA_west_door" },
        { x: 323, y: 400, kind: "corridor", id: "buildingA_south_corridor" },
        { x: 323, y: 470, kind: "corridor", id: "buildingA_north_corridor" },
        { x: 338, y: 411, kind: "corridor", id: "buildingC_east_access" },
        { x: 564, y: 411, kind: "corridor", id: "buildingC_west_access" },
        { x: 606, y: 414, kind: "door",     id: "buildingM_main_access" },
        { x: 645, y: 444, kind: "door",     id: "buildingM_west_partition" },
        { x: 598, y: 438, kind: "stairs",   id: "buildingM_east_stairs" },
        { x: 346, y: 498, kind: "door",     id: "buildingK_north_access" },
        { x: 382, y: 536, kind: "door",     id: "buildingK_cafeteria_access" },
        { x: 582, y: 509, kind: "door",     id: "buildingG_east_access" },
        { x: 612, y: 486, kind: "door",     id: "buildingG_south_access" },
        { x: 640, y: 354, kind: "door",     id: "buildingH_south_access" },
        { x: 618, y: 384, kind: "door",     id: "buildingH_north_access" },
        { x: 616, y: 592, kind: "door",     id: "buildingF_access" },
        { x: 750, y: 623, kind: "door",     id: "buildingI_courtyard_access" },
        { x: 540, y: 296, kind: "door",     id: "miRanchito_east_access" },
        { x: 555, y: 282, kind: "door",     id: "miRanchito_north_access" },
        { x: 523, y: 328, kind: "door",     id: "labDigitalFia_access" },
        { x: 568, y: 194, kind: "door",     id: "buildingO_west_access" },
        { x: 858, y: 576, kind: "door",     id: "jaguarCenter_se_access" },
        { x: 936, y: 576, kind: "door",     id: "jaguarCenter_sw_access" },
        { x: 952, y: 612, kind: "door",     id: "jaguarCenter_side_access" },
        { x: 969, y: 704, kind: "door",     id: "jaguarGym_main_access" }
    ];

    // Explicitly blocked walls / non-passable boundaries (positioned cleanly clear of building badges)
    const BARRIERS = [
        { x: 429, y: 435, id: "barrier_annex_bc_left" },
        { x: 412, y: 397, id: "barrier_buildingC_north_wall" },
        { x: 598, y: 438, id: "barrier_buildingM_east_stairs" },
        { x: 444, y: 274, id: "barrier_buildingN_restricted_clinics" }
    ];

    // 2nd-Floor Covered Connectors (rendered with localized compact floor pill)
    const LEVEL2_BADGES = [
        { x: 530, y: 485, key: "map.walkways_legend.badge_2p" }, // Covered skybridge B <-> E
        { x: 444, y: 435, key: "map.walkways_legend.badge_2p" }  // Central B <-> C annex (1F divider + 2F bridge)
    ];

    // Mapping from Macro Graph Node IDs -> Real Walkable Entrance Micro-Nodes
    const MACRO_TO_MICRO_NODE = {
        mainParking:     "ent_gate",
        buildingK:       "k_door_east",
        chilamatesPlaza: "chilamates_mid",
        buildingA:       "a_center",
        buildingB:       "b_mid",
        buildingC:       "c_mid",
        buildingD:       "d_entry",
        buildingJ:       "j_entry",
        buildingN:       "n_courtyard",
        buildingO:       "o_terrace_mid",
        buildingP:       "p_front_mid",
        buildingM:       "m_center",
        buildingG:       "g_center",
        buildingF:       "f_center",
        buildingE:       "e_mid",
        buildingI:       "i_courtyard",
        buildingH:       "h_south_door",
        sportsZone:      "sports_concourse_m",
        jaguarCenter:    "jc_entry",
        jaguarGym:       "gym_entry",
        physiotherapy:   "ft_entry",
        buildingL:       "l_entry",
        jaguarJungle:    "jj_center",
        miRanchito:      "mi_ranchito_entry",
        labDigitalFia:   "lab_fia_entry",
        areaDeMesas:     "mesas_pad",
        northGate:       "gate_third",
        northeastGate:   "gate_second"
    };

    const RECOMMENDED_SEGMENT_KEYS = new Set([
        ["west_side_k_south", "k_south_walk"],
        ["west_side_k_north", "k_west_apron"],
        ["k_west_apron", "a_south_exit"],
        ["plaza_south_mid", "plaza_south_e"],
        ["plaza_south_e", "e_mid"],
        ["a_north_exit", "crosswalk_bot"],
        ["crosswalk_bot", "crosswalk_mid"],
        ["crosswalk_mid", "jd_cross_turn"],
        ["jd_cross_turn", "jd_alley_bot"],
        ["jd_alley_bot", "jd_walk_d"],
        ["jd_walk_d", "n_south_stairs"],
        ["n_south_stairs", "n_se_corner"],
        ["n_se_corner", "mesas_top_right"],
        ["mesas_top_right", "mesas_corridor"],
        ["mesas_corridor", "mesas_pad"],
        ["mesas_corridor", "mesas_south_turn"],
        ["mesas_south_turn", "mesas_cm_corner"],
        ["mesas_cm_corner", "m_nw_top"],
        ["m_nw_top", "h_south_walk"],
        ["pon_bot_left", "pon_bot_mid"],
        ["pon_bot_mid", "pon_bot_east"],
        ["pon_bot_east", "o_west_curb_bot"],
        ["p_front_east", "o_nw_corner"],
        ["o_nw_corner", "o_terrace_top"],
        ["o_terrace_top", "o_terrace_mid"],
        ["o_terrace_mid", "o_terrace_bot"],
        ["o_terrace_bot", "jj_north_curve"],
        ["jj_north_curve", "jj_center"],
        ["jj_center", "jj_south_curve"],
        ["eg_corridor_gf", "eg_corridor_mid"],
        ["eg_corridor_mid", "eg_corridor_f_south"],
        ["gf_plaza_top", "gf_plaza_mid"],
        ["gf_plaza_mid", "spine_gf_south"],
        ["spine_se_low", "spine_gf_south"],
        ["spine_gf_south", "spine_i_north"],
        ["spine_i_north", "i_nw_drop"],
        ["i_nw_drop", "soccer_south_west"],
        ["soccer_south_west", "jc_top_left"],
        ["jc_top_left", "jc_top_right"],
        ["jc_top_right", "jc_ne_hub"]
    ].map(([from, to]) => `${from}|${to}`));
    const INACCESSIBLE_SEGMENT_KEYS = new Set([
        ["n_west_mid", "chil_east_mid"],
        ["n_west_mid", "n_west_nw"],
        ["n_west_nw", "chil_east_top"]
    ].map(([from, to]) => `${from}|${to}`));
    for (const seg of SEGMENTS) {
        const key = `${seg.from}|${seg.to}`;
        const reverseKey = `${seg.to}|${seg.from}`;
        if (INACCESSIBLE_SEGMENT_KEYS.has(key) || INACCESSIBLE_SEGMENT_KEYS.has(reverseKey)) {
            seg.accessible = false;
        }
        seg.accessibilityZone = seg.accessible === false
            ? "inaccessible"
            : RECOMMENDED_SEGMENT_KEYS.has(key) || RECOMMENDED_SEGMENT_KEYS.has(reverseKey)
                ? "recommended"
                : "neutral";
    }

    // ----------------------------------------------------------------------------
    // 4. Micro-Walkway Dijkstra Router (Produces Real Sidewalk-Hugging Routes)
    // ----------------------------------------------------------------------------
    const ADJACENCY = {};
    for (const id of Object.keys(NODES)) ADJACENCY[id] = [];
    for (const seg of SEGMENTS) {
        const a = NODES[seg.from];
        const b = NODES[seg.to];
        if (!a || !b) continue;
        const weight = Math.hypot(b.x - a.x, b.y - a.y);
        ADJACENCY[seg.from].push({
            to: seg.to,
            weight,
            accessible: seg.accessible !== false,
            accessibilityZone: seg.accessibilityZone
        });
        ADJACENCY[seg.to].push({
            to: seg.from,
            weight,
            accessible: seg.accessible !== false,
            accessibilityZone: seg.accessibilityZone
        });
    }

    function shortestMicroPath(startId, endId, accessibleOnly = false) {
        if (!NODES[startId] || !NODES[endId]) return null;
        if (startId === endId) return [NODES[startId]];

        const dist = {};
        const prev = {};
        const visited = new Set();
        for (const id of Object.keys(NODES)) dist[id] = Infinity;
        dist[startId] = 0;

        while (true) {
            let u = null;
            let best = Infinity;
            for (const id of Object.keys(NODES)) {
                if (!visited.has(id) && dist[id] < best) {
                    best = dist[id];
                    u = id;
                }
            }
            if (!u || u === endId) break;
            visited.add(u);

            for (const edge of ADJACENCY[u]) {
                if (accessibleOnly && (!edge.accessible || edge.accessibilityZone === "inaccessible")) continue;
                const costFactor = accessibleOnly && edge.accessibilityZone === "recommended" ? 0.8 : 1;
                const alt = dist[u] + edge.weight * costFactor;
                if (alt < dist[edge.to]) {
                    dist[edge.to] = alt;
                    prev[edge.to] = u;
                }
            }
        }

        if (dist[endId] === Infinity) {
            return null;
        }

        const ids = [];
        let curr = endId;
        while (curr) {
            ids.push(curr);
            curr = prev[curr];
        }
        ids.reverse();
        return ids.map(id => NODES[id]);
    }

    /**
     * Resolves an ordered array of macro route pathCoordinates into real walkable
     * sidewalk/corridor SVG points avoiding closed walls and obstacles.
     */
    function resolveMicroCampusRoute(pathCoordinates, options = {}) {
        if (!Array.isArray(pathCoordinates) || pathCoordinates.length < 2) return [];
        const accessibleOnly = Boolean(options.accessibleOnly);
        const anchors = window.CAMPUS_BUILDING_ANCHORS || {};
        const pts = [];

        const pushPoint = (pt) => {
            if (!pt) return;
            const last = pts[pts.length - 1];
            if (!last || Math.hypot(pt.x - last.x, pt.y - last.y) > 1.5) {
                pts.push({ x: Math.round(pt.x), y: Math.round(pt.y) });
            }
        };

        const fallbackCoord = (c) => {
            if (c && c.nodeId && anchors[c.nodeId]) return anchors[c.nodeId];
            return {
                x: Math.round(((c.xPercent || 50) / 100) * 1200),
                y: Math.round(((c.yPercent || 50) / 100) * 850)
            };
        };

        for (let i = 0; i < pathCoordinates.length - 1; i++) {
            const cA = pathCoordinates[i];
            const cB = pathCoordinates[i + 1];
            const mA = cA && MACRO_TO_MICRO_NODE[cA.nodeId];
            const mB = cB && MACRO_TO_MICRO_NODE[cB.nodeId];
            const segPts = (mA && mB) ? shortestMicroPath(mA, mB, accessibleOnly) : null;

            if (segPts && segPts.length >= 2) {
                for (const p of segPts) pushPoint(p);
            } else {
                pushPoint(fallbackCoord(cA));
                pushPoint(fallbackCoord(cB));
            }
        }
        return pts;
    }

    // ----------------------------------------------------------------------------
    // 5. Toggleable SVG Micro-Walkways Layer Renderer
    // ----------------------------------------------------------------------------
    function el(tag, attrs = {}, parent = null) {
        const node = document.createElementNS(SVG_NS, tag);
        for (const [k, v] of Object.entries(attrs)) {
            if (v !== undefined && v !== null) node.setAttribute(k, String(v));
        }
        if (parent) parent.appendChild(node);
        return node;
    }

    function renderCampusWalkwaysLayer() {
        const layer = document.getElementById("pedestrianWalkwaysLayer");
        if (!layer || layer.dataset.rendered === "true") return;
        layer.dataset.rendered = "true";

        const haloGroup = el("g", {
            fill: "none",
            stroke: "#ffffff",
            "stroke-width": 4.6,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            opacity: 0.9
        }, layer);

        // Draw all walkable micro-segments
        for (const seg of SEGMENTS) {
            const a = NODES[seg.from];
            const b = NODES[seg.to];
            if (!a || !b) continue;
            const d = `M ${a.x} ${a.y} L ${b.x} ${b.y}`;
            el("path", { d }, haloGroup);

            const zoneColor = seg.accessibilityZone === "inaccessible"
                ? "#2563eb"
                : seg.accessibilityZone === "recommended"
                    ? "#f97316"
                    : "#ec4899";
            el("path", {
                d,
                stroke: zoneColor,
                "stroke-width": seg.accessibilityZone === "inaccessible" ? 3 : 2.4,
                "stroke-dasharray": seg.type === "level2" ? "5,3" : seg.type === "indoor" ? "3.5,3.5" : null,
                "stroke-linecap": "round",
                "stroke-linejoin": "round",
                "data-accessibility-zone": seg.accessibilityZone
            }, layer);
        }

        // Draw clean door & corridor portal markers
        const portalsGroup = el("g", { id: "walkwaysPortalsGroup" }, layer);
        for (const p of PORTALS) {
            if (p.kind === "stairs") continue; // Stairs box is shown via barrier/stairs marker below
            const fill = p.kind === "door" ? "#0ea5e9" : "#f472b6";
            el("circle", {
                cx: p.x, cy: p.y, r: 3.3,
                fill, stroke: "#ffffff", "stroke-width": 1.4
            }, portalsGroup);
        }

        // Draw compact 2nd-floor covered bridge badges
        const level2BadgesGroup = el("g", { id: "walkwaysLevel2BadgesGroup" }, layer);
        for (const b of LEVEL2_BADGES) {
            const g = el("g", {}, level2BadgesGroup);
            el("rect", {
                x: b.x - 8.5, y: b.y - 6, width: 17, height: 12, rx: 4,
                fill: "#7c3aed", stroke: "#ffffff", "stroke-width": 1.3
            }, g);
            const txt = el("text", {
                x: b.x, y: b.y + 0.3,
                fill: "#ffffff",
                "data-walkway-badge": b.key,
                "font-family": "'Plus Jakarta Sans', system-ui, sans-serif",
                "font-size": 7.2,
                "font-weight": 800,
                "text-anchor": "middle",
                "dominant-baseline": "central"
            }, g);
            txt.textContent = typeof window.t === "function" ? window.t(b.key) : "";
        }

        // Draw non-passable wall / blocked access X markers
        const barriersGroup = el("g", { id: "walkwaysBarriersGroup" }, layer);
        for (const bar of BARRIERS) {
            const g = el("g", { class: "walkway-barrier-marker" }, barriersGroup);
            el("circle", {
                cx: bar.x, cy: bar.y, r: 6.2,
                fill: "#ffffff", stroke: "#e11d48", "stroke-width": 1.5
            }, g);
            el("path", {
                d: `M ${bar.x - 2.8} ${bar.y - 2.8} L ${bar.x + 2.8} ${bar.y + 2.8} M ${bar.x + 2.8} ${bar.y - 2.8} L ${bar.x - 2.8} ${bar.y + 2.8}`,
                stroke: "#e11d48", "stroke-width": 1.8, "stroke-linecap": "round"
            }, g);
        }

        // Wire Right Toolbar Toggle Button & Compact Light-Theme Legend Pill
        const btnToggle = document.getElementById("btnToggleWalkwaysLayer");
        const legendPill = document.getElementById("walkwaysLegendPill");

        function syncWalkwaysToggleUI(isVisible) {
            layer.classList.toggle("hidden", !isVisible);
            layer.style.display = isVisible ? "" : "none";
            if (legendPill) {
                legendPill.classList.toggle("lg:flex", isVisible);
                legendPill.classList.toggle("hidden", !isVisible);
                legendPill.style.display = isVisible ? "" : "none";
            }
            if (btnToggle) {
                btnToggle.classList.toggle("bg-pink-100", isVisible);
                btnToggle.classList.toggle("hover:bg-pink-200", isVisible);
                btnToggle.classList.toggle("text-pink-700", isVisible);
                btnToggle.classList.toggle("bg-slate-100", !isVisible);
                btnToggle.classList.toggle("hover:bg-slate-200", !isVisible);
                btnToggle.classList.toggle("text-slate-500", !isVisible);
                btnToggle.setAttribute("aria-pressed", String(isVisible));
            }
        }

        if (btnToggle) {
            // Respect initial visibility from button's aria-pressed state (default hidden -> user toggles at will, OR visible if marked true)
            const initialVisible = btnToggle.getAttribute("aria-pressed") === "true";
            syncWalkwaysToggleUI(initialVisible);

            btnToggle.addEventListener("click", () => {
                const currentlyVisible = !layer.classList.contains("hidden");
                syncWalkwaysToggleUI(!currentlyVisible);
            });
        }
    }

    // Export globals for 2D & 2.5D route rendering
    window.CAMPUS_MICRO_WALKWAYS = {
        nodes: NODES,
        segments: SEGMENTS,
        portals: PORTALS,
        barriers: BARRIERS,
        macroToMicro: MACRO_TO_MICRO_NODE
    };
    window.resolveMicroCampusRoute = resolveMicroCampusRoute;
    window.renderCampusWalkwaysLayer = renderCampusWalkwaysLayer;

    window.addEventListener("jaguarLanguageChanged", () => {
        if (typeof window.t !== "function") return;
        document.querySelectorAll("[data-walkway-badge]").forEach((node) => {
            const key = node.getAttribute("data-walkway-badge");
            if (key) node.textContent = window.t(key);
        });
    });

    if (document.getElementById("pedestrianWalkwaysLayer")) {
        renderCampusWalkwaysLayer();
    } else {
        document.addEventListener("DOMContentLoaded", renderCampusWalkwaysLayer);
    }
})();
