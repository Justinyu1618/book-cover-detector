import requests
import sys
import base64
from os import listdir
from os.path import isfile, join
import re
import json
import ast
import datetime
from _secrets import *

GOOGLE_TARGET_URL = "https://vision.googleapis.com/v1/images:annotate"


def text_detection(image):
    encoded_im = base64.b64encode(image.read())
    data = {"image": {"content": encoded_im.decode('utf-8')},
            "features": [{"type": "TEXT_DETECTION"}]
            }
    payload = {"requests": [data]}
    auth = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    resp = requests.post(GOOGLE_TARGET_URL, json=payload, headers=auth)
    resp.raise_for_status()
    return resp


def image_detection(image):
    encoded_im = base64.b64encode(image.read())
    data = {"image": {"content": encoded_im.decode('utf-8')},
            "features": [
                {"type": "WEB_DETECTION",
                 "maxResults": 100000
                }
                ]
            }
    payload = {"requests": [data]}
    auth = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    resp = requests.post(GOOGLE_TARGET_URL, json=payload, headers=auth)
    resp.raise_for_status()
    return resp


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

    request_signature =
        Algorithm + "\n" +
        RequestDateTime + "\n" +
        CredentialScope + "\n" +
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
    if type(resp) is not dict:
        resp = resp.json()
    try:
        if "pagesWithMatchingImages" in resp["responses"][0]["webDetection"]:
            pages = resp["responses"][0]["webDetection"]["pagesWithMatchingImages"]
            matches = [p["url"] for p in pages if "url" in p]
            amazon_links = [m for m in matches if "https://www.amazon.com" in m]
        return amazon_links
    except Exception as e:
        print(f"FAILED!: {e}")
        return None


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        try:
            count_all = 0
            count_im = 0
            count_am = 0
            with open("results.txt", "a"):
                for source in sys.argv[1:]:
                    print(f"\nScraping {source}")
                    imfile = open(source, "rb")
                    resp = image_detection(imfile)
                    matches = find_amazon(resp)
                    if not matches:
                        print("No Amazon Links!")
                        count_fail += 1
                    else:
                        print("Amazon product matches!")
                        print(matches)
                        count_am += 1
                    count_all += 1
        except KeyboardInterrupt:
            print("\n\n")
            pass
        print(f"{count_im}/{count_all} images found")
        print(f"{count_am}/{count_all} amazon pages found")
    else:
        print("read_cover.py <file path>")

# With this API, you can use RESTful requests to get either web search or image search results in JSON format.
# GET https://www.googleapis.com/customsearch/v1?key=INSERT_YOUR_API_KEY&cx=017576662512468239146:omuauf_lfve&q=lectures


# Price
# https://docs.aws.amazon.com/AWSECommerceService/latest/DG/EX_RetrievingPriceInformation.html
