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

# --- HÀM PHÙ PHÉP GIAO DIỆN LIQUID GLASS (BÊ NGUYÊN TỪ V3 CỦA ANH) ---
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

        html, body, [class*="css"], span, div, button, input {{
            font-family: 'GoogleSans', sans-serif !important;
        }}
        
        /* 1. FIX MÀU CHỮ ĐEN CHO TOÀN BỘ TEXT ĐỂ NỔI TRÊN NỀN KÍNH */
        p, h1, h2, h3, .stSubheader, label p, div[data-testid="stMarkdownContainer"] p {{
            color: #1a1a1a !important;
            text-shadow: none !important;
        }}
        h1, h2, h3, b, strong, .stSubheader {{
            font-family: 'GoogleSansBold', sans-serif !important;
        }}

        /* Nền phủ tràn toàn bộ Window */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* HIỆU ỨNG LIQUID GLASS (GLASSMORPHISM) CHUẨN V3 */
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

        /* ÉP PHẦN CREDIT VÀ GẠCH NGANG TRONG SUỐT HOÀN TOÀN */
        header[data-testid="stHeader"], footer, .stMarkdown hr, div[style*="text-align: center"] {{
            background: transparent !important;
            backdrop-filter: none !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* 2. FIX LỖI DARKMODE CHO FILE UPLOADER (TRẢ LẠI NỀN TỐI & CHỮ TRẮNG CHO KHUNG DROPZONE) */
        [data-testid="stFileUploadDropzone"] {{
            background-color: rgb(38, 39, 48) !important; 
            border: 1px solid rgba(250, 250, 250, 0.2) !important;
            border-radius: 8px !important;
        }}
        [data-testid="stFileUploadDropzone"] * {{
            color: #ffffff !important; 
        }}
        [data-testid="stFileUploadDropzone"] button {{
            background-color: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            color: #ffffff !important;
        }}
        [data-testid="stFileUploadDropzone"] button:hover {{
            background-color: rgba(255,255,255,0.2) !important;
            border: 1px solid #ffffff !important;
        }}

        /* 3. UX CHECKBOX TRẠNG THÁI ĐỘNG XÁM/XANH */
        div[data-testid="stCheckbox"] {{
            padding: 10px 15px !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            margin-bottom: 10px !important;
        }}
        div[data-testid="stCheckbox"]:not(:has(input:checked)) {{
            background: rgba(243, 244, 246, 0.7) !important; 
            border: 1px solid rgba(209, 213, 219, 0.8) !important;
        }}
        div[data-testid="stCheckbox"]:not(:has(input:checked)) label p {{
            color: #4B5563 !important; 
        }}
        div[data-testid="stCheckbox"]:has(input:checked) {{
            background: rgba(34, 197, 94, 0.85) !important; 
            border: 1px solid #16A34A !important;
            box-shadow: 0 4px 10px rgba(34, 197, 94, 0.3) !important;
        }}
        div[data-testid="stCheckbox"]:has(input:checked) label p {{
            color: #ffffff !important; 
            font-weight: bold !important;
        }}
        
        /* Tinh chỉnh nút bấm hiện đại */
        .stButton>button, .stDownloadButton>button {{
            width: 100%;
            border-radius: 12px;
            font-size: 18px !important;
            height: 3.5em !important;
            background: rgba(255, 255, 255, 0.4);
            color: #1a1a1a !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            transition: 0.3s;
            font-weight: bold;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover {{
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 1);
            transform: translateY(-2px);
        }}
        .stDownloadButton>button {{
            background-color: rgba(34, 197, 94, 0.9) !important;
            color: #ffffff !important;
            border: none !important;
        }}
        .stDownloadButton>button:hover {{
            background-color: #16A34A !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

if os.path.exists("web_bg.jpg"):
    set_bg_hack("web_bg.jpg")

# --- HÀM XỬ LÝ ĐỒ HỌA BÁO GIÁ (BẢN FIX LỖI DÍNH CHỮ) ---
def get_lines_and_height(draw, text, font, max_w):
    raw_lines = str(text).split('\n')
    lines = []
    for r_line in raw_lines:
        words = r_line.strip().split()
        current_line = ""
        for word in words:
            # Chống dính chữ cho từ siêu dài
            if draw.textbbox((0, 0), word, font=font)[2] > max_w:
                temp_word = ""
                for char in word:
                    if draw.textbbox((0, 0), temp_word + char, font=font)[2] <= max_w:
                        temp_word += char
                    else:
                        if current_line: 
                            lines.append(current_line)
                            current_line = ""
                        if temp_word: lines.append(temp_word)
                        temp_word = char
                word = temp_word

            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_w:
                current_line = test_line
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
            try:
                f_main_title = ImageFont.truetype("Nunito-Black.ttf", 56) 
            except:
                f_main_title = ImageFont.truetype("GoogleSansFlex_24pt-Bold.ttf", 56) 
            
            d.text((margin_x, margin_t - 70), doc_title.upper(), font=f_main_title, fill=(10, 36, 99))
            
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

# 2. BANNER NHẬN DIỆN
BANNER_PNG = "brand_banner.png"
if os.path.exists(BANNER_PNG):
    st.image(BANNER_PNG, use_container_width=True)

# KHỞI TẠO SESSION STATE
if 'is_generated' not in st.session_state:
    st.session_state.is_generated = False
    st.session_state.final_pdf = None

# --- POP-UP WHAT'S NEW ---
@st.dialog("🚀 WHAT'S NEW IN SMART EDITION?")
def show_update_popup():
    st.markdown(
        """
        <div style="font-family: 'GoogleSans', sans-serif; color: #1a1a1a;">
            <p style="font-size: 16px; margin-bottom: 15px;">Hệ thống Quotation Pro vừa được nâng cấp với loạt "vũ khí" mới, giúp tối ưu hóa luồng công việc của bạn:</p>
            <ul style="line-height: 1.8;">
                <li>🧠 <b>Smart Data Scanner:</b> Xử lý mượt mà mọi định dạng Excel/CSV. Bất kể dòng tiêu đề nằm ở đâu hay file có chứa rác, AI Scanner sẽ tự động "đánh hơi" và trích xuất dữ liệu chuẩn xác.</li>
                <li>🎛️ <b>Freedom of Customization:</b> Quyền lực nằm trong tay bạn. Tự do bật/tắt, lựa chọn các trường thông tin muốn hiển thị trên bản in chỉ bằng một cú tick chuột.</li>
                <li>📏 <b>Auto-Layout Engine:</b> Dính chữ hay tràn khung đã là dĩ vãng! Hệ thống tự động chia lại tỷ lệ bề rộng cột và bẻ dòng thông minh bất chấp độ dài của văn bản.</li>
                <li>💌 <b>Personalized Welcome:</b> Chuyên nghiệp hóa trải nghiệm đối tác với thư ngỏ chào mừng tự động điền tên và tùy biến ngay trên trang bìa.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Tuyệt vời, trải nghiệm ngay!", use_container_width=True):
        st.session_state.has_seen_update = True
        st.rerun()

if 'has_seen_update' not in st.session_state:
    st.session_state.has_seen_update = False

if not st.session_state.has_seen_update:
    show_update_popup()

# 3. GIAO DIỆN CHÍNH CẤU TRÚC CHUẨN V3 (KHÔNG DÙNG CONTAINER)
st.subheader("✍️ Bước 1: Thông tin khách hàng")
col1, col2 = st.columns([1.5, 1])
with col1:
    customer_name = st.text_input("Kính gửi (Tên Khách hàng / Đối tác):", placeholder="VD: Bệnh viện Đa khoa Tâm Anh (Bỏ trống mặc định là Quý Khách hàng)")
with col2:
    doc_type = st.radio("Loại tài liệu:", ["Bảng giá", "Danh mục sản phẩm"], horizontal=True)

st.subheader("📤 Bước 2: Tải lên dữ liệu")
uploaded_file = st.file_uploader("App sẽ tự động quét file để tìm tiêu đề bảng", type=["csv", "xlsx"], key="file_upload")

if uploaded_file is not None:
    try:
        # --- LOGIC QUÉT DÒNG THÔNG MINH ---
        if uploaded_file.name.endswith('.csv'):
            df_temp = pd.read_csv(uploaded_file, header=None)
        else:
            df_temp = pd.read_excel(uploaded_file, header=None)
        
        header_row_index = 0
        max_score = 0
        
        for i in range(min(20, len(df_temp))):
            row_vals = df_temp.iloc[i].dropna().astype(str).str.lower().tolist()
            keywords = ['stt', 'tên', 'thuốc', 'thành phần', 'hoạt chất', 'hàm lượng', 'đường dùng', 'dạng', 'nhóm', 'giá', 'đvt', 'ghi chú', 'quy cách', 'sđk']
            score = sum(1 for val in row_vals if any(kw in val for kw in keywords))
            if score > max_score:
                max_score = score
                header_row_index = i
                if score >= 3:
                    break
        
        df_input = df_temp.iloc[header_row_index + 1:].copy()
        df_input.columns = [str(c).strip() for c in df_temp.iloc[header_row_index].values]
        df_input.reset_index(drop=True, inplace=True)
        
        all_columns = []
        for col in df_input.columns:
            if str(col).lower() != 'nan' and 'unnamed' not in str(col).lower() and str(col) != '':
                all_columns.append(col)

        # --- BƯỚC 3: CHỌN CỘT ---
        st.subheader("☑️ Bước 3: Tick chọn các cột muốn in ra PDF")
        
        selected_cols = []
        cols = st.columns(4) 
        for i, col_name in enumerate(all_columns):
            with cols[i % 4]:
                if st.checkbox(col_name, value=False, key=f"chk_{i}"):
                    selected_cols.append(col_name)

        if not selected_cols:
            st.warning("⚠️ Vui lòng tick chọn ít nhất 1 trường dữ liệu để tiếp tục.")
        else:
            df = df_input[selected_cols].copy()
            
            st.subheader("📄 Bước 4: Xuất báo giá PDF")
            
            if not st.session_state.is_generated:
                if st.button("🚀 XUẤT FILE PDF NGAY", use_container_width=True):
                    with st.spinner("Hệ thống đang thiết kế bản PDF..."):
                        bg_path, f_h_path, f_r_path = "Background.jpg", "GoogleSansFlex_24pt-Bold.ttf", "GoogleSansFlex_24pt-Regular.ttf"
                        W, H = 1920, 1080
                        bg_raw = Image.open(bg_path).convert("RGB").resize((W, H))
                        f_h = ImageFont.truetype(f_h_path, 20)
                        
                        dynamic_font_size = 15
                        if len(selected_cols) > 8:
                            dynamic_font_size = 12
                        elif len(selected_cols) > 6:
                            dynamic_font_size = 13
                        f_b = ImageFont.truetype(f_r_path, dynamic_font_size)
                        
                        f_page = ImageFont.truetype(f_r_path, 13)
                        f_title = ImageFont.truetype(f_h_path, 26)
                        f_welcome = ImageFont.truetype(f_r_path, 22) 
                        
                        margin_t, margin_b, margin_x = 320, 75, 75
                        available_w = W - (margin_x * 2)
                        
                        weights = []
                        for c in selected_cols:
                            cl = str(c).lower()
                            if 'stt' in cl: weights.append(0.5)
                            elif 'tên' in cl or 'thành phần' in cl or 'hoạt chất' in cl or 'cơ sở' in cl: weights.append(2.5)
                            elif 'giá' in cl or 'tiền' in cl: weights.append(1.5)
                            elif 'dạng' in cl or 'đường' in cl or 'nhóm' in cl or 'sđk' in cl: weights.append(1.2)
                            else: weights.append(1.0)
                        
                        total_w = sum(weights)
                        col_w = [int((w / total_w) * available_w) for w in weights]
                        col_w[-1] += available_w - sum(col_w)
                        
                        x_pos = []
                        curr_x = margin_x
                        for w in col_w: 
                            x_pos.append(curr_x)
                            curr_x += w
                        
                        output_images, img, draw, curr_y = [], None, None, 0
                        dummy_draw = ImageDraw.Draw(Image.new('RGB', (W, H)))

                        for index, row in df.iterrows():
                            r_lines, r_max_h = [], 0
                            for idx, col in enumerate(selected_cols):
                                val = str(row.get(col, '')).strip()
                                if val.lower() == 'nan': val = ""
                                if 'giá' in str(col).lower() or 'tiền' in str(col).lower():
                                    try: val = f"{int(float(val)):,} VND" if val else ""
                                    except: pass
                                
                                m_w = col_w[idx] - 15 
                                lines, h = get_lines_and_height(dummy_draw, val, f_b, m_w)
                                r_lines.append(lines); r_max_h = max(r_max_h, h)

                            if img is None or (curr_y + r_max_h + 40 > H - margin_b):
                                if img is not None: output_images.append(img)
                                is_first = (img is None)
                                img, draw, curr_y = create_page(bg_raw, selected_cols, x_pos, col_w, f_h, margin_t, margin_x, W, H, is_first, doc_type, customer_name, f_title, f_welcome)

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
                    st.button("📑 Đã tạo xong báo giá", disabled=True, use_container_width=True)
                with col_btn2:
                    file_name_export = "Bao_Gia_Celesta.pdf" if doc_type == "Bảng giá" else "Danh_Muc_Celesta.pdf"
                    st.download_button(label="📥 Tải file PDF", data=st.session_state.final_pdf, file_name=file_name_export, mime="application/pdf", use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Làm lại file mới"):
                    st.session_state.is_generated = False
                    st.rerun()

    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")

# 4. CREDIT TRONG SUỐT BẢN V3

st.markdown('<div style="text-align: center; color: #FFFFFF; font-size: 14px; text-shadow: 0px 0px 0px rgba(0,0,0,0);">© 2026 - Created by <b>ànBright s\'more creative</b> - exclusive for <b>Celesta Pharma</b></div>', unsafe_allow_html=True)
