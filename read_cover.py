import requests
import sys
import base64
from os import listdir
from os.path import isfile, join
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
                 "maxResults": 10
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





if __name__ == '__main__':
    if len(sys.argv) == 2:
        source = sys.argv[1]
        if "." in source:
            imfile = open(sys.argv[1], "rb")
            resp = image_detection(imfile)
            url = get_amazon_url_from_results(resp)
            ASIN = get_ASIN(url)

        else:
            imfiles = [open(join(source, f), "rb") for f in listdir(source) if isfile(join(source, f))]

    else:
        print("read_cover.py <file path>")

# With this API, you can use RESTful requests to get either web search or image search results in JSON format.
# GET https://www.googleapis.com/customsearch/v1?key=INSERT_YOUR_API_KEY&cx=017576662512468239146:omuauf_lfve&q=lectures


# Price
# https://docs.aws.amazon.com/AWSECommerceService/latest/DG/EX_RetrievingPriceInformation.html
