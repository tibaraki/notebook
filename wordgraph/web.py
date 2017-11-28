import os
import glob
import json
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

@route("/words", method="GET")
def words():
    if any([x not in request.query.keys() for x in ["date","word"]]):
        return res_json({"error": "invalid args"})

    date = request.query.date #[]で取得すると文字化けする
    word = request.query.word
    if vecdir + "vec_" + date not in glob.glob(vecdir + 'vec_*'):
        return res_json({"error": "invalid date"})
    
    model = word2vec.Word2Vec.load(vecdir + "vec_" + date)
    if word not in model.wv.vocab:
        return res_json({"error": "'" + word + "' is not exists in vocabulary"})
    
    nodes = []
    links = []

    nodes.append({ "id":word, "group":"1" })

    for w1 in model.most_similar(positive=[word], negative=[], topn=25)[15:]:
        if w1[0] not in {x["id"] for x in nodes}:
            nodes.append({ "id":w1[0], "group":"2" })
        links.append({ "source":word, "target":w1[0], "value": w1[1] })
        for w2 in model.most_similar(positive=[w1[0]], negative=[], topn=10)[5:]:
            if w2[0] not in {x["id"] for x in nodes}:
                nodes.append({ "id":w2[0], "group":"3" })
            links.append({ "source":w1[0], "target":w2[0], "value": w2[1] })

    return res_json({ "nodes":nodes, "links":links })

@route("/")
@route("/<filename:path>")
def root(filename="index.html"):
    return static_file(filename, root="static")

run(host=hostname, port=int(os.environ.get("PORT", port)))

