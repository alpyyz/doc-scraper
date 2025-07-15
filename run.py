import os
import pandas as pd
from datetime import datetime
from app.scraper.scholar import search_google_scholar

if __name__ == "__main__":
    scraping_name = "time_series_search_0"
    query = "time series frequency analysis for prediction"

    # Perform search
    results = search_google_scholar(query)

    # Prepare folder
    folder_path = f"data/{scraping_name}"
    os.makedirs(folder_path, exist_ok=True)

    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv(f"{folder_path}/items.csv", index=False)

    # Log file creation
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    log_path = os.path.join(folder_path, "log.txt")

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Scraping Name: {scraping_name}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Query: {query}\n")
        f.write(f"Found Articles: {len(results)}\n")

    # Output to console
    for paper in results:
        print(f"{paper['title']} -> {paper['link']}")
