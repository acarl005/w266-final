import asyncio

from bs4 import BeautifulSoup

from main import download

home_url = "https://fangj.github.io/friends/"

def get_script_urls(home_html):
    soup = BeautifulSoup(home_html, "html5lib")
    links = soup.select("a[href]")
    hrefs = [home_url + link.get("href") for link in links]
    return hrefs

#https://fangj.github.io/friends/season/0101.html
def url_to_key(url):
    return url.split("/")[-1].split(".")[0]


loop = asyncio.get_event_loop()
loop.run_until_complete(download("friends", home_url, get_script_urls, url_to_key))
loop.close()

