from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def is_captcha_page(page_source: str) -> bool:
    return (
        "Our systems have detected unusual traffic" in page_source
        or "g-recaptcha" in page_source
        or "captcha-form" in page_source
    )

def search_google_scholar(query: str, max_pages: int = 1):
    # Use visible Chrome (for manual CAPTCHA solve)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # show browser
    # Do NOT use headless

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    all_results = []

    try:
        for page in range(max_pages):
            start = page * 10
            url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}&start={start}"
            driver.get(url)
            time.sleep(8)

            if is_captcha_page(driver.page_source):
                print("[🛑] CAPTCHA detected! Please solve it manually in the browser.")
                while is_captcha_page(driver.page_source):
                    time.sleep(3)
                print("[✅] CAPTCHA passed — continuing.")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            results = soup.select(".gs_r")

            for result in results:
                title_tag = result.select_one(".gs_rt")
                if title_tag and title_tag.a:
                    title = title_tag.get_text(strip=True)
                    link = title_tag.a["href"]
                    all_results.append({"title": title, "link": link})

            print(f"[✓] Page {page + 1} scraped: {len(results)} results")

            if len(results) < 10:
                break

    finally:
        driver.quit()

    return all_results
