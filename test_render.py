# test_render.py
from reports import get_report_data, get_all_books, render_html, generate_pdf
data = get_report_data()
books = get_all_books()
html = render_html(data, books)
generate_pdf(html, "reports/test.pdf")