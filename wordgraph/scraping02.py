# coding: utf-8

import requests
import re
import sqlite3
import hashlib
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime

domain = "https://www.nikkan.co.jp"
startpath = "/"

basesoup = BeautifulSoup(requests.get(domain + startpath).text, "lxml")

links = []
for a in basesoup.find_all("a", href=re.compile("^/articles/view/[0-9]+")):
    links.append(domain + a.get("href"))
links = list(set(links))

texts = []
count = 0

for link in links[:5]:
    sleep(2)
    res = requests.get(link)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "lxml")

    title = "".join([x.text.strip() for x in soup.find_all("div", class_="ttl")])
    main = "".join([x.text.strip() for x in soup.find("div", class_="txt").find_all("p")])
    text = (title + " " + main).replace("\u3000"," ")
    texts.append(text)
    
    count = count + 1
    print (datetime.now().isoformat()+":("+str(count)+"/"+str(len(links))+")")

dbname = "text.db"
dbcon = sqlite3.connect(dbname)
dbcur = dbcon.cursor()

for text in texts:
    insert = "INSERT INTO rawtext(id, source, time, rawtext) VALUES(?, ?, ?, ?)"

    id = hashlib.md5(text.encode("utf-8")).hexdigest()
    source = "日刊工業新聞"
    time = datetime.now().isoformat()
    
    args = (id, source, time, text)
    
    try:
        dbcur.execute(insert, args)
    except sqlite3.Error as e:
        print('sqlite3:', e.args[0])
    
dbcon.commit()
dbcon.close()
print (datetime.now().isoformat()+":db written")

