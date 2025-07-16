import os
import time
import glob
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def normalize_pdf_url(raw_url: str):
    raw_url = raw_url.strip("'\"")
    if raw_url.startswith("http"):
        return raw_url
    elif raw_url.startswith("//"):
        return "https:" + raw_url
    elif raw_url.startswith("/"):
        return "https://sci-hub.se" + raw_url
    elif "sci-hub.se//" in raw_url:
        # Fix broken prepend like https://sci-hub.se//dacemirror...
        parts = raw_url.split("//", 2)
        return "https://" + parts[-1]
    else:
        print(f"[!] Unrecognized format in PDF URL: {raw_url}")
        return None

def download_pdf_via_chrome(original_url, download_dir, index):
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        sci_hub_url = f"https://sci-hub.se/{original_url}"
        driver.get(sci_hub_url)
        time.sleep(10)

        pdf_url = None

        # Try iframe method first
        try:
            iframe = driver.find_element(By.TAG_NAME, "iframe")
            iframe_src = iframe.get_attribute("src")
            pdf_url = normalize_pdf_url(iframe_src)
        except Exception:
            print("[!] iframe not found, trying download button...")

        # Fallback: button with onclick
        if not pdf_url:
            try:
                # Try finding any clickable element with location.href
                elements = driver.find_elements(By.XPATH, "//*[@onclick]")
                for el in elements:
                    onclick = el.get_attribute("onclick")
                    if onclick and "location.href=" in onclick:
                        raw_url = onclick.split("location.href=")[-1]
                        pdf_url = normalize_pdf_url(raw_url)
                        break
            except Exception as e:
                print(f"[✗] No iframe or download button found: {e}")
                return False

        if not pdf_url:
            print(f"[✗] Could not extract valid PDF URL from: {original_url}")
            return False

        # Trigger download
        driver.get(pdf_url)
        print(f"[✓] Triggered download: {pdf_url}")
        time.sleep(6)

        # Rename the latest downloaded PDF
        pdfs = glob.glob(os.path.join(download_dir, "*.pdf"))
        if not pdfs:
            print(f"[!] No PDF file detected in: {download_dir}")
            return False

        latest_pdf = max(pdfs, key=os.path.getctime)
        target_path = os.path.join(download_dir, f"{index:02d}.pdf")

        # Avoid overwriting existing file
        if os.path.exists(target_path):
            os.remove(target_path)

        os.rename(latest_pdf, target_path)
        print(f"[✓] Saved as {target_path}")
        return True

    except Exception as e:
        print(f"[✗] Error during PDF download: {e}")
        return False

    finally:
        driver.quit()
