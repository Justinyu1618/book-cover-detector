import requests
import csv
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re, time, html
# from IPython.display import Markdown, display

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

# def printmd(string):
#     display(Markdown(string))

# from html.parser import HTMLParser

# class MLStripper(HTMLParser):
#     def __init__(self):
#         self.reset()
#         self.strict = False
#         self.convert_charrefs= True
#         self.fed = []
#     def handle_data(self, d):
#         self.fed.append(d)
#     def get_data(self):
#         return ''.join(self.fed)


# def strip_tags(html):
#     s = MLStripper()
#     s.feed(html)
#     return s.get_data()

def clean_text(text):
    text = html.unescape(text)
    text = text.replace("<br />", "\n")
    return text 

def get_amazon_details(isbn):

    # Regex patterns
    re_price = re.compile(r'product-price-line">.*?(\$[0-9\.]*)')
    re_price2 = re.compile(r'offer-price [^>]*?>.*?(\$[0-9\.]*)')

    #re.S --> re.DOTALL flag, makes "." match newlines as well
    # Matching Group Order: icon_link, name, rating, title, date, description
    re_reviews = re.compile(r'id="customer_review-.*?class="a-profile".*?class="a-profile-avatar".*?data-src="(.*?)".*?class="a-profile-name".*?>(.*?)</span>.*?title="([0-9\.]*?) out of.*?data-hook="review-title".*?<span.*?>(.*?)</span>.*?data-hook="review-date".*?>.*?on (.*?)</span>.*?data-hook="review-body".*?review-text-content.*?>.*?<span.*?>(.*?)</span>', flags=re.S)

    # Amazon Scraping
    amazon_base_url = "https://www.amazon.com/dp/"
    amazon_url = amazon_base_url + isbn
    req = Request(amazon_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read().decode("utf-8")

    price = re_price.search(page)
    if price is None: price = re_price2.search(page)
    if price is not None: price = price.group(1)

    review_groups = re_reviews.findall(page)
    props = ["profile_img", "name", "rating", "title", "date", "description"]

    reviews = [{prop:clean_text(value) for prop, value in zip(props, entry)} for entry in review_groups]
    
    return price, reviews




if __name__ == '__main__':
    get_amazon_data('0738206369')