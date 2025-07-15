import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def search_google_scholar(query: str):
    url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.select(".gs_r")

    papers = []
    for result in results:
        title_tag = result.select_one(".gs_rt")
        if title_tag and title_tag.a:
            title = title_tag.get_text(strip=True)
            link = title_tag.a.get("href")
            papers.append({"title": title, "link": link})
    return papers
