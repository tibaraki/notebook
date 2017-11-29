import os
import glob
import json
import re
import sqlite3
from bottle import route, run, HTTPResponse, static_file, request
from datetime import datetime

from gensim.models import word2vec

hostname = "0.0.0.0"
port = 80
vecdir = "vec/"

def res_json(obj):
    body = json.dumps(obj, ensure_ascii=False)
    res = HTTPResponse(status=200, body=body)
    res.set_header('Content-Type', 'application/json')
    return res

@route("/calender")
def calender():
    return res_json(sorted([x.replace(vecdir + "vec_","") for x in glob.glob(vecdir + 'vec_*')], reverse=True))

@route("/words/count", method="GET")
def words_count():
    if any([x not in request.query.keys() for x in ["word"]]):
        return res_json({"error": "invalid args"})
    word = request.query.word

    index = 0
    if "index" in request.query.keys():
        if not re.match("^[0-9]{1,2}$", request.query.index):
            return res_json({"error": "invalid index"})
        index = int(request.query.index)
    
    wordsrank = {}
    dbword = sqlite3.connect("file:words.db", uri=True)
    dbword.row_factory = sqlite3.Row
    for row in dbword.execute("select * from wordstbl where words match ?", (word,)):
        for w in row["words"].split(" "):
            if w == "":
                continue
            if w in wordsrank:
                wordsrank[w] = wordsrank[w] + 1
            else:
                wordsrank[w] = 1
    wordsrank = sorted(wordsrank.items(), key=lambda x: x[1], reverse=True)[:30]
    dbword.close()

    return res_json(wordsrank)

@route("/words/vec", method="GET")
def words_vec():
    if any([x not in request.query.keys() for x in ["date","word"]]):
        return res_json({"error": "invalid args"})

    date = request.query.date #[]で取得すると文字化けする
    word = request.query.word

    if vecdir + "vec_" + date not in glob.glob(vecdir + 'vec_*'):
        return res_json({"error": "invalid date"})
    
    model = word2vec.Word2Vec.load(vecdir + "vec_" + date)
    if word not in model.wv.vocab:
        return res_json({"error": "'" + word + "' does not exist in vocabulary"})

    index = 0
    if "index" in request.query.keys():
        if not re.match("^[0-9]{1,2}$", request.query.index):
            return res_json({"error": "invalid index"})
        index = int(request.query.index)
                    
    nodes = []
    links = []

    nodes.append({ "id":word, "group":"1" })

    for w1 in model.most_similar(positive=[word], negative=[], topn=index+10)[index:]:
        if w1[0] not in {x["id"] for x in nodes}:
            nodes.append({ "id":w1[0], "group":"2" })
        links.append({ "source":word, "target":w1[0], "value": w1[1] })
        for w2 in model.most_similar(positive=[w1[0]], negative=[], topn=index+5)[index:]:
            if w2[0] not in {x["id"] for x in nodes}:
                nodes.append({ "id":w2[0], "group":"3" })
            links.append({ "source":w1[0], "target":w2[0], "value": w2[1] })

    return res_json({ "nodes":nodes, "links":links })

@route("/")
@route("/<filename:path>")
def root(filename="index.html"):
    return static_file(filename, root="static")

run(host=hostname, port=int(os.environ.get("PORT", port)))
