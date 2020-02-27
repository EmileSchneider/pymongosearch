import pymongo
import requests
import json
from lxml.html import fromstring
from bs4 import BeautifulSoup as bs
from itertools import cycle
import traceback

# mongodb integration
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["archimaterie"]
mycol = mydb["active"]

# get updated list of proxies


def get_proxies():
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

# proxies cycling stuff
#proxies = get_proxies()
#proxy_pool = cycle(proxies)


# main function; goes through every doc in collection
for doc in mycol.find():
    #proxy = next(proxy_pool)

    # get company name
    company = str(doc['name'])
    print(company)

    # gen url
    url = "https://www.startpage.com/do/dsearch?query=" + company
    #url = "https://localhost:8128/?q=" + company
    #url = "https://www.google.com/search?query=" + company
    print(url)

    # try to get tasty websoup; (optional: add ", proxies={"http": proxy, "https": proxy}"
    # to requests.get(url))
    # try:
    search = requests.get(url)
    website_data = bs(search.text, features="lxml")

# extract every link from soup into a set
    links = {}
    anon = {}
    i = 0
    j = 0
    for link in website_data.find_all('a'):
        if "proxy" in link.get('href'):
            anon["link%d" % i] = "\"" + str(link.get('href')) + "\""
            j += 1

        # elif "startpage" or "startmail" in link.get('href'):
        #    print("--------------")
        else:
            i += 1
            if i > 14:
                links["link%d" % i] = "\"" + str(link.get('href')) + "\""


# update collection with soup
    var = json.dumps(links, indent=4)
    jsonFromSearch = json.loads(var)
    print(var)
    mycol.update_one(doc, {"$push": jsonFromSearch})

    # except:
    # print("error")
