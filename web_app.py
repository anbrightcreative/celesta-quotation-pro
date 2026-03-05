import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import io
import img2pdf
import base64

# 1. CẤU HÌNH TRANG
st.set_page_config(
    page_title="Quotation Pro - Liquid Glass Edition", 
    page_icon="🚀", 
    layout="wide"
)

# --- HÀM PHỦ NỀN & ĐỒNG BỘ STYLE VỚI GOOGLE SANS ---
def set_bg_hack(main_bg):
    with open(main_bg, "rb") as f:
        bin_str = base64.b64encode(f.read()).decode()
    
    # Đọc file font an toàn
    font_reg_b64 = ""
    font_bold_b64 = ""
    if os.path.exists("GoogleSansFlex_24pt-Regular.ttf"):
        with open("GoogleSansFlex_24pt-Regular.ttf", "rb") as f:
            font_reg_b64 = base64.b64encode(f.read()).decode()
    if os.path.exists("GoogleSansFlex_24pt-Bold.ttf"):
        with open("GoogleSansFlex_24pt-Bold.ttf", "rb") as f:
            font_bold_b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        /* NHÚNG FONT GOOGLE SANS */
        @font-face {{
            font-family: 'GoogleSans';
            src: url('data:font/ttf;base64,{font_reg_b64}');
        }}
        @font-face {{
            font-family: 'GoogleSansBold';
            src: url('data:font/ttf;base64,{font_bold_b64}');
        }}

        /* ÁP DỤNG FONT CHO TOÀN BỘ APP */
        html, body, [class*="css"], .stMarkdown, p, span, div, button {{
            font-family: 'GoogleSans', sans-serif !important;
        }}
        
        h1, h2, h3, b, strong, .stSubheader {{
            font-family: 'GoogleSansBold', sans-serif !important;
        }}

        /* Nền phủ tràn Window */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* ĐỒNG BỘ HIỆU ỨNG GLASSMORPHISM */
        .stColumn, div[data-testid="stMarkdownContainer"] > h1, 
        div[data-testid="stMarkdownContainer"] > h2, 
        .stSubheader, .stFileUploader, .stAlert, div[style*="background-color: rgba(255, 255, 255, 0.1)"] {{
            background: rgba(255, 255, 255, 0.1) !important; 
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 20px !important;
            padding: 25px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1) !important;
            margin-bottom: 25px !important;
        }}

        [data-testid="stFileUploader"] {{
            margin-top: 15px !important;
        }}

        h1, h2, h3, .stSubheader {{
            color: #FFFFFF !important;
            text-shadow: 0px 1px 2px rgba(0,0,0,0.1);
        }}

        /* --- UI NÚT BẤM --- */
        .stButton>button, .stDownloadButton>button {{
            width: 100% !important;
            border-radius: 12px !important;
            height: 3.5em !important;
            font-size: 18px !important;
            transition: all 0.3s ease !important;
            border: none !important;
            font-weight: bold !important;
        }}

        .stButton>button {{ background: rgba(255, 255, 255, 0.9) !important; color: #333 !important; }}
        .stButton>button:hover {{ transform: scale(1.02) !important; }}
        
        /* Trạng thái Disable */
        .stButton>button:disabled {{ 
            background-color: rgba(200, 200, 200, 0.4) !important; 
            color: rgba(50, 50, 50, 0.7) !important; 
            cursor: not-allowed !important; 
            transform: none !important; 
            box-shadow: none !important; 
        }}

        /* Nút tải PDF xanh lá */
        .stDownloadButton>button {{
            background-color: #22C55E !important; 
            color: #FFFFFF !important; 
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4) !important;
        }}
        .stDownloadButton>button:hover {{
            background-color: #16A34A !important; 
            transform: scale(1.02) !important;
            box-shadow: 0 6px 20px rgba(34, 197, 94, 0.6) !important;
        }}

        /* TRONG SUỐT CHO CREDIT */
        header[data-testid="stHeader"], footer, .stMarkdown hr, div[style*="text-align: center"] {{
            background: transparent !important;
            backdrop-filter: none !important;
            border: none !important;
            box-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

if os.path.exists("web_bg.jpg"):
    set_bg_hack("web_bg.jpg")

# --- HÀM XỬ LÝ ĐỒ HỌA BÁO GIÁ ---
def get_lines_and_height(draw, text, font, max_w):
    raw_lines = str(text).split('\n')
    lines = []
    for r_line in raw_lines:
        words = r_line.strip().split()
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_w: current_line = test_line
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

# 2. BANNER & DATA
BANNER_PNG = "brand_banner.png"
if os.path.exists(BANNER_PNG):
    st.image(BANNER_PNG, use_container_width=True)

REQUIRED_COLS = ["STT", "Tên thuốc", "Tên hoạt chất/thành phần", "Hàm Lượng", "Đường dùng", "Dạng bào chế", "Nhóm thuốc", "Giá dịch vụ (Không BHYT)"]

# --- BƯỚC 1: TẢI DỮ LIỆU & TAGS KHUYẾN NGHỊ ---
st.subheader("📤 Bước 1: Tải lên dữ liệu")

tags_html = "".join([
    f'<span style="background-color: #38e75c; color: #1a1a1a; padding: 6px 16px; '
    f'margin: 6px; border-radius: 50px; display: inline-block; font-weight: bold; '
    f'font-size: 13px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"># {col}</span>' 
    for col in REQUIRED_COLS
])

st.markdown(
    f"""
    <div style="background-color: rgba(255, 255, 255, 0.1); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px;">
        <p style="color: #1a1a1a; margin-bottom: 15px; font-weight: bold;">⚠️ File tải lên bắt buộc phải có đủ các trường sau (hệ thống sẽ tự động bỏ qua các trường thừa):</p>
        <div style="line-height: 2.8;">{tags_html}</div>
    </div>
    """, 
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("", type=["csv", "xlsx"], key="file_upload")

# KHỞI TẠO SESSION STATE
if 'is_generated' not in st.session_state:
    st.session_state.is_generated = False
    st.session_state.final_pdf = None

if uploaded_file is not None:
    try:
        df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        missing_cols = [col for col in REQUIRED_COLS if col not in df_input.columns]
        
        if missing_cols:
            st.error(f"❌ Thiếu cột: {', '.join(missing_cols)}")
        else:
            df = df_input[REQUIRED_COLS].copy()
            st.success(f"✅ Đã nhận diện {len(df)} dòng dữ liệu.")
            
            st.subheader("📄 Bước 2: Xuất báo giá PDF")
            
            if not st.session_state.is_generated:
                if st.button("Tạo báo giá", use_container_width=True):
                    with st.spinner("Đang dàn trang..."):
                        bg_path, f_h_path, f_r_path = "Background.jpg", "GoogleSansFlex_24pt-Bold.ttf", "GoogleSansFlex_24pt-Regular.ttf"
                        W, H = 1920, 1080
                        bg_raw = Image.open(bg_path).convert("RGB").resize((W, H))
                        f_h, f_b, f_page = ImageFont.truetype(f_h_path, 20), ImageFont.truetype(f_r_path, 15), ImageFont.truetype(f_r_path, 13)
                        
                        margin_t, margin_b, margin_x = 320, 75, 75
                        col_w = [60, 320, 380, 200, 200, 180, 180, 200]
                        x_pos = []
                        curr_x = margin_x
                        for w in col_w: x_pos.append(curr_x); curr_x += w
                        
                        output_images, img, draw, curr_y = [], None, None, 0
                        dummy_draw = ImageDraw.Draw(Image.new('RGB', (W, H)))

                        for index, row in df.iterrows():
                            r_lines, r_max_h = [], 0
                            for idx, col in enumerate(REQUIRED_COLS):
                                val = str(row.get(col, '')).strip()
                                if val.lower() == 'nan': val = ""
                                if 'Giá' in col:
                                    try: val = f"{int(float(val)):,} VND" if val else ""
                                    except: pass
                                m_w = col_w[idx] - 60 if idx > 1 else 9999
                                lines, h = get_lines_and_height(dummy_draw, val, f_b, m_w)
                                r_lines.append(lines); r_max_h = max(r_max_h, h)

                            if img is None or (curr_y + r_max_h + 40 > H - margin_b):
                                if img is not None: output_images.append(img)
                                img, draw, curr_y = create_page(bg_raw, REQUIRED_COLS, x_pos, f_h, margin_t, margin_x, W, H)

                            for idx, lines in enumerate(r_lines):
                                draw_text_lines(draw, lines, x_pos[idx], curr_y, f_b, (0,0,0))
                            l_y = curr_y + r_max_h + 20
                            draw.line([(margin_x, l_y), (W - margin_x, l_y)], fill=(0,0,0), width=1)
                            curr_y = l_y + 20
                            if index == len(df) - 1: output_images.append(img)

                        for i, p_img in enumerate(output_images):
                            d_p = ImageDraw.Draw(p_img)
                            p_txt = f"Trang {i+1}/{len(output_images)}"
                            bw = d_p.textbbox((0, 0), p_txt, font=f_page)
                            d_p.text((W - 30 - (bw[2]-bw[0]), H - 30 - (bw[3]-bw[1])), p_txt, font=f_page, fill=(100,100,100))

                        # Fix lỗi img2pdf chuẩn xác
                        pdf_bytes_list = []
                        for p_img in output_images:
                            img_io = io.BytesIO()
                            p_img.save(img_io, format='JPEG', quality=95)
                            pdf_bytes_list.append(img_io.getvalue())
                        
                        st.session_state.final_pdf = img2pdf.convert(pdf_bytes_list)
                        st.session_state.is_generated = True
                        st.rerun()
            else:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.button("Đã tạo xong báo giá", disabled=True, use_container_width=True)
                with col_btn2:
                    st.download_button(label="Tải báo giá", data=st.session_state.final_pdf, file_name="Bao_Gia_Celesta.pdf", mime="application/pdf", use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Làm lại file mới"):
                    st.session_state.is_generated = False
                    st.rerun()

    except Exception as e:
        st.error(f"Lỗi: {e}")

# 4. CREDIT
st.markdown("<br><br>---", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #1a1a1a; font-size: 14px; text-shadow: 0px 0px 0px rgba(0,0,0,0.0);">© 2026 - Created by <b>ànBright s\'more creative</b> - exclusive for <b>Celesta Pharma</b></div>', unsafe_allow_html=True)
