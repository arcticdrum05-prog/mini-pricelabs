import asyncio
from playwright.async_api import async_playwright
import psycopg2
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )


async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = "https://www.booking.com/searchresults.html?ss=Tulum&checkin_year=2026&checkin_month=3&checkin_monthday=10&checkout_year=2026&checkout_month=3&checkout_monthday=12&group_adults=2&no_rooms=1&group_children=0"
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(8000)

        cards = await page.query_selector_all('[data-testid="property-card"]')
        print(f"Encontradas {len(cards)} propiedades")

        conn = get_connection()
        cur = conn.cursor()

        for i, card in enumerate(cards[:20]):
            try:
                title_el = await card.query_selector('[data-testid="title"]')
                price_el = await card.query_selector('[data-testid="price-and-discounted-price"]')

                if not title_el or not price_el:
                    continue

                name = await title_el.inner_text()
                price_text = await price_el.inner_text()

                price_number = "".join(c for c in price_text if c.isdigit())
                if not price_number:
                    continue

                price = int(price_number)

                cur.execute("""
                    INSERT INTO market_listings (external_id, zone_id, bedrooms)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id;
                """, (f"booking_pw_{i}", 1, 1))

                result = cur.fetchone()

                if result:
                    listing_id = result[0]
                else:
                    cur.execute("""
                        SELECT id FROM market_listings
                        WHERE external_id = %s
                        LIMIT 1;
                    """, (f"booking_pw_{i}",))
                    listing_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO market_prices
                    (listing_id, stay_date, snapshot_date, price, is_available)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    listing_id,
                    date.today(),
                    date.today(),
                    price,
                    True
                ))

            except Exception as e:
                print("Error en card:", e)

        conn.commit()
        cur.close()
        conn.close()

        await browser.close()
        print("✅ Scraping con Playwright terminado")


if __name__ == "__main__":
    asyncio.run(scrape())
