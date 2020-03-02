import json
import requests
import asyncio
import pymongo
from bs4 import BeautifulSoup as bs
import aiohttp


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["newdb"]
mycol = mydb["active"]


async def donwload_aio(urls):
    async def download(url):
        print(f"Start downloading {url}")
        async with aiohttp.ClientSession() as s:
            resp = await s.get(url)
            out = makesoup(await resp.text())
            links  = alllinks(out)
            updatedoc(docs[urls.index(url)], links)
        print(f"Done downloading {url}")
        return out

    return await asyncio.gather(*[download(url) for url in urls])


def updatedoc(doc, links):
    var = json.dumps(links, indent=4)
    linksjson = json.loads(var)
    print("update: " + str(linksjson))
    mycol.update_one(doc, {"$push": linksjson })


def alllinks(soup):
    links = {}
    anon = {}
    i = 0
    j = 0
    for link in soup.find_all('a'):
        if "proxy" in link.get('href'):
            anon["link%d" % i] = "\"" + str(link.get('href')) + "\""
            j += 1
        else:
            i += 1
            if i > 14:
                links["link%d" % i] = "\"" + str(link.get('href')) + "\""
    return links


def makesoup(reqobj):
    return bs(reqobj, "html.parser")


def genurl(company):
    return  "https://www.startpage.com/do/dsearch?query=" + company

urls = []

docs = [doc for doc in mycol.find()]

for d in docs:
    urls.append(genurl(str(d['name'])))


loop = asyncio.get_event_loop()
result = loop.run_until_complete(donwload_aio(urls[:200]))