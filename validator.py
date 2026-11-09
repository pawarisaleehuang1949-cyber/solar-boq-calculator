def validate_solar_system(pv_module, inverter, n_string_series, n_parallel_strings, dc_vd_pct, ac_vd_pct):
    """
    ตรวจสอบเงื่อนไขความปลอดภัยและมาตรฐานวิศวกรรมไฟฟ้า Solar PV
    """
    warnings = []
    errors = []

    # 1. ตรวจสอบแรงดัน Voc Max (ที่ 15°C) ไม่เกิน Max DC Voltage ของ Inverter
    voc_stc = pv_module['v_oc_v']
    gamma_voc = pv_module['temp_coeff_voc_percent_c']
    voc_tmin = voc_stc * (1 + (gamma_voc / 100.0) * (15 - 25))
    total_voc_max = voc_tmin * n_string_series

    if total_voc_max > inverter['max_dc_voltage_v']:
        errors.append(f"❌ แรงดัน Voc รวมสูงสุด ({total_voc_max:.1f} V) เกินพิกัด Inverter ({inverter['max_dc_voltage_v']} V)")

    # 2. ตรวจสอบช่วงแรงดัน Vmp Min (ที่ 70°C) ให้อยู่ในช่วง MPPT Voltage Range
    vmp_stc = pv_module['v_mp_v']
    vmp_tmax = vmp_stc * (1 + (gamma_voc / 100.0) * (70 - 25))
    total_vmp_min = vmp_tmax * n_string_series

    mppt_min = inverter['mppt_voltage_range_v'][0]
    mppt_max = inverter['mppt_voltage_range_v'][1]

    if total_vmp_min < mppt_min:
        warnings.append(f"⚠️ แรงดัน Vmp ต่ำสุด ({total_vmp_min:.1f} V) ต่ำกว่าช่วงทำงาน MPPT ({mppt_min} V)")
    elif total_vmp_min > mppt_max:
        warnings.append(f"⚠️ แรงดัน Vmp สูงสุด เกินช่วง MPPT ({mppt_max} V)")

    # 3. ตรวจสอบกระแส Isc เกินพิกัด Max MPPT Current
    total_isc = pv_module['i_sc_a'] * n_parallel_strings
    if total_isc > inverter['max_mppt_current_a']:
        errors.append(f"❌ กระแส Isc รวม ({total_isc:.2f} A) เกินพิกัดรองรับของ MPPT ({inverter['max_mppt_current_a']} A)")

    # 4. ตรวจสอบ % Voltage Drop ตามเกณฑ์ วสท.
    if dc_vd_pct > 1.0:
        warnings.append(f"⚠️ แรงดันตกฝั่ง DC ({dc_vd_pct:.2f}%) เกินเกณฑ์มาตรฐาน 1.0%")
    if ac_vd_pct > 1.5:
        warnings.append(f"⚠️ แรงดันตกฝั่ง AC ({ac_vd_pct:.2f}%) เกินเกณฑ์มาตรฐาน 1.5%")

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "total_voc_max": round(total_voc_max, 1),
        "total_vmp_min": round(total_vmp_min, 1)
    }