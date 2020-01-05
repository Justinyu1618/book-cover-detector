import requests
import sys
import base64
from os import listdir
from os.path import isfile, join

ACCESS_TOKEN = "ya29.Il-4B4qmPkJectkjoX9WIhPcmuzPrkGXQXeusTe8uyax5TTsXcZsOLihx8N05nZ1zHNrzRvP_hxlDzCi_skY6-vQJpswV0Nu8PBMUhXmI6siS2_7xKuOOf03RHlbv_D5vw"
TARGET_URL = "https://vision.googleapis.com/v1/images:annotate"


def make_req(image):
    encoded_im = base64.b64encode(image.read())
    data = {"image": {"content": encoded_im.decode('utf-8')},
            "features": [{"type": "TEXT_DETECTION"}]
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
            resp = make_req(imfile)
            print(resp.text)
        else:
            imfiles = [open(join(source, f), "rb") for f in listdir(source) if isfile(join(source, f))]

    else:
        print("read_cover.py <file path>")