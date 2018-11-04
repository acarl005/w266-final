import asyncio
import aiohttp
import os
import csv
from tqdm import tqdm

code_dirname = os.path.dirname(__file__)

sem = asyncio.Semaphore(10)

async def http_get(session, url):
    async with sem:
        print(f"getting {url}")
        async with session.get(url) as resp:
            text = await resp.text(encoding="ISO-8859-1")
            print(f"got page {url}. status: {resp.status} length: {len(text)}")
            return text

async def download(dirname, home_url, get_script_urls, url_to_key):
    session = aiohttp.ClientSession()

    try:
        data_dirname = os.path.join(code_dirname, "..", "data", dirname, "raw")
        if not os.path.exists(data_dirname):
            os.makedirs(data_dirname)

        home_html = await http_get(session, home_url)
        urls = get_script_urls(home_html)
        pages = await asyncio.gather(*[http_get(session, url) for url in urls])
        for url, page in zip(urls, pages):
            key = url_to_key(url)
            with open(os.path.join(data_dirname, f"{key}.html"), "w") as f:
                f.write(page)
    finally:
        await session.close()

def parse(dirname, html_page_to_structured):
    raw_data_dirname = os.path.join(code_dirname, "..", "data", dirname, "raw")
    parsed_data_dirname = os.path.join(code_dirname, "..", "data", dirname, "parsed")
    if not os.path.exists(parsed_data_dirname):
        os.makedirs(parsed_data_dirname)
    files = os.listdir(raw_data_dirname)
    for filename in tqdm(files):
        file_stem, _ = os.path.splitext(filename)
        with open(os.path.join(raw_data_dirname, filename)) as f:
            html = f.read()
            data = html_page_to_structured(html, file_stem)
            with open(os.path.join(parsed_data_dirname, f"{file_stem}.csv"), "w") as csvfile:
                spamwriter = csv.writer(csvfile)
                for row in data:
                    spamwriter.writerow(row)

if __name__ == "__main__":
    raise Exception("this is mnot meant to be run as a standalone script")

