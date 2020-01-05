import requests
import sys
import base64
from os import listdir
from os.path import isfile, join

from _secrets import *

TARGET_URL = "https://vision.googleapis.com/v1/images:annotate"


def text_detection(image):
    encoded_im = base64.b64encode(image.read())
    data = {"image": {"content": encoded_im.decode('utf-8')},
            "features": [{"type": "TEXT_DETECTION"}]
            }
    payload = {"requests": [data]}
    auth = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    resp = requests.post(TARGET_URL, json=payload, headers=auth)
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

    resp = requests.post(TARGET_URL, json=payload, headers=auth)
    resp.raise_for_status()
    return resp

if __name__ == '__main__':
    if len(sys.argv) == 2:
        source = sys.argv[1]
        if "." in source:
            imfile = open(sys.argv[1], "rb")
            resp = image_detection(imfile)
            # print(resp.text)
            # print(type(resp))
            # print(resp.text)
            # print(dir(resp))
            # print(resp.text)
            if "https://www.amazon" in resp.text:
                print("Amazon link exists in text body")

        else:
            imfiles = [open(join(source, f), "rb") for f in listdir(source) if isfile(join(source, f))]

    else:
        print("read_cover.py <file path>")

# With this API, you can use RESTful requests to get either web search or image search results in JSON format.
# GET https://www.googleapis.com/customsearch/v1?key=INSERT_YOUR_API_KEY&cx=017576662512468239146:omuauf_lfve&q=lectures


# Price
# https://docs.aws.amazon.com/AWSECommerceService/latest/DG/EX_RetrievingPriceInformation.html
