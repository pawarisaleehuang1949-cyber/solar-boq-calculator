import math

def calculate_racking_components(n_panels, roof_type="Metal Sheet"):
    """
    คำนวณปริมาณอุปกรณ์โครงสร้างยึดแผงโซลาร์เซลล์ (Racking & Mounting)
    """
    if n_panels <= 0:
        return {}

    # 1. ปริมาณรางอลูมิเนียม (ความยาวรางมาตรฐาน 4.2 เมตร ติดตั้งแผงเรียงแถว)
    # สมมติ 1 รางยาว 2.1 ม. รองรับได้ 2 แผงแนวตั้ง
    rails_qty = math.ceil(n_panels * 2)

    # 2. ปริมาณ Mid Clamp (ตัวยึดระหว่างแผง) = (จำนวนแผง - 1) * 2
    mid_clamp_qty = (n_panels - 1) * 2 if n_panels > 1 else 0

    # 3. ปริมาณ End Clamp (ตัวยึดขอบแผง) = 4 ตัวต่อแถว
    end_clamp_qty = 4

    # 4. เลือกประเภทขายึดหลังคาตามชนิดหลังคา
    fastener_name = "L-Feet Mount (สำหรับ Metal Sheet)"
    unit_price_fastener = 65

    if roof_type == "CPAC / Tile Roof":
        fastener_name = "Tile Roof Hook (สำหรับกระเบื้องซีแพค)"
        unit_price_fastener = 120
    elif roof_type == "Kliplok / Standing Seam":
        fastener_name = "Kliplok Clamp (ไม่เจาะหลังคา)"
        unit_price_fastener = 180

    fastener_qty = n_panels * 2  # ระยะยึดเฉลี่ย 2 จุดต่อแผง

    return {
        "roof_type": roof_type,
        "rails_qty": rails_qty,
        "mid_clamp_qty": mid_clamp_qty,
        "end_clamp_qty": end_clamp_qty,
        "fastener_name": fastener_name,
        "fastener_qty": fastener_qty,
        "fastener_unit_price": unit_price_fastener
    }