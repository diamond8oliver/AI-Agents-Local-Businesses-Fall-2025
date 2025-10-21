import re
from urllib.parse import urljoin, urldefrag, urlparse
from collections import deque
from typing import Dict, List, Set, Tuple

import requests
from bs4 import BeautifulSoup


def is_same_domain(url: str, base_netloc: str) -> bool:
    try:
        return urlparse(url).netloc == base_netloc
    except Exception:
        return False


def normalize_url(base_url: str, link: str) -> str:
    abs_url = urljoin(base_url, link)
    abs_url, _frag = urldefrag(abs_url)
    return abs_url


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Remove scripts/styles/nav/footer
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines()]
    # Collapse excessive whitespace
    text = "\n".join([ln for ln in lines if ln])
    # Trim long runs of spaces
    text = re.sub(r"\s+", " ", text)
    return text


def crawl_site(start_url: str, max_pages: int = 50, timeout: int = 10) -> List[Tuple[str, str]]:
    parsed = urlparse(start_url)
    base_netloc = parsed.netloc

    visited: Set[str] = set()
    queue: deque[str] = deque([start_url])
    results: List[Tuple[str, str]] = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": "LocalBusinessBot/1.0"})
            if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
                continue
        except Exception:
            continue

        text = extract_text(resp.text)
        if text:
            results.append((url, text))

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if not href or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            next_url = normalize_url(url, href)
            if is_same_domain(next_url, base_netloc) and next_url not in visited:
                queue.append(next_url)

    return results


