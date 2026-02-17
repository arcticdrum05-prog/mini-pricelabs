from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def dashboard(request: Request):
    try:
        df = pd.read_csv("data/optimized_prices_2026.csv", parse_dates=["date"])
    except Exception:
        df = pd.DataFrame(columns=[
            "property", "date", "optimal_price",
            "expected_occupancy", "expected_revenue", "currency"
        ])

    # métricas resumen
    total_revenue = round(df["expected_revenue"].sum(), 2) if not df.empty else 0
    avg_occupancy = round(df["expected_occupancy"].mean(), 3) if not df.empty else 0
    avg_price = round(df["optimal_price"].mean(), 2) if not df.empty else 0

    # últimas filas para tabla
    table_data = df.sort_values("date").head(200).to_dict(orient="records") if not df.empty else []

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_revenue": total_revenue,
            "avg_occupancy": avg_occupancy,
            "avg_price": avg_price,
            "rows": table_data,
        }
    )
