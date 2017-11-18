# -*- coding: utf-8 -*-

import sqlite3

import MeCab
import unicodedata
tagger = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd/')
tagger.parse("")#バグ回避

dbcon1 = sqlite3.connect("file:text.db", uri=True)
dbcon1.row_factory = sqlite3.Row

for row in dbcon1.execute("select * from rawtext limit 1"):
	print(row["rawtext"])
	node = tagger.parseToNode(unicodedata.normalize("NFKC", row["rawtext"]))
	separated_text = ""
	while node:
		if node.feature.split(",")[0] in ["名詞"] :
			separated_text = separated_text + " " + node.surface
		node = node.next
	print(separated_text)


dbcon1.close()

