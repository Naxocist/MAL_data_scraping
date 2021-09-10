from bs4 import BeautifulSoup
import requests
import csv
import math
import aiohttp
import asyncio
import time


def generate_urls():
    urls = []
    req = requests.get('https://myanimelist.net/anime.php').text  # genre page
    soup_g = BeautifulSoup(req, 'lxml')
    genre_group = soup_g.find_all('a', class_='genre-name-link')
    genres = [i['href'] for i in genre_group]
    del genres[43:]

    quantities = [q.text for q in genre_group]
    del quantities[43:]

    for i, j in enumerate(quantities):
        pages = math.ceil(int(j[j.index("(") + 1:-1].replace(',', '')) / 100)  # number of page in each genre
        quantities[i] = pages

    pair = {"https://myanimelist.net" + d: quantities[i] for i, d in enumerate(genres)}

    for k, v in pair.items():
        urls.extend([k + f"?page={i}" for i in range(1, v + 1)])

    return urls


async def fetch(session, url):
    global track
    async with session.get(url) as request:
        track += 1
        print("Tracking:", track)
        print(url)
        response = await request.text()
        return response


async def semaphore(session, url, sem):
    async with sem:
        return await fetch(session, url)


async def main(urls):
    sem = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        tasks = [semaphore(session, url, sem) for url in urls]
        return await asyncio.gather(*tasks)


def process_names_link(data):
    for i, nl in enumerate(data):
        html = BeautifulSoup(nl, 'html.parser')
        data = html.find_all('a', class_='link-title')  # list of a tag of anime names
        for d in data:
            name = d.text
            link = d['href']
            if name in animes_name:  # dulplicate anime
                continue

            animes_name.append(name)
            animes_link.append(link)
            alt_animes_link.append(link)
        print("Page", i + 1, "out of", len(name_link))


def process_other_info(data):
    for i, j in enumerate(data):  # other info
        html = BeautifulSoup(j, 'html.parser')

        p = html.find('img', itemprop="image")
        e = html.find('span', id="curEps")
        s = html.find('span', class_="information season")
        g = html.find_all('span', itemprop="genre")
        r = html.find('span', class_="numbers ranked")

        picture = p['data-src'] if p else ""
        ep = e.text if e else "N/A"
        season = s.text if s else "OVA ONA SPECIAL"
        genre = " ".join([j.text for j in g])
        if r:
            rank = r.text[r.text.index("#") + 1:] if r.text != "Ranked N/A" else "Unranked"
        else:
            rank = "Unranked"

        print(i + 1)
        print(picture, ep, season, genre, rank)
        animes_pic.append(picture)
        animes_episode.append(ep)
        animes_season.append(season)
        animes_genre.append(genre)
        animes_rank.append(rank)


if __name__ == '__main__':
    animes_name, animes_episode, animes_rank, animes_link, animes_pic, animes_season, \
        animes_genre, alt_animes_link = [[] for _ in range(8)]
    track = 0
    urls = generate_urls()
    # urls = ['https://myanimelist.net/anime/genre/1/Action']

    name_link = asyncio.get_event_loop().run_until_complete(main(urls))  # scrape all names, links in HTML
    process_names_link(name_link)
    print("There are", len(animes_name), "animes")
    print("Cooling down after fetch... 300 seconds")
    time.sleep(300)
    track = 0
    chunk = 150
    cycle = math.ceil(len(alt_animes_link)/chunk)  # define round in for loop

    for c in range(cycle):  # Has the most chance to crash
        temp = alt_animes_link[:chunk] if len(alt_animes_link) >= chunk else alt_animes_link

        other_info = asyncio.get_event_loop().run_until_complete(main(temp))  # scrape other information in HTML
        process_other_info(other_info)

        alt_animes_link[:chunk] = []
        print("Scrape:", len(animes_name) - len(alt_animes_link), "out of", len(animes_name))
        print("Cool down for 300 seconds.....")
        time.sleep(300)

    print("alt_animes_link:", alt_animes_link)  # must be []
    print("Len animes_name: ", len(animes_name))
    print("Len animes_episode", len(animes_episode))
    print("Len animes_link", len(animes_link))
    print("Len animes_pic", len(animes_pic))
    print("Len animes_season", len(animes_season))
    print("Len animes_genre", len(animes_genre))
    print("Len animes_rank", len(animes_rank))

    with open('animes.csv', 'w', encoding="utf8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'episode', 'link', 'pic', 'season', 'genre', 'rank'])
        for i in range(len(animes_name)):
            writer.writerow([animes_name[i], animes_episode[i], animes_link[i], animes_pic[i],
                             animes_season[i], animes_genre[i], animes_rank[i]])
    print("Finished scraping...")