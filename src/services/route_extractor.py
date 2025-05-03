# app/services/route_extractor.py
import httpx
import xmltodict
from typing import List
from playwright.async_api import async_playwright

# Use a realistic UA & accept XML/text
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "application/xml, text/html;q=0.9",
}

async def extract_all_routes(domain: str) -> List[str]:
    """
    Try robots.txt → sitemap.xml (up to 5 URLs). If that fails,
    crawl the site (up to 5 unique pages) with Playwright.
    """
    domain = domain.rstrip("/")
    robots_url  = f"{domain}/robots.txt"
    sitemap_url = f"{domain}/sitemap.xml"

    # 1️⃣ Attempt sitemap via robots.txt
    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
        try:
            r = await client.get(robots_url)
            r.raise_for_status()
            if "Disallow: /sitemap.xml" not in r.text:
                # fetch sitemap.xml
                s = await client.get(sitemap_url)
                s.raise_for_status()
                doc = xmltodict.parse(s.text)
                urls = _parse_sitemap(doc)
                if urls:
                    return urls[:5]
        except Exception:
            pass  # fall back to crawling

    # 2️⃣ Fallback crawler
    return await _crawl_with_playwright(domain)


def _parse_sitemap(doc: dict) -> List[str]:
    """
    Given a parsed xmltodict document, extract up to 5 <loc> URLs
    from either <urlset> or nested <sitemapindex>.
    """
    urls: List[str] = []
    # Direct <urlset>
    if doc.get("urlset", {}).get("url"):
        entries = doc["urlset"]["url"]
        if not isinstance(entries, list):
            entries = [entries]
        for u in entries:
            loc = u.get("loc")
            if loc:
                urls.append(loc)
        return urls

    # Nested <sitemapindex>
    if doc.get("sitemapindex", {}).get("sitemap"):
        entries = doc["sitemapindex"]["sitemap"]
        if not isinstance(entries, list):
            entries = [entries]
        # for each nested sitemap, try to extract up to 5 URLs total
        for sm in entries:
            loc = sm.get("loc")
            if not loc:
                continue
            try:
                inner = xmltodict.parse(httpx.get(loc, headers=HEADERS, timeout=10.0).text)
                inner_urls = _parse_sitemap(inner)
                for iu in inner_urls:
                    if len(urls) >= 5:
                        return urls
                    urls.append(iu)
            except Exception:
                continue
        return urls

    return []


async def _crawl_with_playwright(base_url: str) -> List[str]:
    """
    Simple breadth‑first crawl (up to 5 unique pages) using Playwright.
    """
    visited = set()
    to_visit = [base_url]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page    = await browser.new_page()
        await page.set_extra_http_headers({"User-Agent": HEADERS["User-Agent"]})

        while to_visit and len(visited) < 5:
            url = to_visit.pop(0)
            if url in visited:
                continue
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # grab all <a href>
                hrefs = await page.eval_on_selector_all(
                    "a",
                    "els => els.map(e => e.href).filter(h => h.startsWith(base))",
                    arg=base_url
                )
                for h in hrefs:
                    if h not in visited and h not in to_visit and len(visited) + len(to_visit) < 20:
                        to_visit.append(h)
                visited.add(url)
            except Exception:
                # ignore navigation errors
                visited.add(url)

        await browser.close()

    return list(visited)
