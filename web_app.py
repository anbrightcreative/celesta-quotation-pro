import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import io
import zipfile

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="Quotation Pro - An Creative Design", page_icon="🚀")

# --- HÀM XỬ LÝ ĐỒ HỌA ---
def get_lines_and_height(draw, text, font, max_w):
    raw_lines = str(text).split('\n')
    lines = []
    for r_line in raw_lines:
        words = r_line.strip().split()
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_w:
                current_line = test_line
            else:
                if current_line: lines.append(current_line); current_line = word
                else: lines.append(word); current_line = ""
        if current_line: lines.append(current_line)
    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        total_h += (bbox[3] - bbox[1]) + 8 
    return lines, total_h

def draw_text_lines(draw, lines, x, y, font, fill):
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        current_y += (bbox[3] - bbox[1]) + 8

def create_page(bg_image, cols, x_pos, f_h, margin_t, margin_x, W, H):
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(bg_image, (0, 0))
    d = ImageDraw.Draw(canvas)
    max_h = 0
    for idx, col in enumerate(cols):
        draw_x = x_pos[idx]
        lines, h = get_lines_and_height(d, col, f_h, 9999)
        draw_text_lines(d, lines, draw_x, margin_t, f_h, (0,0,0))
        max_h = max(max_h, h)
    line_y = margin_t + max_h + 20
    d.line([(margin_x, line_y), (W - margin_x, line_y)], fill=(0,0,0), width=2)
    return canvas, d, line_y + 20

# 2. HIỂN THỊ BANNER
BANNER_PNG = "brand_banner.png"
if os.path.exists(BANNER_PNG):
    st.image(BANNER_PNG, use_container_width=True)
else:
    st.title("🚀 Quotation Pro - Smart Edition")

st.markdown("---")

# 3. DANH SÁCH CỘT MỚI (Đã đổi tên & Bỏ Ghi chú)
REQUIRED_COLS = [
    "STT", 
    "Tên thuốc", 
    "Tên hoạt chất/thành phần", 
    "Hàm Lượng", 
    "Đường dùng", 
    "Dạng bào chế", 
    "Nhóm thuốc", 
    "Giá dịch vụ (Không BHYT)"
]

st.subheader("📤 Bước 1: Tải lên dữ liệu")
st.info(f"Yêu cầu các cột: {', '.join(REQUIRED_COLS)}")

uploaded_file = st.file_uploader("Chọn file Excel (.xlsx) hoặc CSV (.csv)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        missing_cols = [col for col in REQUIRED_COLS if col not in df_input.columns]
        
        if missing_cols:
            st.error(f"❌ Thiếu cột: {', '.join(missing_cols)}")
        else:
            df = df_input[REQUIRED_COLS].copy()
            st.success(f"✅ Đã sẵn sàng xử lý {len(df)} dòng.")
            
            st.subheader("🖼️ Bước 2: Xuất báo giá")
            if st.button("🚀 BẮT ĐẦU XUẤT ẢNH"):
                bg_path = "Background.jpg"
                font_h_path = "GoogleSansFlex_24pt-Bold.ttf"
                font_b_path = "GoogleSansFlex_24pt-Regular.ttf"
                
                W, H = 1920, 1080
                bg_raw = Image.open(bg_path).convert("RGB").resize((W, H))
                f_h = ImageFont.truetype(font_h_path, 20)
                f_b = ImageFont.truetype(font_b_path, 15)

                margin_t, margin_b, margin_x = 320, 75, 75
                # Độ rộng các cột (đã lược bỏ cột Ghi chú và căn chỉnh lại)
                col_w = [60, 320, 380, 200, 200, 180, 180, 200]
                x_pos = []
                curr_x = margin_x
                for w in col_w:
                    x_pos.append(curr_x); curr_x += w

                NO_WRAP = ["Tên hoạt chất/thành phần", "Hàm Lượng", "Đường dùng", "Dạng bào chế", "Nhóm thuốc"]
                output_images = []
                page_num = 1
                img, draw, curr_y = None, None, 0
                progress_bar = st.progress(0)
                dummy_img = Image.new('RGB', (W, H))
                dummy_draw = ImageDraw.Draw(dummy_img)

                for index, row in df.reset_index(drop=True).iterrows():
                    r_lines, r_max_h = [], 0
                    for idx, col in enumerate(REQUIRED_COLS):
                        val = str(row.get(col, '')).strip()
                        if val.lower() == 'nan': val = ""
                        if 'Giá' in col:
                            try: val = f"{int(float(val)):,} VND" if val else ""
                            except: pass
                        
                        m_w = col_w[idx] - 60 if col not in NO_WRAP else 9999
                        lines, h = get_lines_and_height(dummy_draw, val, f_b, m_w)
                        r_lines.append(lines); r_max_h = max(r_max_h, h)

                    if img is None or (curr_y + r_max_h + 40 > H - margin_b):
                        if img is not None:
                            output_images.append((img, f"Page_{page_num}.jpg"))
                            page_num += 1
                        img, draw, curr_y = create_page(bg_raw, REQUIRED_COLS, x_pos, f_h, margin_t, margin_x, W, H)

                    for idx, lines in enumerate(r_lines):
                        draw_text_lines(draw, lines, x_pos[idx], curr_y, f_b, (0,0,0))
                    
                    l_y = curr_y + r_max_h + 20
                    draw.line([(margin_x, l_y), (W - margin_x, l_y)], fill=(0,0,0), width=1)
                    curr_y = l_y + 20
                    
                    if index == len(df) - 1:
                        output_images.append((img, f"Page_{page_num}.jpg"))
                    progress_bar.progress((index + 1) / len(df))

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for pil_img, name in output_images:
                        img_byte_arr = io.BytesIO()
                        pil_img.save(img_byte_arr, format='JPEG', quality=95)
                        zip_file.writestr(name, img_byte_arr.getvalue())
                
                st.download_button(label="📥 TẢI XUỐNG FILE .ZIP", data=zip_buffer.getvalue(), file_name="Bao_Gia_Output.zip", mime="application/zip")

    except Exception as e:
        st.error(f"Lỗi: {e}")

# 4. CREDIT
st.markdown("<br><br>---", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: gray; font-size: 14px;">© 2026 - Created by <b>ànBright s\'more creative</b> - exclusive for <b>Celesta Pharma</b></div>', unsafe_allow_html=True)
