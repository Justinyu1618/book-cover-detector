import goodreads_api_client as gr
import datetime
from html.parser import HTMLParser
import os

if os.environ.get("SETTING") == "prod":
    GOODREADS_KEY = os.environ.get("GOODREADS_KEY")
    GOODREADS_SECRETS_KEY = os.environ.get("GOODREADS_SECRETS_KEY")
else:
    from _secrets import *



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
    client = gr.Client(developer_key=GOODREADS_KEY, developer_secret=GOODREADS_SECRETS_KEY)
    book = client.Book.show_by_isbn(isbn)
    keys_wanted = ['title', 'description', 'average_rating', 'num_pages', 'ratings_count', 'text_reviews_count']
    reduced_book = {k:strip_tags(v) for k, v in book.items() if k in keys_wanted}
    return reduced_book

if __name__ == '__main__':
    startTime = datetime.datetime.now()
    isbn ='0575077832'
    get_goodreads_details(isbn)
    print(datetime.datetime.now() - startTime)
