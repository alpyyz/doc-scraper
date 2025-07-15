from app.scraper.scholar import search_google_scholar

if __name__ == "__main__":
    query = "deep learning medical imaging"
    results = search_google_scholar(query)
    for paper in results:
        print(f"{paper['title']} -> {paper['link']}")
