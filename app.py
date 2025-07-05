import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ------------------------
# Flatten transparent image to white background
# ------------------------
def flatten_transparency(image):
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        return background
    return image.convert("RGB")

# ------------------------
# Calculate logo draw dimensions
# ------------------------
def calculate_logo_dimensions(logo_image, max_width, max_height):
    original_width, original_height = logo_image.size
    aspect = original_width / original_height

    if aspect >= (max_width / max_height):
        logo_draw_width = max_width
        logo_draw_height = max_width / aspect
    else:
        logo_draw_height = max_height
        logo_draw_width = max_height * aspect

    return logo_draw_width, logo_draw_height

# ------------------------
# Draw badge
# ------------------------
def draw_badge(c, x, y, badge_width, badge_height, name, org, logo, logo_draw_width, logo_draw_height, font_type, name_font_size, org_font_size, padding):
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.rect(x, y, badge_width, badge_height)

    text_x = x + padding
    text_y = y + badge_height - 1.2 * cm

    try:
        c.setFont(font_type + "-Bold", name_font_size)
    except:
        c.setFont(font_type, name_font_size)
    c.drawString(text_x, text_y, name)

    c.setFont(font_type, org_font_size)
    c.drawString(text_x, text_y - 0.6 * cm, org)

    logo_x = x + badge_width - logo_draw_width - padding
    logo_y = y + (badge_height - logo_draw_height) / 2

    c.drawImage(logo, logo_x, logo_y, width=logo_draw_width, height=logo_draw_height, mask='auto')

# ------------------------
# Generate badges PDF
# ------------------------
def generate_badges_pdf(data, logo_image, font_type, name_font_size, org_font_size):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    badge_width, badge_height = 9.01 * cm, 5.51 * cm
    max_logo_width, max_logo_height = 3.25 * cm, 5.0 * cm
    left_margin, top_margin, padding = 1.0 * cm, 1.0 * cm, 0.3 * cm
    badges_per_row, badges_per_column = 2, 4

    logo_buffer = BytesIO()
    logo_image.save(logo_buffer, format="PNG")
    logo_buffer.seek(0)
    logo = ImageReader(logo_buffer)
    logo_draw_width, logo_draw_height = calculate_logo_dimensions(logo_image, max_logo_width, max_logo_height)

    for i, row in data.iterrows():
        col = i % badges_per_row
        row_num = (i // badges_per_row) % badges_per_column
        page_num = i // (badges_per_row * badges_per_column)

        if i % (badges_per_row * badges_per_column) == 0 and i != 0:
            c.showPage()

        x = left_margin + col * (badge_width + padding)
        y = A4[1] - top_margin - (row_num + 1) * (badge_height + padding)

        draw_badge(c, x, y, badge_width, badge_height, str(row['Name']), str(row['Organisation']), logo, logo_draw_width, logo_draw_height, font_type, name_font_size, org_font_size, padding)

    c.save()
    buffer.seek(0)
    return buffer

# ------------------------
# Generate preview badge PDF
# ------------------------
def generate_preview_pdf(name, org, logo_image, font_type, name_font_size, org_font_size):
    buffer = BytesIO()
    badge_width, badge_height = 9.01 * cm, 5.51 * cm
    max_logo_width, max_logo_height = 3.25 * cm, 5.0 * cm
    padding = 0.3 * cm

    c = canvas.Canvas(buffer, pagesize=(badge_width, badge_height))

    logo_buffer = BytesIO()
    logo_image.save(logo_buffer, format="PNG")
    logo_buffer.seek(0)
    logo = ImageReader(logo_buffer)
    logo_draw_width, logo_draw_height = calculate_logo_dimensions(logo_image, max_logo_width, max_logo_height)

    draw_badge(c, 0, 0, badge_width, badge_height, name, org, logo, logo_draw_width, logo_draw_height, font_type, name_font_size, org_font_size, padding)

    c.save()
    buffer.seek(0)
    return buffer

# ------------------------
# Streamlit App
# ------------------------
st.title("📛 Name Badge Generator – Fixed Logo Positioning (9.01 × 5.51 cm)")

uploaded_excel = st.file_uploader("Upload Excel with 'Name' and 'Organisation'", type=["xlsx"])
uploaded_logo = st.file_uploader("Upload Logo (PNG, JPG)", type=["png", "jpg", "jpeg"])

st.sidebar.header("🖋️ Font Settings")
font_type = st.sidebar.selectbox("Font Type", ["Helvetica", "Times-Roman", "Courier"])
name_font_size = st.sidebar.slider("Name Font Size", 8, 24, 13)
org_font_size = st.sidebar.slider("Organisation Font Size", 6, 20, 11)

if uploaded_excel and uploaded_logo:
    df = pd.read_excel(uploaded_excel, engine='openpyxl')

    if df.empty:
        st.error("The uploaded Excel file is empty.")
    elif 'Name' not in df.columns or 'Organisation' not in df.columns:
        st.error("Excel file must contain 'Name' and 'Organisation' columns.")
    else:
        if df[['Name', 'Organisation']].isnull().any().any():
            st.warning("Some rows have missing Name or Organisation values. These will be skipped.")

        logo_image = Image.open(uploaded_logo)
        logo_image = flatten_transparency(logo_image)

        first_valid = df.dropna(subset=['Name', 'Organisation']).iloc[0]

        st.subheader("🔍 Preview of First Badge")
        preview_pdf = generate_preview_pdf(str(first_valid['Name']), str(first_valid['Organisation']), logo_image, font_type, name_font_size, org_font_size)

        st.download_button("📥 Download Preview Badge (PDF)", preview_pdf, file_name="preview_badge.pdf", mime="application/pdf")

        if st.button("🔄 Generate PDF Badges"):
            cleaned_df = df.dropna(subset=['Name', 'Organisation'])
            pdf_output = generate_badges_pdf(cleaned_df, logo_image, font_type, name_font_size, org_font_size)
            st.download_button("📥 Download Name Badges (PDF)", pdf_output, file_name="name_badges.pdf", mime="application/pdf")
else:
    st.info("Please upload both an Excel file and a logo image to continue.")
