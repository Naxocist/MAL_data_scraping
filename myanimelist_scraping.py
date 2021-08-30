from bs4 import BeautifulSoup
from gevent import monkey as curious_george

curious_george.patch_all(thread=False, select=False)
import requests
import grequests
import csv
import math

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

rs = (grequests.get(u) for u in urls)
resp = grequests.map(rs)
print(len(urls))
for r in resp:  # Through all links (each page of genre)
    print("I'm here")

    soup = BeautifulSoup(r.text, 'lxml')
    name_tag = soup.find_all('a', class_='link-title')
    print(name_tag)
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
    season = soup.find('span', class_="information season")
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
