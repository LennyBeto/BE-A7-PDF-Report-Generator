import json
from db import get_conn, init_db

def seed():
    init_db()
    conn = get_conn()
    conn.execute("DELETE FROM books")  # idempotent — safe to run twice

    with open("books.json") as f:
        books = json.load(f)

    for b in books:
        conn.execute(
            "INSERT INTO books (title, price, rating, url) VALUES (?, ?, ?, ?)",
            (b["title"], b["price"], b["rating"], b["url"]),
        )
    conn.commit()
    print(f"Seeded {len(books)} books")
    conn.close()

if __name__ == "__main__":
    seed()