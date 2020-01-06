import csv
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import wget

driver = webdriver.Chrome()
BASE_URL = "http://bookcoverarchive.com/page/%s/"
page_num = 0


if len(sys.argv) == 2:
    TARGET_DIR = sys.argv[1]
else:
    print("download_covers.py <target_folder>")

def process_url(string):
    ret = string.replace("url(\"","")
    ret = ret.replace("\")", "")
    return ret 

def process_title(string):
    return string.strip().lower().replace(" ","_").replace("/","_") + ".jpg"

while(True):
    page_num += 1
    page_url = BASE_URL % str(page_num)
    driver.get(page_url)
    print(f"\nSCRAPING {page_url}\n\n")
    elems = driver.find_elements_by_tag_name('a')
    covers = [e for e in elems if "book_" in e.get_property("id")]
    image_urls = [(c.get_property("title"), process_url(c.value_of_css_property("background-image"))) for c in covers]
    for title, url in image_urls:
        filename = wget.download(url, out=TARGET_DIR+f"/{process_title(title)}")
        print(filename)
    # except Exception as e:
    #     print(e)
    #     print(f"{page_url} DOESN'T EXIST! Finished scraping")
    #     break
