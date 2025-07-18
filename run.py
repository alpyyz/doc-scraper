import os
import pandas as pd
from datetime import datetime
import requests
import arxiv

from app.scraper.pdf_handler import extract_text_from_pdf
from app.storage.postgresql_handler import get_pg_connection, insert_paper_pg

if __name__ == "__main__":
    scraping_name = "medical_imaging_0"
    query = "medical image anomaly detection lung"
    max_results = 3

    # Create folders
    folder_path = f"data/{scraping_name}"
    pdf_folder = f"{folder_path}/pdfs"
    os.makedirs(pdf_folder, exist_ok=True)

    # Search arXiv
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    # Prepare result list
    results = []
    for result in search.results():
        results.append({
            "title": result.title,
            "link": result.entry_id,
            "pdf_url": result.pdf_url,
            "published": result.published.strftime("%Y-%m-%d"),
            "authors": ", ".join(str(a) for a in result.authors)
        })

    # Save CSV
    df = pd.DataFrame(results)
    df.to_csv(f"{folder_path}/items.csv", index=False)

    # Save log
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f"{folder_path}/log.txt", "w", encoding="utf-8") as f:
        f.write(f"Scraping Name: {scraping_name}\n")
        f.write(f"Timestamp: {now}\n")
        f.write(f"Query: {query}\n")
        f.write(f"Found Articles: {len(results)}\n")

    # Connect to PostgreSQL
    conn = get_pg_connection()

    # Download PDFs
    for i, paper in enumerate(results, 1):
        title = paper["title"]
        link = paper["link"]
        pdf_url = paper["pdf_url"]
        print(f"[{i}] {title} -> {pdf_url}")

        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            pdf_path = os.path.join(pdf_folder, f"{i:02d}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            print(f"[✓] Downloaded: {pdf_path}")
            success = True
        except Exception as e:
            print(f"[✗] Failed to download PDF for: {title} — {e}")
            pdf_path = None
            success = False

        raw_text = extract_text_from_pdf(pdf_path) if success else None

        insert_paper_pg(
            conn=conn,
            title=title,
            scholar_link=link,
            scihub_link=pdf_url,  # You can rename this in your DB schema if needed
            is_downloaded=success,
            local_path=pdf_path,
            raw_text=raw_text
        )

    conn.close()
