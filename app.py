import asyncio
import json
from flask import Flask, Response
from flask_cors import CORS
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

SUBSCRIPTION_URL = "https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/?year=2025"
ALLOTMENT_URL = "https://www.chittorgarh.com/report/ipo-allotment-status-check-date-process/23/"

async def fetch_subscription_data(page):
    await page.goto(SUBSCRIPTION_URL, wait_until="load", timeout=15000)
    await page.wait_for_selector("#report_table tbody tr", timeout=15000)
    data = await page.evaluate("""() => {
        const rows = document.querySelectorAll("#report_table tbody tr");
        return Array.from(rows).map(row => {
            const cols = row.querySelectorAll("td");
            return {
                company_name: cols[0]?.innerText.trim(),
                close_date: cols[1]?.innerText.trim(),
                size_rs_cr: cols[2]?.innerText.trim(),
                QIB_x: cols[3]?.innerText.trim(),
                sNII_x: cols[4]?.innerText.trim(),
                bNII_x: cols[5]?.innerText.trim(),
                NII_x: cols[6]?.innerText.trim(),
                Retail_x: cols[7]?.innerText.trim(),
                Employee_x: cols[8]?.innerText.trim(),
                Others: cols[9]?.innerText.trim(),
            };
        });
    }""")
    return data

async def fetch_allotment_data(page):
    await page.goto(ALLOTMENT_URL, wait_until="load", timeout=15000)
    await page.wait_for_selector("#report_table tbody tr", timeout=15000)
    data = await page.evaluate("""() => {
        const rows = document.querySelectorAll("#report_table tbody tr");
        return Array.from(rows).map(row => {
            const cols = row.querySelectorAll("td");
            const registrarAnchor = cols[4]?.querySelector("a");
            return {
                company_name: cols[0]?.innerText.trim(),
                issue_open: cols[1]?.innerText.trim(),
                issue_close: cols[2]?.innerText.trim(),
                registrar_link: registrarAnchor ? registrarAnchor.href.trim() : null,
            };
        });
    }""")
    return data

def normalize_name(name):
    return ''.join(e for e in name.lower() if e.isalnum())

async def get_ipo_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        
        subscription_page = await context.new_page()
        subscription_data = await fetch_subscription_data(subscription_page)
        await subscription_page.close()

        allotment_page = await context.new_page()
        allotment_data = await fetch_allotment_data(allotment_page)
        await allotment_page.close()

        await browser.close()

        allotment_dict = {}
        for item in allotment_data:
            key = normalize_name(item['company_name'])
            allotment_dict[key] = {
                'issue_open': item['issue_open'],
                'issue_close': item['issue_close'],
                'registrar_link': item['registrar_link'],
            }

        for ipo in subscription_data:
            key = normalize_name(ipo['company_name'])
            ipo['Allotment_Info'] = allotment_dict.get(key, None)

        return subscription_data

@app.route("/")
def home():
    data = asyncio.run(get_ipo_data())
    return Response(json.dumps(data, indent=2), mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
