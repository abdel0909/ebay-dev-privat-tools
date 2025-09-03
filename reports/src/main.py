import os
import csv
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from dotenv import load_dotenv

from ebay_client import EbayClient
from price_check import extract_prices, summarize

DEFAULT_FILTER = (
    # Beispiel-Filter: Nur Sofort-Kauf und Europreise
    # Mehr möglich: price:[..], conditions:{NEW|USED_GOOD}, itemLocationCountry:DE etc.
    "buyingOptions:{FIXED_PRICE},priceCurrency:EUR"
)

def run(csv_path="items.csv", out_dir="reports"):
    load_dotenv()
    tz = ZoneInfo("Europe/Berlin")
    ts = datetime.now(tz).strftime("%Y-%m-%d_%H-%M")

    os.makedirs(out_dir, exist_ok=True)

    cli = EbayClient(env=os.getenv("EBAY_ENV", "PROD"))
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row["query"].strip()
            try:
                max_price = float(row["max_price"])
            except:
                max_price = None
            notes = row.get("notes", "")

            data = cli.search_items(q, limit=30, filter_str=DEFAULT_FILTER)
            prices = extract_prices(data)
            stats = summarize(prices)

            status = ""
            if stats["median"] is None:
                status = "keine Daten"
            elif max_price is None:
                status = "ohne Zielpreis"
            else:
                if stats["median"] > max_price:
                    status = "zu teuer"
                elif stats["median"] < max_price * 0.85:
                    status = "evtl. zu billig (Chance?)"
                else:
                    status = "ok"

            rows.append({
                "query": q,
                "count": stats["count"],
                "min": stats["min"],
                "median": stats["median"],
                "mean": stats["mean"],
                "max": stats["max"],
                "target_max": max_price,
                "status": status,
                "notes": notes,
                "timestamp": ts,
            })

    df = pd.DataFrame(rows, columns=[
        "timestamp","query","count","min","median","mean","max","target_max","status","notes"
    ])
    out_csv = os.path.join(out_dir, f"price_report_{ts}.csv")
    df.to_csv(out_csv, index=False)
    # Zusätzlich: aktuelle Kurz-Übersicht immer als latest.csv
    df.to_csv(os.path.join(out_dir, "latest.csv"), index=False)
    print(f"Report geschrieben: {out_csv}")

if __name__ == "__main__":
    run()
