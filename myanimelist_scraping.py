from bs4 import BeautifulSoup
import requests
import csv
import math
import aiohttp
import asyncio
import time

animes_name, animes_episode, animes_rank, animes_link, animes_pic, animes_season, \
    animes_season, urls = [[] for _ in range(8)]

req = requests.get('https://myanimelist.net/anime.php').text
soup_g = BeautifulSoup(req, 'lxml')
genre_group = soup_g.find_all('a', class_='genre-name-link')
genres = [i['href'] for i in genre_group]
del genres[43:]

quantities = [q.text for q in genre_group]
del quantities[43:]

for i, j in enumerate(quantities):
    quantities[i] = math.ceil(int(j[j.index("(") + 1:-1].replace(',', '')) / 100)

# -------------------------------------------------------------------------------------

pair = {"https://myanimelist.net" + d: quantities[i] for i, d in enumerate(genres)}

for k, v in pair.items():  # declare each genre's number pages
    urls.extend([k + f"?page={i}" for i in range(1, v+1)])

print(urls)


async def fetch(session, url):
    async with session.get(url) as request:
        response = await request.text()
        print(url)
        return response


async def main(urls):
    async with aiohttp.ClientSession() as session:

        task = [fetch(session, url) for url in urls]
        return await asyncio.gather(*task)
    
    
name_link = asyncio.get_event_loop().run_until_complete(main(urls))

for nl in name_link:  # get names and links of all animes
    html = BeautifulSoup(nl, 'html.parser')
    data = html.find_all('a', class_='link-title')
    for d in data:
        name = d.text
        link = d['href']

        if name in animes_name:
            continue
        animes_name.append(name)
        animes_link.append(link)
        print(name, link)

print(f"Big scrape finished or server restricted")
print("There are", len(animes_name), "animes")

other_info = asyncio.get_event_loop().run_until_complete(main(animes_link))

for index, r in enumerate(other_info):  # get other information reference from links of animes
    print(index + 1)
    html = BeautifulSoup(r, 'html.parser')
    p = html.find('img', itemprop="image")
    e = html.find('span', id="curEps")
    s = html.find('span', class_="information season")

    picture = p['data-src'] if p is not None else ""
    ep = e.text if e is not None else ""
    season = s.text if s is not None else ""

    animes_pic.append(picture)
    animes_episode.append(ep)
    animes_season.append(season)
    print(picture, ep, season)

with open('animes.csv', 'w', encoding="utf8", newline='') as f:  # Write to csv file
    writer = csv.writer(f)
    writer.writerow(['name', 'episode', 'link', 'pic', 'season', 'genre'])
    for i in range(len(animes_name)):
        writer.writerow([animes_name[i], animes_episode[i], animes_link[i], animes_pic[i],
                         animes_season[i]])
