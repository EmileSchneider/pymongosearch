import pymongo
import requests
import json
from lxml.html import fromstring
from bs4 import BeautifulSoup as bs
from itertools import cycle
import traceback

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["archimaterie"]
mycol = mydb["active"]

def getproxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:1000]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

proxies = getproxies()


def genurl(company):
    return "https://www.startpage.com/do/dsearch?query=" + company

def soupmaker(url):
    s = request.get(url)
    return bs(s.text, features="lxml")

def alllinks(soup):
    links = {}
    anon = {}
    i = 0
    j = 0
    for link in website_data.find_all('a'):
        if "proxy" in link.get('href'):
            anon["link%d" % i] = "\"" + str(link.get('href')) + "\""
            j += 1
        else:
            i += 1
            if i > 14:
                links["link%d" % i] = "\"" + str(link.get('href')) + "\""
    yield links, anon

def updatedoc(doc, links):
    var = json.dumps(links, indent=4)
    linksjson = json.loads(var)
    mycol.update_one(doc, {"$push": linksjson })


def main():
    for doc in mycol.find():
        updatedoc(doc, alllinks(soupmaker(genurl(str(doc['name']))))[0])
        
