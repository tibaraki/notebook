# coding: utf-8

import logging
import sqlite3
from datetime import datetime
from gensim.models import word2vec

startdate = datetime.now().date().isoformat()

logging.basicConfig(filename='./log/genmodel.log', format='%(asctime)s : %(module)s : %(levelname)s : %(message)s', level=logging.INFO)

dbname = "words.db"
dbcon = sqlite3.connect(dbname)
dbcon.row_factory = sqlite3.Row

file = open("./tmp/txt", mode="w", encoding="utf-8", newline="\n")

sentences = map(lambda x: x["words"], dbcon.execute("select * from wordstbl"))

for sentence in sentences:
    file.write(sentence + "\n")

file.close()
dbcon.close()

logging.info("word2vec start")

ls = word2vec.LineSentence('./tmp/txt')
model = word2vec.Word2Vec(ls, sg=1, size=200, min_count=1, window=10, hs=0, negative=15, iter=5, sample=0.001)

logging.info("word2vec end")

model.save("./vec/vec_" + startdate)

logging.info("./vec/vec_" + startdate + " saved")


