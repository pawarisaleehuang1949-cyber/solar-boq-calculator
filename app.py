import json
import os
import streamlit as st
from string_sizing import calculate_string_limits
from cable_sizing import calculate_dc_cable, calculate_ac_cable
from protection_sizing import calculate_protection
from racking_sizing import calculate_racking_components
from boq_generator import generate_boq_excel
from validator import validate_solar_system

st.set_page_config(page_title="Solar PV BOQ System", layout="wide")
st.title("ระบบถอดปริมาณงาน BOQ สำหรับ Solar PV")

# 1. โหลดข้อมูล Catalog
try:
   with open('catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
except Exception as e:
    st.error(f"ไม่สามารถอ่าน catalog.json ได้: {e}")

if 'catalog' in locals():
    # Sidebar พารามิเตอร์การวางระบบ
    st.sidebar.header("🎯 1. เลือกอุปกรณ์ในระบบ")
    pv_options = {f"{p['brand']} {p['model']} ({p['p_max_w']}W)": p for p in catalog['pv_modules']}
    selected_pv_name = st.sidebar.selectbox("เลือกแผงโซลาร์เซลล์", list(pv_options.keys()))
    pv = pv_options[selected_pv_name]

    inv_options = {f"{i['brand']} {i['model']} ({i['rated_ac_power_kw']}kW)": i for i in catalog['inverters']}
    selected_inv_name = st.sidebar.selectbox("เลือกอินเวอร์เตอร์", list(inv_options.keys()))
    inv = inv_options[selected_inv_name]

    st.sidebar.header("⚙️ 2. พารามิเตอร์การติดตั้ง")
    n_strings_parallel = st.sidebar.number_input("จำนวน String ที่ต่อขนาน", min_value=1, max_value=4, value=1)
    roof_type = st.sidebar.selectbox("ประเภทหลังคา", ["Metal Sheet", "CPAC / Tile Roof", "Kliplok / Standing Seam"])
    dc_len = st.sidebar.slider("ความยาวสาย DC String (เมตร)", 10, 150, 30)
    ac_len = st.sidebar.slider("ความยาวสาย AC (Inverter -> MDB) (เมตร)", 5, 100, 25)
    labor_pct = st.sidebar.slider("คิดอัตราค่าแรงติดตั้ง (% ของค่าอุปกรณ์)", 10, 30, 15)

    # 2. ประมวลผลคำนวณทางวิศวกรรม
    string_res = calculate_string_limits(pv, inv)
    n_s = string_res['n_s_max']
    v_mp_string = n_s * pv['v_mp_v']

    dc_cable_res = calculate_dc_cable(pv['i_sc_a'], dc_len, v_mp_string)
    ac_cable_res = calculate_ac_cable(inv['rated_ac_power_kw'], ac_len)
    prot_res = calculate_protection(pv['i_sc_a'], pv['max_series_fuse_rating_a'], ac_cable_res['i_ac_rated'], n_strings_parallel)
    racking_res = calculate_racking_components(n_s * n_strings_parallel, roof_type)

    # 3. ตรวจสอบเงื่อนไขวิศวกรรม (Validation)
    val_res = validate_solar_system(
        pv_module=pv,
        inverter=inv,
        n_string_series=n_s,
        n_parallel_strings=n_strings_parallel,
        dc_vd_pct=dc_cable_res['v_drop_percent'],
        ac_vd_pct=ac_cable_res['v_drop_percent']
    )

    # แสดงข้อความแจ้งเตือนผลการตรวจสอบ
    if not val_res['is_valid']:
        for err in val_res['errors']:
            st.error(err)
    else:
        st.success("✅ ระบบผ่านการตรวจสอบเงื่อนไขความปลอดภัยทางไฟฟ้าตามมาตรฐาน")

    for warn in val_res['warnings']:
        st.warning(warn)

    # 4. จัดการ Tabs แสดงผล
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 String Sizing", 
        "🔌 สายไฟฟ้า & Voltage Drop", 
        "🛡️ อุปกรณ์ป้องกัน", 
        "🏗️ โครงสร้างยึดแผง",
        "📊 ถอดปริมาณ BOQ & ส่งออก Excel",
        "📈 วิเคราะห์ต้นทุนโครงการ"
    ])

    with tab1:
        st.subheader("ผลการจัด String แผงโซลาร์เซลล์")
        col1, col2, col3 = st.columns(3)
        col1.metric("จำนวนแผงอนุกรมสูงสุด (Ns Max)", f"{string_res['n_s_max']} แผง")
        col2.metric("Voc รวมสูงสุด (ที่ 15°C)", f"{val_res['total_voc_max']} V")
        col3.metric("Vmp รวมต่ำสุด (ที่ 70°C)", f"{val_res['total_vmp_min']} V")

    with tab2:
        st.subheader("คำนวณสายไฟฟ้าและการควบคุมแรงดันตก (Voltage Drop)")
        c1, c2 = st.columns(2)
        with c1:
            st.info("### ฝั่ง DC (Solar Cable)")
            st.write(f"- ขนาดสายที่เลือก: **{dc_cable_res['selected_size_sqmm']} sq.mm**")
            st.write(f"- แรงดันตก: **{dc_cable_res['v_drop_percent']}%** ({dc_cable_res['v_drop_v']} V)")
        with c2:
            st.info("### ฝั่ง AC (Inverter to MDB)")
            st.write(f"- กระแสพิกัด AC: **{ac_cable_res['i_ac_rated']} A**")
            st.write(f"- ขนาดสายที่เลือก: **{ac_cable_res['selected_size_sqmm']} sq.mm**")
            st.write(f"- แรงดันตก: **{ac_cable_res['v_drop_percent']}%** ({ac_cable_res['v_drop_v']} V)")

    with tab3:
        st.subheader("อุปกรณ์ป้องกันไฟฟ้าระบบ Solar PV")
        st.write(f"- **DC Fuse Protection:** {'จำเป็นต้องใส่ขนาด ' + str(prot_res['dc_fuse_rating_a']) + 'A' if prot_res['need_dc_fuse'] else 'ไม่ต้องใส่ DC Fuse (ต่อขนาน < 3 String)'}")
        st.write(f"- **AC Circuit Breaker:** ขนาด **{prot_res['ac_cb_rating_a']} A** 3P")

    with tab4:
        st.subheader(f"🏗️ การถอดปริมาณอุปกรณ์โครงสร้างยึดแผง ({racking_res['roof_type']})")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("รางอลูมิเนียม (Rails)", f"{racking_res['rails_qty']} เส้น")
        r2.metric("Mid Clamp", f"{racking_res['mid_clamp_qty']} ตัว")
        r3.metric("End Clamp", f"{racking_res['end_clamp_qty']} ตัว")
        r4.metric(racking_res['fastener_name'], f"{racking_res['fastener_qty']} ชุด")

    with tab5:
        st.subheader("📋 สรุปประมาณราคาและถอดปริมาณงาน (BOQ Summary)")
        total_panels = n_s * n_strings_parallel
        total_kwp = (total_panels * pv['p_max_w']) / 1000.0
        mat_cost = (total_panels * pv['unit_price_thb']) + inv['unit_price_thb'] + (dc_len * 2 * 40) + (ac_len * 120) + 15000
        labor_cost = mat_cost * (labor_pct / 100.0)
        grand_total = (mat_cost + labor_cost) * 1.07

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ขนาดติดตั้งรวม", f"{total_kwp:.2f} kWp")
        m2.metric("ค่าอุปกรณ์รวม", f"{mat_cost:,.2f} บาท")
        m3.metric(f"ค่าแรงติดตั้ง ({labor_pct}%)", f"{labor_cost:,.2f} บาท")
        m4.metric("ราคารวมสุทธิ (รวม VAT)", f"{grand_total:,.2f} บาท")

        st.divider()
        os.makedirs("outputs", exist_ok=True)
        excel_file_path = "outputs/Solar_PV_BOQ_Report.xlsx"

        if st.button("🚀 สร้างไฟล์รายงาน BOQ (.xlsx)", type="primary"):
            generate_boq_excel(
                pv_info=pv,
                inv_info=inv,
                dc_cable_info=dc_cable_res,
                ac_cable_info=ac_cable_res,
                prot_info=prot_res,
                n_panels=total_panels,
                dc_length_m=dc_len,
                ac_length_m=ac_len,
                labor_percent=labor_pct,
                output_path=excel_file_path
            )
            st.success("สร้างไฟล์รายงาน BOQ สำเร็จแล้ว!")

        if os.path.exists(excel_file_path):
            with open(excel_file_path, "rb") as file:
                st.download_button(
                    label="💾 คลิกเพื่อดาวน์โหลดไฟล์ BOQ Excel",
                    data=file,
                    file_name="Solar_PV_BOQ_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with tab6:
        st.subheader("📈 ดัชนีชี้วัดทางเศรษฐศาสตร์เบื้องต้น (Financial Key Metrics)")
        total_panels = n_s * n_strings_parallel
        total_kwp = (total_panels * pv['p_max_w']) / 1000.0
        mat_cost = (total_panels * pv['unit_price_thb']) + inv['unit_price_thb'] + (dc_len * 2 * 40) + (ac_len * 120) + 15000
        grand_total = (mat_cost * (1 + labor_pct/100.0)) * 1.07

        cost_per_watt = grand_total / (total_kwp * 1000.0)
        est_annual_yield_kwh = total_kwp * 1400  # สมมติค่าเฉลี่ยความเข้มแสงไทย 1,400 kWh/kWp/ปี
        est_annual_saving_thb = est_annual_yield_kwh * 4.30  # สมมติค่าไฟฟ้าเฉลี่ย 4.30 บาท/หน่วย
        payback_years = grand_total / est_annual_saving_thb if est_annual_saving_thb > 0 else 0

        f1, f2, f3 = st.columns(3)
        f1.metric("ต้นทุนติดตั้งต่อวัตต์ (THB/Wp)", f"{cost_per_watt:.2f} บาท/Wp")
        f2.metric("ประมาณการประหยัดค่าไฟฟ้า/ปี", f"{est_annual_saving_thb:,.2f} บาท/ปี")
        f3.metric("ระยะเวลาคืนทุนโดยประมาณ (Payback)", f"{payback_years:.1f} ปี")
