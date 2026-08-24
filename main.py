from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import date, datetime
from db import get_conn, init_db
from reports import get_report_data, get_all_books, render_html, generate_pdf

app = FastAPI()
init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=201)
def create_report(force: bool = False):
    conn = get_conn()

    if not force:
        existing = conn.execute(
            "SELECT * FROM reports WHERE date(created_at) = date('now') ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if existing:
            conn.close()
            return {"id": existing["id"], "file": f"/reports/{existing['id']}/file"}

    data = get_report_data()
    books = get_all_books()
    html = render_html(data, books)

    cur = conn.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, ?)",
        ("", datetime.utcnow().isoformat()),
    )
    report_id = cur.lastrowid
    path = f"reports/{report_id}.pdf"
    generate_pdf(html, path)

    conn.execute("UPDATE reports SET path = ? WHERE id = ?", (path, report_id))
    conn.commit()
    conn.close()

    return {"id": report_id, "file": f"/reports/{report_id}/file"}

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Report not found")
    return {"id": row["id"], "created_at": row["created_at"], "file": f"/reports/{row['id']}/file"}

@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Report not found")
    return FileResponse(row["path"], media_type="application/pdf", filename=f"report-{report_id}.pdf")