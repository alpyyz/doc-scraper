import os
import requests

import arxiv


def download_arxiv_papers(query, max_results=5, out_dir="arxiv_pdfs"):
    os.makedirs(out_dir, exist_ok=True)
    
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    for i, result in enumerate(search.results(), 1):
        print(f"[{i}] {result.title}")
        print("→", result.pdf_url)

        # Download the PDF
        response = requests.get(result.pdf_url)
        file_path = os.path.join(out_dir, f"{i:02d}_{result.entry_id.split('/')[-1]}.pdf")
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("✓ Saved:", file_path)


def download_arxiv_sources(query, max_results=5, out_dir="arxiv_src"):
    os.makedirs(out_dir, exist_ok=True)
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    for i, paper in enumerate(client.results(search), 1):
        arxiv_id = getattr(paper, "get_short_id", lambda: paper.entry_id.split("/")[-1])()
        fname = f"{i:02d}_{arxiv_id}.tar.gz"
        try:
            paper.download_source(dirpath=out_dir, filename=fname)  # saves .tar.gz
            print("✓ Saved source:", os.path.join(out_dir, fname))
        except Exception as e:
            print(f"× Source not available for {arxiv_id}: {e}")
