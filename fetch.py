import os
import time
import requests
from pathlib import Path

# ---------------- Config ----------------
BASE_DIR = Path("databank")
BASE_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "YourName your@email.com"
}

YEARS = {"2023", "2024", "2025"}

CIKS = {
    # --- Big Tech / AI ---
    "Apple": "0000320193",
    "Microsoft": "0000789019",
    "Amazon": "0001018724",
    "Alphabet": "0001652044",
    "NVIDIA": "0001045810",
    "Meta": "0001326801",
    "Tesla": "0001318605",

    # --- Finance ---
    "BerkshireHathaway": "0001067983",
    "JPMorganChase": "0000019617",
    "BankOfAmerica": "0000070858",
    "WellsFargo": "0000072971",
    "GoldmanSachs": "0000886982",
    "MorganStanley": "0000895421",

    # --- Energy ---
    "ExxonMobil": "0000034088",
    "Chevron": "0000093410",

    # --- Semiconductors ---
    "Intel": "0000050863",
    "AMD": "0000002488",
    "Qualcomm": "0000804328",
    "Broadcom": "0001730168",
    "TexasInstruments": "0000097476",

    # --- Consumer / Retail ---
    "Walmart": "0000104169",
    "Costco": "0000909832",
    "HomeDepot": "0000354950",
    "CocaCola": "0000021344",
    "PepsiCo": "0000077476",
    "McDonalds": "0000063908",
    "Nike": "0000320187",

    # --- Healthcare ---
    "JohnsonAndJohnson": "0000200406",
    "Pfizer": "0000078003",
    "UnitedHealth": "0000731766",
    "Merck": "0000310158",

    # --- Telecom / Media ---
    "Verizon": "0000732712",
    "ATandT": "0000732717",
    "Comcast": "0001166691",
    "Disney": "0001744489",

    # --- Industrials ---
    "Boeing": "0000012927",
    "Caterpillar": "0000018230",
    "GeneralElectric": "0000040545",

    # --- Payments ---
    "Visa": "0001403161",
    "Mastercard": "0001141391",

    # --- Cloud / Enterprise ---
    "Oracle": "0001341439",
    "Salesforce": "0001108524",
    "Adobe": "0000796343",
}


def get_10k_filings(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    data = r.json()

    filings = data["filings"]["recent"]
    results = []

    for form, acc, date, primary in zip(
        filings["form"],
        filings["accessionNumber"],
        filings["filingDate"],
        filings["primaryDocument"]
    ):
        if form == "10-K" and date[:4] in YEARS:
            acc_nodash = acc.replace("-", "")
            doc_url = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/{acc_nodash}/{primary}"
            )
            results.append((date[:4], doc_url))

    return results


def download_file(url, out_path):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    out_path.write_bytes(r.content)


for company, cik in CIKS.items():
    company_dir = BASE_DIR / company
    company_dir.mkdir(exist_ok=True)

    print(f"\n📄 {company}")

    try:
        filings = get_10k_filings(cik)
        if not filings:
            print("  No 10-K filings found for selected years.")
            continue

        for year, url in filings:
            filename = f"{company}_10K_{year}.html"
            out_file = company_dir / filename

            if out_file.exists():
                print(f"  ✔ Already exists: {filename}")
                continue

            print(f"  ⬇ Downloading {filename}")
            download_file(url, out_file)
            time.sleep(0.2)  # SEC rate limit safety

    except Exception as e:
        print(f"Error: {e}")

print("\nDone. Files saved in ./databank/")
