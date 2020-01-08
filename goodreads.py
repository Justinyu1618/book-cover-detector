import requests
import csv
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
# from IPython.display import Markdown, display

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

# def printmd(string):
#     display(Markdown(string))

from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def get_goodreads_details(isbn):
    """
    param: isbn
    returns: book_title, authors, average_rating, num_ratings, pg_count, actual_reviews, description
    """
    amazon_base_url = "https://www.amazon.com/dp/"
    amazon_url = amazon_base_url + isbn
    req = Request(amazon_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')

    a_title = soup.find_all("span",id="productTitle")
    a_title = str(a_title)
    a_title = remove_tags(a_title)
    a_title = a_title.strip("[]")
    a_title = a_title.strip()
    a_title_list = a_title.split(" ")

    # Goodreads Scraping
    goodreads_base_url = "https://www.goodreads.com/book/isbn/"
    goodreads_url = goodreads_base_url + isbn
    req = Request(goodreads_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')

    # Book Title
    book_name = soup.find(itemprop="name")
    book_name = str(book_name)
    book_name = remove_tags(book_name)
    book_name = book_name.strip()
    book_name_list = book_name.split(" ")

    # Verifying if isbn is present in Goodreads by comparing book titles from Goodreads & Amazon
#     if str(a_title_list[0]).lower() != str(book_name_list[0]).lower():
#         return print("Book not found in Goodreads")

    # Author Names
    author_names = soup.find_all("span",itemprop="name")
    author_names = str(author_names)
    author_names = author_names.split(",")
    author_name = author_names[0]
    author_name = author_name.split(">")[1].split("<")[0]
    for i in range(len(author_names)):
        author_names[i] = author_names[i].split(">")[1].split("<")[0]

    author_names_text = ""
    for i in range(len(author_names)):
        author_names_text += str(author_names[i])
        author_names_text += ", "

    # Number of Ratings
    rating_count = soup.find(itemprop="ratingCount")
    rating_count = str(rating_count)
    rating_count = rating_count.split('"')[1]

    # Average Rating
    rating_val = soup.find(itemprop="ratingValue")
    rating_val = str(rating_val)
    rating_val = remove_tags(rating_val)

    # Number of pages in book
    pg_count = soup.find("meta",  property="books:page_count")
    pg_count = str(pg_count)
    pg_count = pg_count.split('"')[1]

    # Book Description
    desc = soup.find("div", id="description")
    if desc is not None:
        desc = desc.find_all("span",style="display:none")
        if desc is not None:
            desc = str(desc)
            desc = remove_tags(desc)
            description = desc.strip("[]")
            description = description.strip()
        else:
            description = "No description found"
    else:
        description = "No description found"


    # Reviews
    review_block = soup.find('div', {'id': 'reviews'})
    reviews = review_block.find_all('span', {'id': re.compile('^freeTextContainer')})
    actual_reviews = reviews[0].text

    # for i in range(0, 5):
    #     review = reviews[i]
    #     review = strip_tags(str(review))
    #     end_index = review.rfind(".")
    #     review = review[:end_index + 1]
    #     actual_reviews.append(review)

    # # Friend reviews
    # review_block = soup.find('div', {'id': 'reviews'})
    # reviews = review_block.find_all('span', {'id': re.compile('^freeTextContainer')})
    # actual_reviews = []
    # for review in reviews:
    #     review = strip_tags(str(review))
    #     end_index = review.rfind(".")
    #     review = review[:end_index + 1]
    #     actual_reviews.append(review)

    # Printing book details from Goodreads
    # printmd('**Book Details from Goodreads\n**')
    # #print("Book Details from Goodreads\n")
    # print("Book Title: ",book_name.splitlines()[0])
    # #print("\n")
    # print("Authors: ",author_names_text)
    # #print("\n")
    # print("Average Rating: ",rating_val)
    # #print("\n")
    # print("Number of ratings: ",rating_count)
    # #print("\n")
    # print("Number of pages in book: ",pg_count)
    # print("\n")
    # print("Book Description:")
    # print("\n")
    # print(description)
    # print("Book Reviews:")
    # print(actual_reviews)
    book_title = book_name.splitlines()[0]
    authors = author_names_text
    average_rating = rating_val
    num_ratings = rating_count

    return book_title, authors, \
      average_rating, num_ratings, pg_count, \
      actual_reviews, description



