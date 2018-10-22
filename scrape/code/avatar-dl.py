import asyncio
from urllib import parse

from bs4 import BeautifulSoup

from main import download

home_url = "http://atla.avatarspirit.net/transcripts.php"

def get_script_urls(home_html):
    soup = BeautifulSoup(home_html, "html5lib")
    table = soup.find("div", "content").find("table")
    hrefs = [link.get("href") for link in table.select("a[href]")]
    return hrefs[13:]

def url_to_key(url):
    query_params = parse.parse_qs(parse.urlsplit(url).query)
    return query_params['num'][0]


loop = asyncio.get_event_loop()
loop.run_until_complete(download("avatar", home_url, get_script_urls, url_to_key))
loop.close()

