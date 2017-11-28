
# coding: utf-8

# In[7]:


import requests
import re
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime

domain = "https://www.kobe-np.co.jp"
startpath = "/news/keizai"


# In[8]:


basesoup = BeautifulSoup(requests.get(domain + startpath).text, "lxml")


# In[9]:


links = []
for a in basesoup.find_all("a", href=re.compile("/news/keizai/[0-9]+/.*")):
    links.append(domain + a.get("href"))


# In[10]:


texts = []
count = 0

for link in links:
    sleep(2)
    soup = BeautifulSoup(requests.get(link).text, "lxml")
    texts.append(soup.find("h4", class_="news-title").text.strip() + " " + soup.find("div", class_="news-contents").text.strip())
    
    count = count + 1
    print (datetime.now().isoformat()+":("+str(count)+"/"+str(len(links))+")")


# In[6]:


import sqlite3
import hashlib

dbname = "text.db"
dbcon = sqlite3.connect(dbname)
dbcur = dbcon.cursor()

for text in texts:
    insert = "INSERT INTO rawtext(id, source, time, rawtext) VALUES(?, ?, ?, ?)"

    id = hashlib.md5(text.encode("utf-8")).hexdigest()
    source = "神戸新聞（経済）"
    time = datetime.now().isoformat()
    
    args = (id, source, time, text)
    
    try:
        dbcur.execute(insert, args)
    except sqlite3.Error as e:
        print('sqlite3:', e.args[0])
    
dbcon.commit()
dbcon.close()
print (datetime.now().isoformat()+":db written")

