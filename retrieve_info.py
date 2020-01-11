
from amazon_api2 import get_book_info
from goodreads_data import get_goodreads_details
from amazon_data import get_amazon_details
import datetime

def retrieve_primary_info(isbn):
    """
    Takes in ISBN number, spits out a dict of all the data
    about the book
    """

    # Get info with isbn
    author, title, iframe_url, offer_summary, affiliate_url = get_book_info(isbn)
    reduced_book = get_goodreads_details(isbn)


    response_dict = {
      "Title": title,
      "Prices": offer_summary,
      "Affiliate_url": affiliate_url,
      "Iframe_url": iframe_url,
      "Author": author,
      "Average_rating": reduced_book['average_rating'],
      "Num_pages": reduced_book['num_pages'],
      "Ratings_count": reduced_book['ratings_count']
    }

    return response_dict

def retrieve_secondary_info(isbn):
    """
    Takes in ISBN number, spits out a dict of all the data
    about the book
    """
    response_dict = {"price":None, "reviews":[]}
    price, reviews = get_amazon_details(isbn)
    if price: response_dict["price"] = price
    if reviews: response_dict["reviews"] = reviews
    return response_dict

if __name__ == '__main__':
  startTime = datetime.datetime.now()
  print(retrieve_primary_info("0393355624"))
  print(datetime.datetime.now() - startTime)
