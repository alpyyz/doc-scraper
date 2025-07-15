import requests
from bs4 import BeautifulSoup

def download_pdf_scihub(original_url, save_path):
    sci_hub_url = f"https://sci-hub.se/{original_url}"
    try:
        # Get the Sci-Hub page
        res = requests.get(sci_hub_url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Find iframe with the PDF
        iframe = soup.find("iframe")
        if not iframe or not iframe.get("src"):
            print(f"PDF not found on Sci-Hub for: {original_url}")
            return False

        pdf_url = iframe["src"]
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url
        elif pdf_url.startswith("/"):
            pdf_url = "https://sci-hub.se" + pdf_url

        # Download the PDF
        pdf_res = requests.get(pdf_url, stream=True, timeout=15)
        pdf_res.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in pdf_res.iter_content(1024):
                f.write(chunk)
        print(f"PDF downloaded: {save_path}")
        return True
    except Exception as e:
        print(f"Failed to download PDF for {original_url}: {e}")
        return False
