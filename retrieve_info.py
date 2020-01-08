
from goodreads_data import get_goodreads_details
import datetime

def retrieve_info(isbn):
    """
    Takes in ISBN number, spits out a dict of all the data
    about the book
    """
    response_dict = get_goodreads_details(isbn)
    return response_dict

if __name__ == '__main__':
  startTime = datetime.datetime.now()
  print(retrieve_info("0393355624"))
  print(datetime.datetime.now() - startTime)
