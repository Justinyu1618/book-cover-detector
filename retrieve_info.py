
from goodreads_data import get_goodreads_details
from amazon_data import get_amazon_details
import datetime

def retrieve_primary_info(isbn):
    """
    Takes in ISBN number, spits out a dict of all the data
    about the book
    """
    response_dict = get_goodreads_details(isbn)
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
