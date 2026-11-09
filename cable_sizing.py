import math

def calculate_dc_cable(i_sc, length_m, v_mp_string, k_t=0.91, k_g=0.80):
    """
    คำนวณขนาดสายไฟฟ้า DC (Solar Cable) และ % Voltage Drop
    - พิกัดกระแสสาย: I_design = 1.25 * I_sc
    - เกณฑ์แรงดันตก (%VDc): <= 1.0% ตามมาตรฐาน วสท.
    """
    i_design = 1.25 * i_sc
    i_required = i_design / (k_t * k_g)

    # เลือกขนาดสาย DC (4 sq.mm หรือ 6 sq.mm)
    if i_required <= 55:
        selected_size = 4.0
        r_dc = 5.09
    else:
        selected_size = 6.0
        r_dc = 3.39

    # คำนวณ แรงดันตก (คิดสายไป-กลับ: 2 * Length)
    v_drop = (2 * i_sc * length_m * r_dc) / 1000.0
    v_drop_percent = (v_drop / v_mp_string) * 100.0

    return {
        "i_design": round(i_design, 2),
        "selected_size_sqmm": selected_size,
        "v_drop_v": round(v_drop, 2),
        "v_drop_percent": round(v_drop_percent, 2),
        "pass_vd": v_drop_percent <= 1.0
    }

def calculate_ac_cable(p_ac_kw, length_m, v_ac_line=400.0, pf=1.0, k_t=0.87, k_g=0.80):
    """
    คำนวณขนาดสายไฟฟ้า AC (3-Phase) และ % Voltage Drop
    - I_ac = P_ac / (sqrt(3) * V_line * PF)
    - เกณฑ์แรงดันตก (%VAc): <= 1.5%
    """
    i_ac_rated = (p_ac_kw * 1000.0) / (math.sqrt(3) * v_ac_line * pf)
    i_design = 1.25 * i_ac_rated
    i_required = i_design / (k_t * k_g)

    # ตารางเลือกขนาดสาย AC มาตรฐาน (IEC 01)
    if i_required <= 32:
        selected_size, r_ac = 4.0, 5.52
    elif i_required <= 41:
        selected_size, r_ac = 6.0, 3.68
    elif i_required <= 57:
        selected_size, r_ac = 10.0, 2.22
    else:
        selected_size, r_ac = 16.0, 1.40

    v_drop = (math.sqrt(3) * i_ac_rated * length_m * r_ac) / 1000.0
    v_drop_percent = (v_drop / v_ac_line) * 100.0

    return {
        "i_ac_rated": round(i_ac_rated, 2),
        "i_design": round(i_design, 2),
        "selected_size_sqmm": selected_size,
        "v_drop_v": round(v_drop, 2),
        "v_drop_percent": round(v_drop_percent, 2),
        "pass_vd": v_drop_percent <= 1.5
    }