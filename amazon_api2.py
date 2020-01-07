"""
This file uses the https://pypi.org/project/python-amazon-product-api/.
I downloaded the source files, and ran setup.py install myself after using 2to3 to convert all the python files to python3.
"""

from amazonproduct import API
api = API(locale='us')

def main():
  # get all books from result set and
  # print author and title
  for book in api.item_search("Books", Publisher="Galileo Press"):
      print('%s: "%s"' % (book.ItemAttributes.Author,
                          book.ItemAttributes.Title))

if __name__ == '__main__':
  main()
