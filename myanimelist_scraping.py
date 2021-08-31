from bs4 import BeautifulSoup
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
import requests
import grequests
import csv
import math
import aiohttp
import asyncio

animes_name = []
animes_episode = []
animes_rank = []
animes_link = []
animes_pic = []
animes_season = []
animes_genre = []
urls = []
end = 0

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
        s = BeautifulSoup(response, 'html.parser')
        data = s.find_all('a', class_='link-title')
        for index in data:
            name = index.text
            link = index['href']
            animes_name.append(name)
            animes_link.append(link)
            print(name, link)
            print(url)


async def other_info(session, url):
    async with session.get(url) as resp:
        response = await resp.text()
        s = BeautifulSoup(response, 'html.parser')
        p = s.find('img', itemprop="image")['data-src']
        e = s.find('span', id="curEps")
        s = s.find('span', class_="information season")
        r = s.find('span', class_="numbers ranked")
        animes_pic.append(p)
        animes_episode.append(e)
        animes_season.append(s)
        animes_rank.append(r)
        print(s, p, e, s, r)
        print(url)


async def semaphore(session, url, sem):
    async with sem:
        return await name_link(session, url)


async def main(links: list):
    sem = asyncio.Semaphore(7)  # task grouping
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(semaphore(session, url, sem)) for url in links]
        gather = await asyncio.gather(*tasks)


n = asyncio.get_event_loop()
n.run_until_complete(main(urls))
n.close()

print("Finished Scraping")
print("There are", len(animes_name), "animes")

p = asyncio.get_event_loop()
p.run_until_complete(main(animes_link))
p.close()

print("name", animes_name)
print("link", animes_link)
print("pic: ", animes_pic)
print("season: ", animes_season)
print("ep: ", animes_episode)
print("rank: ", animes_rank)

with open('animes.csv', 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'episode', 'rank', 'link', 'pic', 'season', 'genre'])
    for i in range(len(animes_name)):
        writer.writerow([animes_name[i], animes_episode[i], animes_rank[i], animes_link[i], animes_pic[i],
                         animes_season[i]])
