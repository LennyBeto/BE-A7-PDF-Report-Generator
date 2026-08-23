from jinja2 import Template
from playwright.sync_api import sync_playwright
from datetime import date
import os
from db import get_conn

TEMPLATE = Template("""
<html>
<head>
<style>
  body { font-family: sans-serif; }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
  thead { display: table-header-group; }
  tr { break-inside: avoid; }
</style>
</head>
<body>
  <h1>Bookstore Report — {{ today }}</h1>
  <p>Total books: {{ data.total_books }}</p>
  <p>Average price: £{{ data.avg_price }}</p>

  <h2>Top 5 most expensive</h2>
  <table>
    <thead><tr><th>Title</th><th>Price</th></tr></thead>
    <tbody>
    {% for b in data.top_5 %}
      <tr><td>{{ b.title }}</td><td>£{{ b.price }}</td></tr>
    {% endfor %}
    </tbody>
  </table>

  <h2>All books</h2>
  <table>
    <thead><tr><th>Title</th><th>Price</th><th>Rating</th></tr></thead>
    <tbody>
    {% for b in all_books %}
      <tr><td>{{ b.title }}</td><td>£{{ b.price }}</td><td>{{ b.rating }}</td></tr>
    {% endfor %}
    </tbody>
  </table>
</body>
</html>
""")

def get_report_data():
    conn = get_conn()

    total_books = conn.execute("SELECT COUNT(*) AS n FROM books").fetchone()["n"]
    avg_price = conn.execute("SELECT AVG(price) AS avg FROM books").fetchone()["avg"]

    top_5 = conn.execute(
        "SELECT title, price FROM books ORDER BY price DESC LIMIT 5"
    ).fetchall()

    by_rating = conn.execute(
        "SELECT rating, COUNT(*) AS n FROM books GROUP BY rating ORDER BY rating"
    ).fetchall()

    conn.close()

    return {
        "total_books": total_books,
        "avg_price": round(avg_price, 2),
        "top_5": [dict(r) for r in top_5],
        "by_rating": [dict(r) for r in by_rating],
    }

def get_all_books():
    conn = get_conn()
    rows = conn.execute("SELECT title, price, rating FROM books").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def render_html(data, all_books):
    return TEMPLATE.render(today=date.today().isoformat(), data=data, all_books=all_books)

def generate_pdf(html, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=out_path, format="A4", print_background=True)
        browser.close()