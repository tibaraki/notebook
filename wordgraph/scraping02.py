
# coding: utf-8

# In[1]:


import requests
import re
import operator
from time import sleep
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime

domain = "https://www.nikkan.co.jp"
startpath = "/"


# In[2]:


basesoup = BeautifulSoup(requests.get(domain + startpath).text, "lxml")


# In[3]:


links = []
for a in basesoup.find_all("a", href=re.compile("^/articles/view/[0-9]+")):
    links.append(domain + a.get("href"))
links = list(set(links))


# In[4]:


texts = []
count = 0

for link in links:
    sleep(2)
    res = requests.get(link)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "lxml")

    title = reduce(operator.add ,[x.text.strip() for x in soup.find_all("div", class_="ttl")], "")
    main = reduce(operator.add ,[x.text.strip() for x in soup.find_all("p", style="text-indent:1em;")], "")
    text = (title + " " + main).replace("\u3000"," ")
    texts.append(text)
    
    count = count + 1
    print (datetime.now().isoformat()+":("+str(count)+"/"+str(len(links))+")")


# In[14]:


import sqlite3
import hashlib

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

