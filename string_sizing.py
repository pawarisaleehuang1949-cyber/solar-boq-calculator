import math

def calculate_string_limits(pv_module, inverter, t_min=15, t_max_cell=70):
    voc_stc = pv_module['v_oc_v']
    gamma_voc = pv_module['temp_coeff_voc_percent_c']
    voc_tmin = voc_stc * (1 + (gamma_voc / 100.0) * (t_min - 25))

    vmp_stc = pv_module['v_mp_v']
    vmp_tmax = vmp_stc * (1 + (gamma_voc / 100.0) * (t_max_cell - 25))

    v_dc_max = inverter['max_dc_voltage_v']
    v_mppt_min = inverter['mppt_voltage_range_v'][0]

    n_s_max = math.floor(v_dc_max / voc_tmin)
    n_s_min = math.ceil(v_mppt_min / vmp_tmax)

    return {
        "voc_tmin": round(voc_tmin, 2),
        "vmp_tmax": round(vmp_tmax, 2),
        "n_s_max": n_s_max,
        "n_s_min": n_s_min
    }