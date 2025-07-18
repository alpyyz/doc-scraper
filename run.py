import os
import pandas as pd
from datetime import datetime
from app.scraper.scholar import search_google_scholar
from app.scraper.pdf_handler import download_pdf_via_chrome, extract_text_from_pdf
from app.storage.postgresql_handler import get_pg_connection, insert_paper_pg

if __name__ == "__main__":
    scraping_name = "medical_imaging_0"
    query = "medical image anomaly detection lung"

    # Scrape results
    results = search_google_scholar(query, 3)

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
    
    # Connect to the PostgreSQL DB
    conn = get_pg_connection()

    # Download PDFs
    for i, paper in enumerate(results, 1):
        title = paper.get("title")
        link = paper.get("link")
        print(f"[{i}] {title} -> {link}")

        if not link:
            continue

        success, scihub_link = download_pdf_via_chrome(link, pdf_folder, i)
        if not success:
            print(f"[✗] Failed to download PDF for: {title}")
        
        pdf_path = f"{pdf_folder}/{i:02d}.pdf" if success else None
        if success:
            raw_text = extract_text_from_pdf(pdf_path)
        else:
            raw_text = None


        insert_paper_pg(
                conn=conn,
                title=title,
                scholar_link=link,
                scihub_link=scihub_link,
                is_downloaded=success,
                local_path=pdf_path,
                raw_text=extract_text_from_pdf(pdf_path)
            )