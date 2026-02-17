from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import psycopg2

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


def get_connection():
    return psycopg2.connect(
        host="SWITCHYARD.PROXY.RLWY.NET",
    port="47433",
    dbname="railway",
    user="postgres",
    password="nZgHfBcHgqsBVyQXQbDahfvSNEpZfYNU"
    )


@app.get("/")
def dashboard(request: Request):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.name,
            pr.date,
            pr.recommended_price,
            pr.market_avg_price,
            pr.expected_revenue
        FROM price_recommendations pr
        JOIN properties p ON pr.property_id = p.id
        ORDER BY p.name, pr.date
        LIMIT 200;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "rows": rows}
    )
