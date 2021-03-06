import os
import glob
import json
import re
import sqlite3
from bottle import route, run, HTTPResponse, static_file, request
from datetime import datetime
import unicodedata
import numpy as np

from gensim.models import word2vec

hostname = "0.0.0.0"
port = 80
vecdir = "vec/"

@route("/calender")
def calender():
    return {"calender": sorted([x.replace(vecdir + "vec_","") for x in glob.glob(vecdir + 'vec_??????????')], reverse=True)}

@route("/article/search", method="GET")
def article_search():
    if any([x not in request.query.keys() for x in ["date","query"]]):
        return {"error": "invalid args"}

    date = request.query.date#[]で取得すると文字化けする
    query = request.query.query

    if not re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
        return {"error": "invalid date"}
    if query == '':
        return {"error": "invalid query"}

    offset = 0
    if "offset" in request.query.keys():
        if not re.match("^[0-9]{1,4}$", request.query.offset):
            return {"error": "invalid offset"}
        offset = int(request.query.offset)

    time = date+"T23:59:59.999999"

    article = []

    dbword = sqlite3.connect("file:words.db", uri=True)
    dbword.row_factory = sqlite3.Row
    dbtext = sqlite3.connect("file:text.db", uri=True)
    dbtext.row_factory = sqlite3.Row

    for r1 in dbword.execute("select * from wordstbl where words match ? and time < ? order by time desc limit 20 offset ?", (query, time, offset)):
        r2 = dbtext.execute("select * from rawtext where id = ?", (r1["id"],)).fetchone()
        if r2 is None:
            r2 = dbtext.execute("select * from rawtext2 where id = ?", (r1["id"],)).fetchone()

        article.append({"date": r2["time"], "text": unicodedata.normalize("NFKC", r2["rawtext"]), "source": r2["source"]})

    dbtext.close()
    dbword.close()
    
    return {"article": article}

@route("/words/count", method="GET")
def words_count():
    if any([x not in request.query.keys() for x in ["date","word","date_comp","diff"]]):
        return {"error": "invalid args"}

    date = request.query.date
    date_comp = request.query.date_comp
    word = request.query.word
    diff = request.query.diff

    if not re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
        return {"error": "invalid date"}
    if not re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date_comp):
        return {"error": "invalid date_comp"}
    
    diff = (diff == "1")
    
    if date_comp < date:
        t1, t2 = date_comp+"T23:59:59.999999", date+"T23:59:59.999999"
    else:
        t1, t2 = date+"T23:59:59.999999", date_comp+"T23:59:59.999999"

    wc = {}
    dbword = sqlite3.connect("file:words.db", uri=True)
    dbword.row_factory = sqlite3.Row
    for row in dbword.execute("select * from wordstbl where words match ? and time < ?", (word, t2)):
        t = row["time"]
        for w in row["words"].split(" "):
            if w == "":
                continue
            if w in wc:
                if t <= t1:
                    wc[w]["count1"] = wc[w]["count1"] + 1
                    wc[w]["count2"] = wc[w]["count2"] + 1
                else:
                    wc[w]["count2"] = wc[w]["count2"] + 1
            else:
                if t <= t1:
                    wc[w] = {"count1":1, "count2":1}
                else:
                    wc[w] = {"count1":0, "count2":1}
    dbword.close()
    if diff:
        wc = sorted(wc.items(), key=lambda x: x[1]["count2"]-x[1]["count1"], reverse=True)[:30]
    else:
        wc = sorted(wc.items(), key=lambda x: x[1]["count2"], reverse=True)[:30]

    return {"wordcount": wc}

@route("/words/vec", method="GET")
def words_vec():
    if any([x not in request.query.keys() for x in ["date","word","date_comp"]]):
        return {"error": "invalid args"}

    date = request.query.date
    words = request.query.word.split(" ")
    date_comp = request.query.date_comp

    if vecdir + "vec_" + date not in glob.glob(vecdir + 'vec_*'):
        return {"error": "invalid date"}
    
    model = word2vec.Word2Vec.load(vecdir + "vec_" + date)
    if any(word not in model.wv.vocab for word in words):
        return {"error": "at least one word is not in the vocabulary"}

    index = 0
    if "index" in request.query.keys():
        if not re.match("^[0-9]{1,2}$", request.query.index):
            return {"error": "invalid index"}
        index = int(request.query.index)

    if vecdir + "vec_" + date_comp not in glob.glob(vecdir + 'vec_*'):
        return {"error": "invalid date"}

    model_comp = word2vec.Word2Vec.load(vecdir + "vec_" + date_comp)
    
    (nodes, links) = generate_nodes_links(words, model, index)
    (nodes_comp, _) = generate_nodes_links(words, model_comp, index)
    
    for n in nodes:
        if n["id"] in [nc["id"] for nc in nodes_comp]:
            n["isnew"] = 0
        else:
            n["isnew"] = 1

    return {"nodes":nodes, "links":links}

def generate_nodes_links(words, model, index):
    nodes = {}
    links = []
    
    wv0 = np.average(np.array([model.wv[x] for x in words]), axis = 0)

    word = "+".join(words)

    nodes[word] = 1

    rank = 15
    
    for w1 in model.wv.most_similar(positive=[wv0], negative=[], topn=index+rank)[index:]:
        if word == w1[0]:
            continue
        else:
            nodes[w1[0]] = 2
            links.append({ "source":word, "target":w1[0], "value": w1[1] })            
            
        for w2 in model.wv.most_similar(positive=[model.wv[w1[0]]], negative=[], topn=index+3)[index:]:
            if w2[0] not in nodes.keys():
                nodes[w2[0]] = 3
                links.append({ "source":w1[0], "target":w2[0], "value": w2[1] })
            elif nodes[w2[0]] == 3:
                links.append({ "source":w1[0], "target":w2[0], "value": w2[1] })

    nodes = [{ "id": k, "group": v } for k, v in sorted(nodes.items(), key=lambda x:x[1])]
    
    return (nodes, links)


def generate_nodes_mesh(words, model, index):
    nodes = {}
    links = []
    
    wv0 = np.average(np.array([model.wv[x] for x in words]), axis = 0)

    word = "+".join(words)

    nodes[word] = 1

    rank = 10
    
    ret_words = model.wv.most_similar(positive=[wv0], negative=[], topn=index+rank)[index:]
    
    for w1 in ret_words:
        if word != w1[0]:
            nodes[w1[0]] = 2

    for i in range(len(ret_words)):
        for j in range(i + 1, len(ret_words)):
            links.append({ "source":ret_words[i][0], "target":ret_words[j][0], "value": model.wv.similarity(ret_words[i][0], ret_words[j][0]) })            

    nodes = [{ "id": k, "group": v } for k, v in sorted(nodes.items(), key=lambda x:x[1])]
    
    return (nodes, links)


@route("/dl/<filename:path>")
def download(filename):
    return static_file(filename, root="dl", download=True)

@route("/")
@route("/<filename:path>")
def root(filename="index.html"):
    return static_file(filename, root="static")

run(host=hostname, port=int(os.environ.get("PORT", port)))
