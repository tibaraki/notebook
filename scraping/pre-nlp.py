# -*- coding: utf-8 -*-

import sqlite3

import MeCab
import unicodedata
from datetime import datetime

tagger = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd/')
tagger.parse("")#バグ回避

dbtext = sqlite3.connect("file:text.db", uri=True)
dbtext.row_factory = sqlite3.Row

dbword = sqlite3.connect("file:words.db", uri=True)
dbword.row_factory = sqlite3.Row

lasttime = ""
row = dbword.execute("select time from wordstbl order by time desc limit 1").fetchone()
if row is not None:
	lasttime = row["time"]

count = 0
fromtime = ""
totime = ""

for row in dbtext.execute("select * from rawtext where time > ? order by time", (lasttime,)):
	node = tagger.parseToNode(unicodedata.normalize("NFKC", row["rawtext"]))
	separated_text = ""
	while node:
		features = node.feature.split(",")
		if features[0] in ["名詞"] and features[1] not in ["接尾", "数", "接続詞的", "非自立", "代名詞"]:
			separated_text = separated_text + " " + node.surface
		node = node.next
	
	insert = "INSERT INTO wordstbl(id, source, time, words) VALUES(?, ?, ?, ?)"
	args = (row["id"], row["source"], row["time"], separated_text)

	if fromtime > row["time"] or fromtime == "":
		fromtime = row["time"]
	if totime < row["time"]:
		totime = row["time"]

	try:
		dbword.execute(insert, args)
		count = count + 1
	except sqlite3.Error as e:
		print ('sqlite3:', e.args[0])

dbword.commit()
dbword.close()
dbtext.close()

print (datetime.now().isoformat()+":words.db written(" + str(count) + ")(" + fromtime + "~" + totime + ")")

