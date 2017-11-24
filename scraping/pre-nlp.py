# -*- coding: utf-8 -*-

import sqlite3

import MeCab
import unicodedata
tagger = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd/')
tagger.parse("")#バグ回避

dbcon1 = sqlite3.connect("file:text.db", uri=True)
dbcon1.row_factory = sqlite3.Row

for row in dbcon1.execute("select * from rawtext order by time desc limit 5"):
	print(row["rawtext"])
	node = tagger.parseToNode(unicodedata.normalize("NFKC", row["rawtext"]))
	separated_text = ""
	while node:
		features = node.feature.split(",")
		if features[0] in ["名詞"] and features[1] not in ["接尾", "数", "接続詞的", "非自立", "代名詞"]:
			separated_text = separated_text + " " + node.surface
			print(node.surface + " " + node.feature)
		node = node.next
	#print(separated_text)


dbcon1.close()

