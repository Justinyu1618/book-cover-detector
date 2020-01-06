import sys, os
from read_cover import make_req
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from pprint import pprint

nlp = en_core_web_sm.load()

def parse_resp(resp):
    text = resp["responses"][0]["textAnnotations"][0]["description"]
    text = text.split("\n")
    return text


def extract_book(resp):
    text = parse_resp(resp)
    docs = [nlp(t) for t in text]
    pprint(docs)
    pprint([[(x.text, x.label_) for x in d.ents] for d in docs])


if __name__ == '__main__':
    if len(sys.argv) == 2:
        source = sys.argv[1]
        imfile = open(sys.argv[1], "rb")
        resp = make_req(imfile)
        extract_book(resp.json())
    else:
        print("read_cover.py <file path>")