from bs4 import BeautifulSoup
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
import requests
import grequests
import csv
import asyncio
import aiohttp


animes_name = []
animes_episode = []
animes_rank = []
animes_link = []
animes_pic = []
animes_season = []
animes_genre = []
p = 1
i = 1
end = 0
genre_html = requests.get('https://myanimelist.net/anime.php').text
soup_g = BeautifulSoup(genre_html, 'lxml')
genres = [i['href'] for i in soup_g.find_all('a', class_='genre-name-link')]

for i, j in enumerate(genres):
    if 'Yuri' in j:
        end = i + 1
genres = genres[:end]
print(genres)

# async def fetch(url, session):
#     async with session.get(url) as response:
#         html = await response.read()
#         return html
#
#
# async def main():
#     global p
#     urls = []
#
#     async with aiohttp.ClientSession() as session:
#         for g in genres:
#             while True:
#                 url = 'https://myanimelist.net' + g + f"?page={p}"
#                 fet = await fetch(url, session)
#                 html = fet.decode()
#                 if html.find("link-title") == -1:
#                     break
#                 # tasks.append(asyncio.create_task(fetch(url, session)))
#                 print(url)
#                 urls.append(url)
#                 p += 1
#             p = 1
#
#     return urls
#
# urls = asyncio.run(main())


def fetch_data_check(url):
    req = requests.get(url).text
    error = BeautifulSoup(req, 'lxml').text
    return False if "404 Not Found" in error else True


urls = []
for g in genres:
    while True:
        url = f'https://myanimelist.net{g}?page={p}'
        if not fetch_data_check(url):
            break
        print(url)
        urls.append(url)
        p += 1
    p = 1

print(urls)

rs = (grequests.get(u) for u in urls)
resp = grequests.map(rs)
print(resp)
for r in resp:  # Through all links (each page of genre)
        soup = BeautifulSoup(r.text, 'lxml')
        name_tag = soup.find_all('a', class_='link-title')

        if name_tag is None:
            break
        for data in name_tag:
            name = data.text
            link = data['href']
            if name in animes_name:
                continue
            animes_name.append(name)
            animes_link.append(link)
            print(name)
            print(link)

print("Finished Scraping")
print("There are", len(animes_name), "animes")

requests = (grequests.get(url) for url in animes_link)
response = grequests.map(requests)
for r in response:  # grab other information
    soup = BeautifulSoup(r.text, 'lxml')
    pic = soup.find('img', itemprop="image")
    season = soup.ftind('span', class_="information season")
    rank = soup.find('span', class_="numbers ranked")
    episode = soup.find('span', id="curEps")
    if pic is None:
        pic = ""
    else:
        pic = pic['data-src']
    if season is None:
        season = ""
    else:
        season = season.a.text
    if rank is None:
        rank = ""
    else:
        rank = rank.text
    if episode is None:
        episode = ""
    else:
        episode = episode.text
    animes_pic.append(pic)
    animes_season.append(season)
    animes_episode.append(episode)
    animes_rank.append(rank)
    print(pic, season, episode, rank)

with open('animes.csv', 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'episode', 'rank', 'link', 'pic', 'season', 'genre'])
    for i in range(len(animes_name)):
        writer.writerow([animes_name[i], animes_episode[i], animes_rank[i], animes_link[i], animes_pic[i],
                         animes_season[i]])
