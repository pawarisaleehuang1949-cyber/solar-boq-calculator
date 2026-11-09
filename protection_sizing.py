def calculate_protection(i_sc_pv, max_fuse_rating, i_ac_rated, n_parallel_strings=1):
    """
    คำนวณพิกัดอุปกรณ์ป้องกัน DC Fuse และ AC Breaker
    """
    # 1. DC Fuse (จำเป็นเมื่อ String ขนานกันตั้งแต่ 3 ชุดขึ้นไป)
    need_dc_fuse = n_parallel_strings >= 3
    dc_fuse_rating = 0
    if need_dc_fuse:
        calc_fuse = 1.5 * i_sc_pv
        standard_fuses = [15, 20, 25, 30]
        dc_fuse_rating = min([f for f in standard_fuses if f >= calc_fuse], default=max_fuse_rating)

    # 2. AC Breaker (MCCB/MCB)
    i_cb_calc = 1.25 * i_ac_rated
    standard_breakers = [16, 20, 25, 32, 40, 50, 63, 80]
    ac_cb_rating = min([b for b in standard_breakers if b >= i_cb_calc], default=100)

    return {
        "need_dc_fuse": need_dc_fuse,
        "dc_fuse_rating_a": dc_fuse_rating,
        "ac_cb_rating_a": ac_cb_rating,
        "dc_spd": "DC SPD Type 2 (1000V DC)",
        "ac_spd": "AC SPD Type 2 (400V AC 3P+N)"
    }