from bs4 import BeautifulSoup
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
import requests
import csv
import math
import aiohttp
import asyncio
import time

animes_name = []
animes_episode = []
animes_rank = []
animes_link = []
animes_pic = []
animes_season = []
animes_genre = []
urls = []

catogories = requests.get('https://myanimelist.net/anime.php').text
soup_g = BeautifulSoup(catogories, 'lxml')

genre_group = soup_g.find_all('a', class_='genre-name-link')
genres = [i['href'] for i in genre_group]
del genres[43:]

quantities = [q.text for q in genre_group]
del quantities[43:]
for i, j in enumerate(quantities):
    quantities[i] = math.ceil(int(j[j.index("(") + 1:-1].replace(',', '')) / 100)

pair = {d: quantities[i] for i, d in enumerate(genres)}

for k, v in pair.items():
    for i in range(1, v+1):
        url = "https://myanimelist.net" + k + f"?page={i}"
        urls.append(url)


async def name_link(session, url):
    async with session.get(url) as resp:
        response = await resp.text()
        print("scraping:", url)
        s = BeautifulSoup(response, 'html.parser')
        return s


async def other_info(session, url):  # fetch other information
    async with session.get(url) as resp:
        response = await resp.text()
        print("scraping anime:", url)
        s = BeautifulSoup(response, 'html.parser')
        return s


async def semaphore(session, url, sem):
    async with sem:
        return await name_link(session, url)


async def alt_semaphore(session, url, sem):
    async with sem:
        return await other_info(session, url)


async def main(u: list):  # main async function
    sem = asyncio.Semaphore(100)  # task grouping
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(semaphore(session, url, sem)) for url in u]
        time.sleep(1)
        return await asyncio.gather(*tasks)


async def fetch_other(u: list):
    sem = asyncio.Semaphore(100)
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(alt_semaphore(session, url, sem)) for url in u]
        time.sleep(1)
        return await asyncio.gather(*tasks)


# urls = ["https://myanimelist.net/anime/genre/1/Action"]

result = asyncio.get_event_loop().run_until_complete(main(urls))
for r in result:
    data = r.find_all('a', class_='link-title')
    for index in data:
        name = index.text
        link = index['href']
        if name in animes_name:
            continue
        animes_name.append(name)
        animes_link.append(link)
        print(name, link)

print("Done scraping + Add to txt file")
print("There are", len(animes_name), "animes")

result = asyncio.get_event_loop().run_until_complete(fetch_other(animes_link))
for r in result:
    p = r.find('img', itemprop="image")
    e = r.find('span', id="curEps")
    s = r.find('span', class_="information season")
    p = "" if p is None else p['data-src']
    e = "" if e is None else e.text
    s = "" if s is None else s.text
    animes_pic.append(p)
    animes_episode.append(e)
    animes_season.append(s)

print("name: ", animes_name)
print("link: ", animes_link)
print("pic: ", animes_pic)
print("season: ", animes_season)
print("ep: ", animes_episode)
print("rank: ", animes_rank)

with open('animes.csv', 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'episode', 'link', 'pic', 'season', 'genre'])
    for i in range(len(animes_name)):
        writer.writerow([animes_name[i], animes_episode[i], animes_link[i], animes_pic[i],
                         animes_season[i]])
