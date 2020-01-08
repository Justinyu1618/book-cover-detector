import requests
import sys
import base64
import os
from os import listdir
from os.path import isfile, join
import re
import json
import ast
import datetime

if os.environ.get("SETTING") == "prod":
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
else:
    from _secrets import *

from goodreads_data import get_goodreads_details
from pprint import pprint
from urllib import parse
from googlesearch import search
import time
# import spacy
# from spacy import displacy
# import en_core_web_sm
# nlp = spacy.load('xx_ent_wiki_sm')

import nltk
nltk.download("names")
nltk.download("stopwords")
# from nltk.tag.stanford import StanfordNERTagger
from bs4 import BeautifulSoup

# classifier_path = 'stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz'
# jar_path = 'stanford-ner-2018-10-16/stanford-ner.jar'
# STANF = StanfordNERTagger(classifier_path, jar_path)

GOOGLE_CLOUD_URL = "https://vision.googleapis.com/v1/images:annotate"
OPEN_LIB_URL = 'http://openlibrary.org/api/books?bibkeys=ISBN:%s&format=json&jscmd=data'
GOOGLE_SEARCH_URL = "https://www.google.com/search?q=%s"

NAMES_CORPUS = set([w.lower() for w in nltk.corpus.names.words()])
STOP_WORDS = set(nltk.corpus.stopwords.words("english"))

BLACKLIST_WORDS = set(["bestseller", "the new yorker", "publish","introduction by", "-the"])
# ======== Helper Functions ========

def valid_ISBN(code):
    code = code.lower()
    if len(code) == 10 and code[:-1].isdigit() and (code[-1].isdigit() or code[-1] == 'x'):
        total = sum([(10-i)*int(code[i]) for i in range(9)])
        last_dig = 10 if code[-1] == 'x' else code[-1]
        return (total + int(last_dig)) % 11 == 0
    return False 


def has_blacklisted(text):
    for word in BLACKLIST_WORDS:
        if word in text: return True
    return False

# ======== API Functions ========

def text_detection(image):
    encoded_im = base64.b64encode(image.read())
    data = {"image": {"content": encoded_im.decode('utf-8')},
            "features": [{"type": "TEXT_DETECTION"}]
            }
    payload = {"requests": [data]}
    auth = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    resp = requests.post(GOOGLE_CLOUD_URL, json=payload, headers=auth)
    resp.raise_for_status()
    return resp


def image_detection(encoded_im):
    data = {"image": {"content": encoded_im},
            "features": [
                # {"type": "WEB_DETECTION",
                # "maxResults": 100000
                # },
                {"type": "TEXT_DETECTION",
                }
                ]
            }
    payload = {"requests": [data]}
    auth = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    resp = requests.post(GOOGLE_CLOUD_URL, json=payload, headers=auth)
    resp.raise_for_status()
    return resp.json()


def get_book_info(ISBN):
    resp = requests.get(OPEN_LIB_URL % ISBN)
    return resp.json()

def clean_google_query(query):
    query = [q for q in query if not has_blacklisted(q)]
    final = []
    for q in query:
        if "\"" in q:# and len(re.search(r'".*?"', q).group(0)) > 2:
            continue
        final.append(q)
    return final


def perform_google_search(query):
    query = clean_google_query(query)
    print(query)
    query = " ".join(query) + " Amazon Books"
    
    resp = search(query, tld="com", stop=5)
    return resp

# ======== Parsing ========

def parse_google_search(resp):
    pattern = re.compile(r'https://www\.amazon\..*?/dp/([0-9xX]{10})')
    # soup = BeautifulSoup(resp, 'html.parser')
    # links = [link.get("href") for link in soup.find_all('a')]
    # matches = []
    # for link in links:
    #     print(link)
    #     search = pattern.search(link)
    #     if search: matches.append(search)
    # return matches
    matches = []
    for link in resp:
        match = pattern.findall(link)
        if match:
            matches.append((match[0], str(link)))
    return matches


def get_amazon_url_from_results(response):
    """
    Parses first amazon url
    """
    response_dict = ast.literal_eval(resp.text)
    for page in response_dict["responses"][0]["webDetection"]["pagesWithMatchingImages"]:
        page_url = page['url']
        if "amazon" in page_url:
            return page_url

    #TODO: this currently returns no url if no amazon result, need to figure out how to handle edge cases
    return


def get_ASIN(url):
    """
    Parses ASIN from url
    """
    first_index = url.rfind("/")
    ASIN = url[first_index + 1:]
    print(ASIN)
    return ASIN


def get_price_with_ASIN(id):
    """
    Take ASIN and return JSON prices
    """
    Algorithm = "AWS4-HMAC-SHA256"

    date = datetime.datetime.now().replace(microsecond=0).isoformat()
    RequestDateTime = re.sub(r'\W+', '', date) + "Z"

    request_signature = Algorithm + "\n" + \
        RequestDateTime + "\n" + \
        CredentialScope + "\n" + \
        HashedCanonicalRequest

    data = {"Service": "AWSECommerceService",
            "Operation": "ItemLookup",
            "ResponseGroup": "Offers",
            "IdType": "ASIN",
            "ItemId": id,
            "AssociateTag": AMAZON_AFFILIATE_ID,
            "AWSAccessKeyId": AWS_ACCESS_KEY,
            }
    payload = {"requests": [data]}
    auth = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    resp = requests.post(AMAZON_TARGET_URL, json=payload, headers=auth)
    resp.raise_for_status()
    return resp


def find_image_links(resp):
    if type(resp) is not dict:
        resp = resp.json()
    try:
        objs = []
        for val in resp["responses"][0]["webDetection"].values():
            objs.extend(val)
        matches = [u["url"] for u in objs if "url" in u and "amazon.com" in u["url"]]
        amazon_links = [m for m in matches if "https://www.amazon.com" in m]
        return (matches, amazon_links)
    except Exception as e:
        print(f"FAILED!: {e}")
        print(resp["responses"][0]["webDetection"])
        return None

def find_amazon(resp):
    amazon_links = None
    if "pagesWithMatchingImages" in resp["responses"][0]["webDetection"]:
        pages = resp["responses"][0]["webDetection"]["pagesWithMatchingImages"]
        matches = [p["url"] for p in pages if "url" in p]
        amazon_links = [m for m in matches if "https://www.amazon.com" in m]
    return amazon_links

def get_labels(resp):
    matches = None
    if "bestGuessLabels" in resp["responses"][0]["webDetection"]:
        labels = resp["responses"][0]["webDetection"]["bestGuessLabels"]
        matches = [l["label"] for l in labels if "label" in l]
    return matches

def get_text(resp):
    final_text = None
    if "textAnnotations" in resp["responses"][0]:
        raw_text = resp["responses"][0]["textAnnotations"][0]["description"]
        final_text = raw_text.lower().strip().split("\n")
    return final_text

def extract_author_STANF(text):
    final = []
    for sent in text:
        tokens = nltk.tokenize.word_tokenize(sent)
        tags = STANF.tag(tokens)
        final.append(tags)
    return final

def extract_author(text):
    final = []
    if not text: return None
    for segment in text:
        words = segment.split(" ")
        if len(words) <= 3:
            words = [w for w in words if w not in STOP_WORDS]
            if any([w in NAMES_CORPUS for w in words]):
                final.append(segment)
    return final


def get_data(imfile):
    """
    This takes an encoded image and returns data about the image.
    """
    resp = image_detection(imfile)
    url = get_amazon_url_from_results(resp)
    ASIN = get_ASIN(url)
    return get_goodreads_details(ASIN)


def read_cover(image, isfile=False):
    """ 
    Takes in Image, identifies the book and spits out ISBN number
    """
    if isfile:
        image = open(image, "rb")
        image = base64.b64encode(image.read()).decode("utf-8")
    resp = image_detection(image)
    text = get_text(resp)
    if not text:
        return None
    resp = perform_google_search(text)
    isbns = parse_google_search(resp)
    if isbns:
        final = isbns[0] # (isbn, amazon_link)
        print(f"ISBN FOUND: {final}")
        # print(f"INFO: {get_book_info(final)}")
        return final
    else:
        return None


def extract_info_openlib(resp):
    books = resp.values()
    ret = []
    for book in books:
        entry = {"title": book["title"],
                "author": book["authors"][0]["name"]}
        ret.append(entry)
    return ret

# ======== TESTS ========


def test_results(*args):
    if len(args) >= 2:
        count_all, count_am, count_label, count_text = 0, 0, 0, 0
        try: 
            for source in args[1:]:
                print(f"\nScraping {source}")
                imfile = open(source, "rb")
                resp = image_detection(imfile)
                am_links = find_amazon(resp)
                labels = get_labels(resp)
                text = get_text(resp)
                tags = extract_author(text)
                with open("results.txt", "a") as file:
                    file.write(f"Source: {source}\nAmazon: {am_links}\nLabel: {labels}\nText: {text}\nNames: {tags}\n\n\n")
                count_am += am_links is not None and len(am_links) > 0
                count_label += labels is not None
                count_text += text is not None
                count_all += 1
        except KeyboardInterrupt as e:
            pass
        print(count_all, count_am, count_label)
    else:
        print("read_cover.py <file path>")


def test_amazon(*args):
    if len(args) >= 2:
        count_all, count_fail = 0, 0
        try: 
            for source in args[1:]:
                print(f"\nScraping {source}")
                isbns = read_cover(source, isfile=True)
                if isbns is None:
                    count_fail += 1
                else:
                    final_str = ""
                    for isbn in isbns:
                        book_info = get_book_info(isbn)
                        final_str += f"{isbn}: {extract_info_openlib(book_info)}\n"
                    with open("test2_results.txt", "a") as file:
                        file.write(f"Source: {source}\nResult:{final_str}\n\n\n")
                count_all += 1
        except KeyboardInterrupt as e:
            pass
        print(count_all, count_fail)
    else:
        print("read_cover.py <file path>")

def test_google(*args):
    if len(args) >= 2:
        count_all, count_google = 0, 0
        try: 
            for source in args[1:]:
                start = time.time()
                count_all += 1
                print(f"\nScraping {source}")
                imfile = open(source, "rb")
                resp = image_detection(imfile)
                # am_links = find_amazon(resp)
                # labels = get_labels(resp)
                text = get_text(resp)
                # tags = extract_author(text)
                if not text:
                    continue
                print(time.time() - start)
                mid = time.time()
                resp = perform_google_search(text)
                isbns = parse_google_search(resp)
                print(time.time() - mid)
                if isbns:
                    later = time.time()
                    final_str = ""
                    for isbn in isbns:
                        book_info = get_book_info(isbn)
                        final_str += f"{isbn}: {extract_info_openlib(book_info)}"
                    print(time.time() - later)
                    with open("results.txt", "a") as file:
                        file.write(f"Source: {source}\nGoogle ISBNS: {final_str}\nTime:{time.time() - start}\n\n")
                    count_google += 1
                else:
                    with open("results.txt", "a") as file:
                        file.write(f"Source: {source}\n FAILED\nTime:{time.time() - start}\n\n")
                
        except KeyboardInterrupt as e:
            pass
        print(count_all, count_google)
    else:
        print("read_cover.py <file path>")


if __name__ == '__main__':
    # test_results(*sys.argv)
    # test_amazon(*sys.argv)
    test_google(*sys.argv)

    

# With this API, you can use RESTful requests to get either web search or image search results in JSON format.
# GET https://www.googleapis.com/customsearch/v1?key=INSERT_YOUR_API_KEY&cx=017576662512468239146:omuauf_lfve&q=lectures


# Price
# https://docs.aws.amazon.com/AWSECommerceService/latest/DG/EX_RetrievingPriceInformation.html
