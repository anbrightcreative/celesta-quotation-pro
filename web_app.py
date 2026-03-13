import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import io
import img2pdf
import base64

# 1. CẤU HÌNH TRANG TRÀN VIỀN
st.set_page_config(
    page_title="Quotation Pro - Smart Edition", 
    page_icon="🚀", 
    layout="wide"
)

# --- HÀM PHÙ PHÉP GIAO DIỆN LIQUID GLASS & ANTI-DARKMODE ---
def set_bg_hack(main_bg):
    with open(main_bg, "rb") as f:
        bin_str = base64.b64encode(f.read()).decode()
    
    font_reg_b64, font_bold_b64 = "", ""
    if os.path.exists("GoogleSansFlex_24pt-Regular.ttf"):
        with open("GoogleSansFlex_24pt-Regular.ttf", "rb") as f:
            font_reg_b64 = base64.b64encode(f.read()).decode()
    if os.path.exists("GoogleSansFlex_24pt-Bold.ttf"):
        with open("GoogleSansFlex_24pt-Bold.ttf", "rb") as f:
            font_bold_b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        @font-face {{ font-family: 'GoogleSans'; src: url('data:font/ttf;base64,{font_reg_b64}'); }}
        @font-face {{ font-family: 'GoogleSansBold'; src: url('data:font/ttf;base64,{font_bold_b64}'); }}

        /* --- SIÊU CẤP ANTI-DARKMODE --- */
        :root {{ color-scheme: light !important; }}
        
        html, body, [class*="css"], span, div, button, input {{
            font-family: 'GoogleSans', sans-serif !important;
        }}
        
        /* FIX MÀU CHỮ ĐEN CHO TOÀN BỘ TEXT */
        p, h1, h2, h3, .stSubheader, label p, div[data-testid="stMarkdownContainer"] p, input {{
            color: #1a1a1a !important;
            -webkit-text-fill-color: #1a1a1a !important;
            text-shadow: none !important;
        }}
        h1, h2, h3, b, strong, .stSubheader {{
            font-family: 'GoogleSansBold', sans-serif !important;
        }}

        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
        }}

        /* HIỆU ỨNG LIQUID GLASS CHUẨN V3 */
        .stColumn, div[data-testid="stMarkdownContainer"] > h1, 
        div[data-testid="stMarkdownContainer"] > h2, 
        .stSubheader, .stFileUploader, .stAlert {{
            background: rgba(255, 255, 255, 0.1) !important; 
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 20px !important;
            padding: 25px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
            margin-bottom: 20px !important;
        }}

        /* FIX BOX NHẬP LIỆU VÀ DROPZONE */
        div[data-baseweb="input"] {{ background-color: #ffffff !important; border: 1px solid #d1d5db !important; }}
        [data-testid="stFileUploadDropzone"] {{ background-color: #ffffff !important; border: 2px dashed #d1d5db !important; }}
        [data-testid="stFileUploadDropzone"] * {{ color: #1a1a1a !important; }}

        header[data-testid="stHeader"], footer, .stMarkdown hr, div[style*="text-align: center"] {{
            background: transparent !important; backdrop-filter: none !important; border: none !important; box-shadow: none !important;
        }}

        /* UX CHECKBOX ĐỘNG */
        div[data-testid="stCheckbox"] {{
            padding: 10px 15px !important; border-radius: 12px !important; transition: all 0.3s ease !important; margin-bottom: 10px !important;
        }}
        div[data-testid="stCheckbox"]:not(:has(input:checked)) {{ 
            background: rgba(243, 244, 246, 0.7) !important; border: 1px solid rgba(209, 213, 219, 0.8) !important; 
        }}
        div[data-testid="stCheckbox"]:not(:has(input:checked)) label p {{ color: #4B5563 !important; }}
        div[data-testid="stCheckbox"]:has(input:checked) {{ 
            background: rgba(34, 197, 94, 0.85) !important; border: 1px solid #16A34A !important; box-shadow: 0 4px 10px rgba(34, 197, 94, 0.3) !important; 
        }}
        div[data-testid="stCheckbox"]:has(input:checked) label p {{ color: #ffffff !important; font-weight: bold !important; }}
        
        .stButton>button, .stDownloadButton>button {{
            width: 100%; border-radius: 12px; font-size: 18px !important; height: 3.5em !important; 
            background: rgba(255, 255, 255, 0.4); color: #1a1a1a !important; backdrop-filter: blur(10px); 
            border: 1px solid rgba(255, 255, 255, 0.5); transition: 0.3s; font-weight: bold;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover {{ 
            background: rgba(255, 255, 255, 0.8); border: 1px solid rgba(255, 255, 255, 1); transform: translateY(-2px); 
        }}
        .stDownloadButton>button {{ background-color: rgba(34, 197, 94, 0.9) !important; color: #ffffff !important; border: none !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

if os.path.exists("web_bg.jpg"):
    set_bg_hack("web_bg.jpg")

# --- HÀM XỬ LÝ ĐỒ HỌA PDF THÔNG MINH ---
def get_lines_and_height(draw, text, font, max_w):
    raw_lines = str(text).split('\n')
    lines = []
    for r_line in raw_lines:
        words = r_line.strip().split()
        current_line = ""
        for word in words:
            if draw.textbbox((0, 0), word, font=font)[2] > max_w:
                temp_word = ""
                for char in word:
                    if draw.textbbox((0, 0), temp_word + char, font=font)[2] <= max_w:
                        temp_word += char
                    else:
                        if current_line: lines.append(current_line); current_line = ""
                        if temp_word: lines.append(temp_word)
                        temp_word = char
                word = temp_word
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_w: current_line = test_line
            else:
                if current_line: lines.append(current_line); current_line = word
                else: lines.append(word); current_line = ""
        if current_line: lines.append(current_line)
    total_h = sum([(draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1]) + 8 for l in lines])
    return lines, total_h

def draw_text_lines(draw, lines, x, y, font, fill):
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        current_y += (bbox[3] - bbox[1]) + 8

def create_page(bg_image, cols, x_pos, col_w, f_h, margin_t, margin_x, W, H, is_first_page=False, doc_title="", customer_name="", f_title=None, f_welcome=None):
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(bg_image, (0, 0))
    d = ImageDraw.Draw(canvas)
    actual_margin_t = margin_t
    if is_first_page:
        actual_margin_t = margin_t + 180 
        if f_title and f_welcome:
            # TĂNG TIÊU ĐỀ LỚN THÊM 50% (TỪ 46 LÊN 69)
            try: f_main_title = ImageFont.truetype("Nunito-Black.ttf", 69) 
            except: f_main_title = ImageFont.truetype("GoogleSansFlex_24pt-Bold.ttf", 69) 
            
            d.text((margin_x, margin_t - 90), doc_title.upper(), font=f_main_title, fill=(10, 36, 99))
            khach_hang = customer_name.strip() if customer_name.strip() else "Quý Khách hàng"
            welcome_line1 = f"Kính gửi: {khach_hang},"
            welcome_line2 = "Công ty TNHH Celesta Pharma trân trọng cám ơn quý đối tác đã quan tâm đến sản phẩm của chúng tôi."
            welcome_line3 = f"Chúng tôi xin kính gửi đến quý đối tác {doc_title} thuốc Kê đơn với chi tiết như sau:"
            d.text((margin_x, margin_t + 10), welcome_line1, font=f_title, fill=(10, 36, 99)) 
            d.text((margin_x, margin_t + 60), welcome_line2, font=f_welcome, fill=(50, 50, 50))
            d.text((margin_x, margin_t + 95), welcome_line3, font=f_welcome, fill=(50, 50, 50))
    max_h = 0
    for idx, col in enumerate(cols):
        draw_x = x_pos[idx]
        lines, h = get_lines_and_height(d, col, f_h, col_w[idx] - 15) 
        draw_text_lines(d, lines, draw_x, actual_margin_t, f_h, (0,0,0))
        max_h = max(max_h, h)
    line_y = actual_margin_t + max_h + 20
    d.line([(margin_x, line_y), (W - margin_x, line_y)], fill=(0,0,0), width=2)
    return canvas, d, line_y + 20

# 2. BANNER
BANNER_PNG = "brand_banner.png"
if os.path.exists(BANNER_PNG): st.image(BANNER_PNG, use_container_width=True)


# 4. GIAO DIỆN CHÍNH
st.subheader("✍️ Bước 1: Thông tin khách hàng")
col1, col2 = st.columns([1.5, 1])
with col1: customer_name = st.text_input("Kính gửi:", placeholder="VD: Bệnh viện Đa khoa Tâm Anh")
with col2: doc_type = st.radio("Loại tài liệu:", ["Bảng giá", "Danh mục sản phẩm"], horizontal=True)

st.subheader("📤 Bước 2: Tải lên dữ liệu")
uploaded_file = st.file_uploader("Quét file để tìm tiêu đề bảng", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        df_temp = pd.read_csv(uploaded_file, header=None) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file, header=None)
        header_row_index, max_score = 0, 0
        for i in range(min(20, len(df_temp))):
            row_vals = df_temp.iloc[i].dropna().astype(str).str.lower().tolist()
            score = sum(1 for val in row_vals if any(kw in val for kw in ['stt', 'tên', 'thuốc', 'thành phần', 'hoạt chất', 'hàm lượng', 'giá', 'sđk']))
            if score > max_score: header_row_index, max_score = i, score
            if score >= 3: break
        
        df_input = df_temp.iloc[header_row_index + 1:].copy()
        df_input.columns = [str(c).strip() for c in df_temp.iloc[header_row_index].values]
        df_input.reset_index(drop=True, inplace=True)
        all_columns = [col for col in df_input.columns if str(col).lower() != 'nan' and 'unnamed' not in str(col).lower() and str(col) != '']

        st.subheader("☑️ Bước 3: Tick chọn các cột muốn in")
        selected_cols = []
        cols = st.columns(4) 
        for i, col_name in enumerate(all_columns):
            with cols[i % 4]:
                if st.checkbox(col_name, value=False, key=f"chk_{i}"): selected_cols.append(col_name)

        if selected_cols:
            df = df_input[selected_cols].copy()
            st.subheader("📄 Bước 4: Xuất PDF")
            
            # --- LOGIC HIỆN NÚT THÔNG MINH ---
            if 'final_pdf' not in st.session_state:
                if st.button("🚀 XUẤT FILE PDF NGAY", use_container_width=True):
                    with st.spinner("Đang thiết kế bản PDF..."):
                        bg_path, f_h_path, f_r_path = "Background.jpg", "GoogleSansFlex_24pt-Bold.ttf", "GoogleSansFlex_24pt-Regular.ttf"
                        W, H = 1920, 1080
                        bg_raw = Image.open(bg_path).convert("RGB").resize((W, H))
                        f_h, f_title, f_welcome = ImageFont.truetype(f_h_path, 20), ImageFont.truetype(f_h_path, 26), ImageFont.truetype(f_r_path, 22)
                        f_b = ImageFont.truetype(f_r_path, 12 if len(selected_cols) > 8 else 15)
                        f_page = ImageFont.truetype(f_r_path, 13)
                        
                        margin_t, margin_b, margin_x, available_w = 320, 75, 75, 1920 - 150
                        weights = []
                        for c in selected_cols:
                            cl = str(c).lower()
                            if 'stt' in cl: weights.append(0.5)
                            elif any(k in cl for k in ['tên', 'thành phần', 'hoạt chất']): weights.append(2.5)
                            elif 'giá' in cl: weights.append(1.5)
                            else: weights.append(1.0)
                        total_w = sum(weights)
                        col_w = [int((w / total_w) * available_w) for w in weights]
                        col_w[-1] += available_w - sum(col_w)
                        x_pos = []
                        curr_x = margin_x
                        for w in col_w: x_pos.append(curr_x); curr_x += w
                        
                        output_images, img, draw, curr_y = [], None, None, 0
                        dummy_draw = ImageDraw.Draw(Image.new('RGB', (W, H)))
                        for index, row in df.iterrows():
                            r_lines, r_max_h = [], 0
                            for idx, col in enumerate(selected_cols):
                                val = str(row.get(col, '')).strip()
                                if val.lower() == 'nan': val = ""
                                if 'giá' in str(col).lower():
                                    try: val = f"{int(float(val)):,} VND" if val else ""
                                    except: pass
                                lines, h = get_lines_and_height(dummy_draw, val, f_b, col_w[idx] - 15)
                                r_lines.append(lines); r_max_h = max(r_max_h, h)
                            if img is None or (curr_y + r_max_h + 40 > H - margin_b):
                                if img is not None: output_images.append(img)
                                img, draw, curr_y = create_page(bg_raw, selected_cols, x_pos, col_w, f_h, margin_t, margin_x, W, H, img is None, doc_type, customer_name, f_title, f_welcome)
                            for idx, lines in enumerate(r_lines): draw_text_lines(draw, lines, x_pos[idx], curr_y, f_b, (0,0,0))
                            curr_y += r_max_h + 20
                            draw.line([(margin_x, curr_y), (W - margin_x, curr_y)], fill=(0,0,0), width=1)
                            curr_y += 20
                            if index == len(df) - 1: output_images.append(img)
                        for i, p_img in enumerate(output_images):
                            ImageDraw.Draw(p_img).text((W - 100, H - 50), f"Trang {i+1}/{len(output_images)}", font=f_page, fill=(100,100,100))
                        pdf_bytes_list = []
                        for p_img in output_images:
                            img_io = io.BytesIO()
                            p_img.save(img_io, format='JPEG', quality=95)
                            pdf_bytes_list.append(img_io.getvalue())
                        st.session_state.final_pdf = img2pdf.convert(pdf_bytes_list)
                        st.rerun()

            else:
                # NÚT TẢI CHỈ HIỆN SAU KHI ĐÃ CÓ FILE
                export_name = "Bao_Gia_Celesta_Pharma.pdf" if doc_type == "Bảng giá" else "Danh_Muc_San_Pham_Celesta.pdf"
                st.download_button(label="📥 TẢI FILE PDF", data=st.session_state.final_pdf, file_name=export_name, mime="application/pdf", use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Làm lại file mới"):
                    del st.session_state['final_pdf']
                    st.rerun()
                    
    except Exception as e: st.error(f"Lỗi: {e}")

st.markdown("<br><br>---", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #FFFFFF; font-size: 14px; text-shadow: 0px 1px 3px rgba(0,0,0,0.5);">© 2026 - Created by <b>ànBright s\'more creative</b> - exclusive for <b>Celesta Pharma</b></div>', unsafe_allow_html=True)
