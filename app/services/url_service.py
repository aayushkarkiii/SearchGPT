import httpx
from html.parser import HTMLParser

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fed = []
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head", "title", "meta", "nav", "footer"):
            self.ignore = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head", "title", "meta", "nav", "footer"):
            self.ignore = False

    def handle_data(self, data):
        if not self.ignore:
            text = data.strip()
            if text:
                self.fed.append(text)

    def get_data(self) -> str:
        return "\n".join(self.fed)

async def extract_url_text(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        html_content = resp.text
    
    stripper = HTMLStripper()
    stripper.feed(html_content)
    text = stripper.get_data().strip()
    return text
