
# coding: utf-8

# In[7]:


import requests
import re
import operator
from time import sleep
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime

domain = "https://www.nikkei.com"
startpath = "/business"


# In[3]:


basesoup = BeautifulSoup(requests.get(domain + startpath).text, "lxml")


# In[4]:


links = []
for a in basesoup.find_all("a", href=re.compile("^/article/.+/$")):
    links.append(domain + a.get("href"))
links = list(set(links))


# In[10]:


texts = []
count = 0

for link in links:
    sleep(2)

    res = requests.get(link)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "lxml")

    title = soup.find("meta", property="og:title").get("content").strip()
    main = soup.find("meta", property="og:description").get("content").strip()
    text = (title + " " + main).replace("\u3000"," ").replace("（ニュースこう読む）","")

    texts.append(text)
    
    count = count + 1
    print (datetime.now().isoformat()+":("+str(count)+"/"+str(len(links))+")")


# In[39]:


import sqlite3
import hashlib

dbname = "text.db"
dbcon = sqlite3.connect(dbname)
dbcur = dbcon.cursor()

for text in texts:
    insert = "INSERT INTO rawtext(id, source, time, rawtext) VALUES(?, ?, ?, ?)"

    id = hashlib.md5(text.encode("utf-8")).hexdigest()
    source = "日経新聞（ビジネス）"
    time = datetime.now().isoformat()
    
    args = (id, source, time, text)
    
    try:
        dbcur.execute(insert, args)
    except sqlite3.Error as e:
        print('sqlite3:', e.args[0])
    
dbcon.commit()
dbcon.close()
print (datetime.now().isoformat()+":db written")


# In[32]:




