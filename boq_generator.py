import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_boq_excel(pv_info, inv_info, dc_cable_info, ac_cable_info, prot_info, 
                       n_panels, dc_length_m, ac_length_m, labor_percent=15, 
                       output_path="outputs/Solar_PV_BOQ_Report.xlsx"):
    """
    สร้างไฟล์ Excel รายงาน BOQ พร้อมจัดรูปแบบและใส่สูตรคำนวณอัตโนมัติ
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BOQ Solar PV"
    ws.views.sheetView[0].showGridLines = True

    # 1. การกำหนดรูปแบบสไตล์ (Styles)
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=16, bold=True, color="1F497D")
    sub_title_font = Font(name="Calibri", size=11, italic=True, color="595959")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    section_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    total_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    double_bottom_border = Border(
        top=Side(style='thin', color='000000'),
        bottom=Side(style='double', color='000000')
    )

    # 2. หัวข้อรายงาน (Report Header)
    ws['A1'] = "ใบถอดปริมาณงานและประมาณราคา (Bill of Quantities - BOQ)"
    ws['A1'].font = title_font
    ws['A2'] = f"ระบบผลิตพลังงานไฟฟ้าจากเซลล์แสงอาทิตย์ (Solar PV System) ขนาด {(n_panels * pv_info['p_max_w'])/1000:.2f} kWp"
    ws['A2'].font = sub_title_font

    # 3. กำหนดหัวตาราง (Table Headers)
    headers = ["ลำดับ", "รายการอุปกรณ์ / งาน", "จำนวน", "หน่วย", "ราคา/หน่วย (บาท)", "ราคารวมอุปกรณ์ (บาท)"]
    start_row = 4
    for col_idx, text in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_idx, value=text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # 4. รายการอุปกรณ์ (BOQ Items)
    # คำนวณปริมาณ Racking และท่อร้อยสายไฟเบื้องต้น
    racking_qty = n_panels
    mid_clamp_qty = (n_panels - 1) * 2 if n_panels > 1 else 2
    end_clamp_qty = 4
    dc_conduit_qty = round(dc_length_m * 1.1)  # คิด เผื่อ 10%
    ac_conduit_qty = round(ac_length_m * 1.1)

    items_data = [
        # (ประเภท, ลำดับ, รายการ, ปริมาณ, หน่วย, ราคาต่อหน่วย)
        ("SEC", "1", "หมวดงานแผงเซลล์แสงอาทิตย์และอินเวอร์เตอร์", "", "", ""),
        ("ITEM", "1.1", f"แผงโซลาร์เซลล์ {pv_info['brand']} {pv_info['model']} {pv_info['p_max_w']}W", n_panels, "แผง", pv_info['unit_price_thb']),
        ("ITEM", "1.2", f"อินเวอร์เตอร์ {inv_info['brand']} {inv_info['model']} {inv_info['rated_ac_power_kw']}kW", 1, "เครื่อง", inv_info['unit_price_thb']),
        
        ("SEC", "2", "หมวดงานโครงสร้างรองรับแผง (Racking & Mounting)", "", "", ""),
        ("ITEM", "2.1", "ชุดรางอลูมิเนียมยึดแผงโซลาร์เซลล์ (Aluminum Rail)", racking_qty, "ชุด", 450),
        ("ITEM", "2.2", "อุปกรณ์ยึดกลางแผง (Mid Clamp)", mid_clamp_qty, "ตัว", 35),
        ("ITEM", "2.3", "อุปกรณ์ยึดขอบแผง (End Clamp)", end_clamp_qty, "ตัว", 35),
        ("ITEM", "2.4", "อุปกรณ์ยึดหลังคา (L-Feet / Roof Fastener)", racking_qty * 2, "ชุด", 65),

        ("SEC", "3", "หมวดงานระบบสายไฟฟ้าและท่อร้อยสาย", "", "", ""),
        ("ITEM", "3.1", f"สายไฟ DC Solar Cable {dc_cable_info['selected_size_sqmm']} sq.mm", dc_length_m * 2, "เมตร", 40),
        ("ITEM", "3.2", f"สายไฟ AC {ac_cable_info['selected_size_sqmm']} sq.mm (4 Core)", ac_length_m, "เมตร", 120),
        ("ITEM", "3.3", "ท่อร้อยสายไฟ DC (HDPE / Conduit)", dc_conduit_qty, "เมตร", 45),
        ("ITEM", "3.4", "ท่อร้อยสายไฟ AC (uPVC / EMT)", ac_conduit_qty, "เมตร", 55),

        ("SEC", "4", "หมวดงานระบบป้องกันและตู้ไฟฟ้า (Protection Panel)", "", "", ""),
        ("ITEM", "4.1", f"AC Circuit Breaker 3P {prot_info['ac_cb_rating_a']}A", 1, "ชุด", 2500),
        ("ITEM", "4.2", "Surge Protective Device (DC/AC SPD)", 2, "ชุด", 1800),
        ("ITEM", "4.3", "ตู้ควบคุมไฟฟ้าพร้อมอุปกรณ์ประกอบ (Combiner Enclosure)", 1, "ตู้", 4500)
    ]

    current_row = 5
    item_rows = []

    for item in items_data:
        if item[0] == "SEC":
            # แถวหัวข้อหมวด
            ws.cell(row=current_row, column=1, value=item[1]).font = bold_font
            ws.cell(row=current_row, column=2, value=item[2]).font = bold_font
            for c in range(1, 7):
                ws.cell(row=current_row, column=c).fill = section_fill
        else:
            # แถวรายการอุปกรณ์
            ws.cell(row=current_row, column=1, value=item[1]).alignment = Alignment(horizontal="center")
            ws.cell(row=current_row, column=2, value=item[2])
            ws.cell(row=current_row, column=3, value=item[3]).number_format = '#,##0'
            ws.cell(row=current_row, column=4, value=item[4]).alignment = Alignment(horizontal="center")
            ws.cell(row=current_row, column=5, value=item[5]).number_format = '#,##0.00'
            
            # ใส่สูตรคำนวณราคารวมอุปกรณ์ = ปริมาณ * ราคาต่อหน่วย
            formula = f"=C{current_row}*E{current_row}"
            ws.cell(row=current_row, column=6, value=formula).number_format = '#,##0.00'
            
            item_rows.append(current_row)

        for c in range(1, 7):
            ws.cell(row=current_row, column=c).border = thin_border
            if item[0] == "ITEM":
                ws.cell(row=current_row, column=c).font = regular_font

        current_row += 1

    # 5. แถวสรุปมูลค่า (Subtotals & Summary)
    # รวมราคาอุปกรณ์ทั้งหมด
    sum_start = item_rows[0]
    sum_end = item_rows[-1]
    
    ws.cell(row=current_row, column=2, value="รวมราคาค่าอุปกรณ์ทั้งหมด (Total Material Cost)").font = bold_font
    ws.cell(row=current_row, column=6, value=f"=SUM(F{sum_start}:F{sum_end})").font = bold_font
    ws.cell(row=current_row, column=6).number_format = '#,##0.00'
    ws.cell(row=current_row, column=6).fill = total_fill
    mat_sum_row = current_row
    current_row += 1

    # คิดค่าแรงติดตั้ง (% ของราคาอุปกรณ์)
    ws.cell(row=current_row, column=2, value=f"ค่าแรงติดตั้ง ทดสอบ และดำเนินงาน ({labor_percent}%)").font = bold_font
    ws.cell(row=current_row, column=6, value=f"=F{mat_sum_row}*({labor_percent}/100)").font = bold_font
    ws.cell(row=current_row, column=6).number_format = '#,##0.00'
    labor_sum_row = current_row
    current_row += 1

    # รวมเป็นเงินก่อนภาษี
    ws.cell(row=current_row, column=2, value="รวมเป็นเงินทั้งสิ้นก่อนภาษีมูลค่าเพิ่ม (Subtotal)").font = bold_font
    ws.cell(row=current_row, column=6, value=f"=F{mat_sum_row}+F{labor_sum_row}").font = bold_font
    ws.cell(row=current_row, column=6).number_format = '#,##0.00'
    subtotal_row = current_row
    current_row += 1

    # ภาษีมูลค่าเพิ่ม (VAT 7%)
    ws.cell(row=current_row, column=2, value="ภาษีมูลค่าเพิ่ม (VAT 7%)").font = bold_font
    ws.cell(row=current_row, column=6, value=f"=F{subtotal_row}*0.07").font = bold_font
    ws.cell(row=current_row, column=6).number_format = '#,##0.00'
    vat_row = current_row
    current_row += 1

    # ราคารวมสุทธิ (Grand Total)
    ws.cell(row=current_row, column=2, value="ราคารวมสุทธิทั้งสิ้น (Grand Total)").font = Font(name="Calibri", size=12, bold=True, color="1F497D")
    grand_cell = ws.cell(row=current_row, column=6, value=f"=F{subtotal_row}+F{vat_row}")
    grand_cell.font = Font(name="Calibri", size=12, bold=True, color="1F497D")
    grand_cell.number_format = '#,##0.00'
    grand_cell.border = double_bottom_border
    grand_cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

    # 6. ปรับขนาดความกว้างคอลัมน์อัตโนมัติ
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    ws.column_dimensions['B'].width = 50  # ปรับความกว้างช่องรายการอุปกรณ์เป็นพิเศษ

    # บันทึกไฟล์ Excel
    wb.save(output_path)
    return output_path