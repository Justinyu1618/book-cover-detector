"""
This file uses the https://pypi.org/project/python-amazon-product-api/.
I downloaded the source files, and ran setup.py install myself after using 2to3 to convert all the python files to python3.
"""

from amazonproduct import API
import datetime
import lxml

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

api = API(locale='us')

def get_amazon_affiliate_link(isbn):
  print(isbn)
  result = api.item_lookup(isbn, IdType='ISBN', SearchIndex='Books')
  affiliate_url = result.Items.Item.DetailPageURL
  title = strip_tags(result.Items.Item.ItemAttributes.Title)
  author = result.Items.Item.ItemAttributes.Author
  return str(author), str(title), str(affiliate_url)

def get_book_reviews_price(isbn):
  # get all books from result set and
  # print author and title

  # Example single item lookup
 
  # Returns a link to an iframe
  reviews = api.item_lookup(isbn, ResponseGroup='Reviews', TruncateReviewsAt=1024, IncludeReviewsSummary=True)
  iframe_url = reviews.Items.Item.CustomerReviews.IFrameURL

  # Returns the price summary
  offers = api.item_lookup(isbn, ResponseGroup='OfferSummary')
  lowest_new_price = offers.Items.Item.OfferSummary.LowestNewPrice.FormattedPrice
  lowest_used_price = offers.Items.Item.OfferSummary.LowestUsedPrice.FormattedPrice

  offer_summary = {
    "lowest_new_price" : lowest_new_price,
    "lowest_used_price" : lowest_used_price
  }

  return  iframe_url, offer_summary

if __name__ == '__main__':
  # for book in api.item_search("Books", Publisher="Galileo Press"):
  #   print('%s: "%s"' % (book.ItemAttributes.Author,
  #                       book.ItemAttributes.Title))
  startTime = datetime.datetime.now()
  print(get_book_info("0393355624"))
  print(datetime.datetime.now() - startTime)
