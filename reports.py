from db import get_conn

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