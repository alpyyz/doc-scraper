import os
import pandas as pd
from datetime import datetime
from app.scraper.scholar import search_google_scholar
from app.scraper.pdf_downloader import download_pdf_via_chrome

if __name__ == "__main__":
    scraping_name = "medical_image_0"
    query = "deep learning medical imaging"

    # Scrape results
    results = search_google_scholar(query)

    # Prepare folders
    folder_path = f"data/{scraping_name}"
    pdf_folder = f"{folder_path}/pdfs"
    os.makedirs(pdf_folder, exist_ok=True)

    # Save CSV
    df = pd.DataFrame(results)
    df.to_csv(f"{folder_path}/items.csv", index=False)

    # Write log file
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f"{folder_path}/log.txt", "w", encoding="utf-8") as f:
        f.write(f"Scraping Name: {scraping_name}\n")
        f.write(f"Timestamp: {now}\n")
        f.write(f"Query: {query}\n")
        f.write(f"Found Articles: {len(results)}\n")

    # Download PDFs
    for i, paper in enumerate(results, 1):
        title = paper.get("title")
        link = paper.get("link")
        print(f"[{i}] {title} -> {link}")

        if not link:
            continue

        success = download_pdf_via_chrome(link, pdf_folder, i)
        if not success:
            print(f"[✗] Failed to download PDF for: {title}")
