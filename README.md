# Name Badge Generator

A Streamlit app that turns an Excel spreadsheet of names and organisations, plus a logo, into printable PDF name badges (9.01 × 5.51 cm, laid out for A4 sheets).

## Tech Stack

- Python 3
- Streamlit
- pandas / openpyxl (Excel parsing)
- Pillow (image handling)
- ReportLab (PDF generation)

## Features

- Upload an Excel file with `Name` and `Organisation` columns
- Upload a logo (PNG/JPG), automatically flattened onto a white background if transparent
- Adjustable font type and font sizes for name and organisation text
- Live preview of the first badge as a downloadable PDF
- Bulk-generates all badges into a single multi-page PDF, laid out 2×4 per A4 page
- Skips rows with missing name or organisation data (with a warning)

## Getting Started

```bash
pip install streamlit pandas pillow reportlab openpyxl
streamlit run app.py
```
