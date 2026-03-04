import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import io
import zipfile

# Cấu hình trang
st.set_page_config(page_title="Quotation Pro - Celesta Pharma", page_icon="💊")

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
        if idx == 8: draw_x += 75
        lines, h = get_lines_and_height(d, col, f_h, 9999)
        draw_text_lines(d, lines, draw_x, margin_t, f_h, (0,0,0))
        max_h = max(max_h, h)
    line_y = margin_t + max_h + 20
    d.line([(margin_x, line_y), (W - margin_x, line_y)], fill=(0,0,0), width=2)
    return canvas, d, line_y + 20

# --- PHẦN HIỂN THỊ BANNER THƯƠNG HIỆU ---

# Danh sách các file banner anh có thể dùng (ưu tiên PNG để có nền trong suốt)
BANNER_PNG = "brand_banner.png"
BANNER_JPG = "brand_banner.jpg"

if os.path.exists(BANNER_PNG):
    st.image(BANNER_PNG, use_container_width=True)
elif os.path.exists(BANNER_JPG):
    st.image(BANNER_JPG, use_container_width=True)
else:
    st.title("💊 Quotation Pro - Auto Design")
    st.markdown("Hệ thống tạo báo giá tự động chuyên nghiệp.")

st.markdown("---")


# --- BƯỚC 1: TẢI FILE MẪU ---
st.subheader("1️⃣ Bước 1: Tải file cấu trúc data mẫu")
st.info("Nhấn nút bên dưới để tải file cấu trúc chuẩn về máy.")

template_cols = ["STT", "Tên sản phẩm", "Tên hoạt chất/thành phần", "Hàm Lượng", "Đường dùng", "Dạng bào chế", "Nhóm thuốc", "Giá dịch vụ"]
df_template = pd.DataFrame(columns=template_cols)
df_template.loc[0] = ["1", "Tên thuốc ví dụ", "Hoạt chất A", "500mg", "Uống", "Viên nén", "Kháng sinh", "150000"]

csv_template = df_template.to_csv(index=False).encode('utf-8-sig')

st.download_button(
    label="📥 Tải file data.csv mẫu",
    data=csv_template,
    file_name="data.csv",
    mime="text/csv"
)

st.warning("⚠️ **Lưu ý:** Sau khi tải về và nhập thông tin, anh/chị vui lòng giữ nguyên tên file là **data.csv** để hệ thống xử lý chính xác nhất.")

st.markdown("---")

# --- BƯỚC 2: UP FILE DATA VỪA NHẬP THÔNG TIN ---
st.subheader("2️⃣ Bước 2: Tải lên dữ liệu đã nhập")
st.write("Sau khi đã nhập dữ liệu vào file `data.csv`, hãy kéo thả file đó vào đây.")

uploaded_file = st.file_uploader("Yêu cầu file: data.csv", type=["csv"])

if uploaded_file is not None:
    # Kiểm tra tên file (tùy chọn, để nhắc nhở user)
    if uploaded_file.name != "data.csv":
        st.error(f"Tên file đang là '{uploaded_file.name}'. Vui lòng đổi tên đúng thành 'data.csv' để tránh lỗi định dạng.")
    
    st.success("Đã nạp file dữ liệu thành công!")
    if st.button("🚀 XUẤT BÁO GIÁ (DẠNG ẢNH)"):
        try:
            bg_path = "Background.jpg"
            font_h_path = "GoogleSansFlex_24pt-Bold.ttf"
            font_b_path = "GoogleSansFlex_24pt-Regular.ttf"
            
            if not os.path.exists(bg_path):
                st.error("Không tìm thấy file Background.jpg!")
                st.stop()

            df = pd.read_csv(uploaded_file)
            df.dropna(how='all', inplace=True)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            cols = df.columns.tolist()[:9]

            W, H = 1920, 1080
            bg_raw = Image.open(bg_path).convert("RGB").resize((W, H))
            f_h = ImageFont.truetype(font_h_path, 20)
            f_b = ImageFont.truetype(font_b_path, 15)

            margin_t, margin_b, margin_x = 320, 75, 75
            col_w = [60, 280, 340, 170, 170, 150, 155, 140, 280]
            x_pos = []
            curr_x = margin_x
            for w in col_w:
                x_pos.append(curr_x); curr_x += w

            NO_WRAP = ["Tên hoạt chất/thành phần", "Hàm Lượng", "Đường dùng", "Dạng bào chế", "Nhóm thuốc"]
            
            output_images = []
            page_num = 1
            dummy_img = Image.new('RGB', (W, H))
            dummy_draw = ImageDraw.Draw(dummy_img)
            img, draw, curr_y = None, None, 0

            progress_bar = st.progress(0)
            status_text = st.empty()
            total_rows = len(df)

            for index, row in df.reset_index(drop=True).iterrows():
                r_lines, r_max_h = [], 0
                for idx, col in enumerate(cols):
                    val = str(row.get(col, '')).strip()
                    if val.lower() == 'nan': val = ""
                    if 'Giá' in col:
                        try: val = f"{int(float(val)):,} VND" if val else ""
                        except: pass
                    m_w = col_w[idx] - 70 if col not in NO_WRAP else 9999
                    lines, h = get_lines_and_height(dummy_draw, val, f_b, m_w)
                    r_lines.append(lines); r_max_h = max(r_max_h, h)

                if img is None or (curr_y + r_max_h + 40 > H - margin_b):
                    if img is not None:
                        output_images.append((img, f"Page_{page_num}.jpg"))
                        page_num += 1
                    img, draw, curr_y = create_page(bg_raw, cols, x_pos, f_h, margin_t, margin_x, W, H)

                for idx, lines in enumerate(r_lines):
                    dx = x_pos[idx]
                    if idx == 8: dx += 75
                    draw_text_lines(draw, lines, dx, curr_y, f_b, (0,0,0))
                l_y = curr_y + r_max_h + 20
                draw.line([(margin_x, l_y), (W - margin_x, l_y)], fill=(0,0,0), width=1)
                curr_y = l_y + 20
                
                if index == total_rows - 1:
                    output_images.append((img, f"Page_{page_num}.jpg"))
                
                progress_bar.progress((index + 1) / total_rows)
                status_text.text(f"Đang xử lý dòng {index + 1}/{total_rows}...")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for pil_img, name in output_images:
                    img_byte_arr = io.BytesIO()
                    pil_img.save(img_byte_arr, format='JPEG', quality=95)
                    zip_file.writestr(name, img_byte_arr.getvalue())
            
            st.success(f"✅ Hoàn tất! Đã tạo xong {len(output_images)} trang báo giá.")
            st.download_button(
                label="📥 TẢI XUỐNG TRỌN BỘ ẢNH (.ZIP)",
                data=zip_buffer.getvalue(),
                file_name="Bao_Gia_Creative_An.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Có lỗi xảy ra: {e}")

# --- PHẦN CREDIT (DƯỚI CÙNG TRANG) ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 14px;">
        © 2026 - Created by <b>ànBright s'more creative</b> - exclusive for <b>Celesta Pharma</b>
    </div>
    """, 
    unsafe_allow_html=True
)