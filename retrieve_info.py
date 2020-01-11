
from amazon_api2 import get_amazon_affiliate_link, get_book_reviews_price
from goodreads_data import get_goodreads_details
from amazon_data import get_amazon_details
import datetime

def retrieve_primary_info(isbn):
    """
    Takes in ISBN number, spits out a dict of all the data
    about the book
    """

    # Get info with isbn
    reduced_book = get_goodreads_details(isbn)
    author, title, affiliate_url = get_amazon_affiliate_link(isbn)

    response_dict = {
      "title": title,
      "affiliate_url": affiliate_url,
      "author": author,
      "average_rating": reduced_book['average_rating'],
      "num_pages": reduced_book['num_pages'],
      "ratings_count": reduced_book['ratings_count']
    }

    return response_dict

def retrieve_secondary_info(isbn):
    """
    Takes in ISBN number, spits out a dict of all the data
    about the book
    """
    iframe_url, offer_summary = get_book_reviews_price(isbn)
    print(iframe_url, offer_summary)

    response_dict = {"price":None, "reviews":[]}
    price, reviews = get_amazon_details(isbn)
    if price: response_dict["price"] = price
    if reviews: response_dict["reviews"] = reviews
    return response_dict

if __name__ == '__main__':
  startTime = datetime.datetime.now()
  print(retrieve_primary_info("0393355624"))
  print(datetime.datetime.now() - startTime)
