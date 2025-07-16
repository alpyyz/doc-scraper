import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://scholar.google.com/"
}

url = "https://scholar.google.com/scholar?q=deep+learning+medical+imaging&start=10"
r = requests.get(url, headers=HEADERS)

print("Status code:", r.status_code)
print("Blocked?", "unusual traffic" in r.text)