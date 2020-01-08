import requests

def get_goodreads_details(isbn):
    """
    param: isbn
    returns: book_title, authors, average_rating, num_ratings, pg_count, actual_reviews, description
    """
