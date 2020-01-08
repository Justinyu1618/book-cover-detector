
from goodreads import get_goodreads_details
import datetime

def retrieve_info(isbn):
    """
    Takes in ISBN number, spits out a dict of all the data
    about the book
    """
    book_title, authors, average_rating, \
                num_ratings, pg_count, \
                    actual_reviews, description = get_goodreads_details(isbn)

    response_dict = {
      "Book_Title": book_title,
      "Authors": authors,
      "Average_rating": average_rating,
      "Num_ratings": num_ratings,
      "pg_count": pg_count,
      "actual_reviews": actual_reviews,
      "description": description
    }

    return response_dict

if __name__ == '__main__':
  startTime = datetime.datetime.now()
  print(retrieve_info("0393355624"))
  print(datetime.datetime.now() - startTime)
