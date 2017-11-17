
# coding: utf-8

# In[2]:


import sqlite3


# In[3]:


dbname = "text.db"
dbcon = sqlite3.connect(dbname)
dbcur = dbcon.cursor()
#dbcur.execute("DROP TABLE rawtext;")
dbcur.execute("CREATE TABLE rawtext(id VARCHAR(36) NOT NULL PRIMARY KEY, source VARCHAR(20), time VARCHAR(20), rawtext VARCHAR(1024));")
dbcon.commit()
dbcon.close()


# In[5]:


#dbname = "text.db"
#dbcon = sqlite3.connect(dbname)
#df = pandas.read_sql_query("select * from rawtext", dbcon)
#dbcon.close()

#pandas.set_option("display.max_colwidth", 1000)
#pandas.set_option("display.max_rows", 100)
#df

