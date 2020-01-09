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


def book_details_amazon(isbn):
    # Amazon Scraping
    amazon_base_url = "https://www.amazon.com/dp/"
    amazon_url = amazon_base_url + isbn
    req = Request(amazon_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')

    # Book title
    a_title = soup.find_all("span",id="productTitle")
    a_title = str(a_title)
    a_title = remove_tags(a_title)
    a_title = a_title.strip("[]")
    a_title = a_title.strip()

    # Book details
    book_info = []
    for li in soup.select('table#productDetailsTable div.content ul li'):
        try:
            title = li.b
            key = title.text.strip().rstrip(':')
            value = title.next_sibling.strip()
            value = value.strip("()")
            book_info.append((key,value))
        except AttributeError:
            break

    # Amazon reviews scraping
    amazon_review_base_url = "https://www.amazon.com/product-reviews/"
    amazon_review_url = amazon_review_base_url + isbn + "/ref=cm_cr_getr_d_paging_btm_2?pageNumber="
    print(amazon_review_url)
    req = Request(amazon_review_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read().decode("utf-8")
    with open("lol.html", "w") as f:
        f.write(page)
    soup = BeautifulSoup(page, 'html.parser')

    all_divids = [tag['id'] for tag in soup.find_all('div') if 'id' in tag]
    print(all_divids)
    txt = soup.find('div', {'id': 'cm_cr-review_list'})
    print(txt)
    

    # List of book reviews in Amazon
    reviews_list = []
    reviews_list_final = []
    
    for pg in range(1):
#         amazon_review_url = amazon_review_base_url + isbn + "/ref=cm_cr_getr_d_paging_btm_2?pageNumber=" + str(pg)
#         req = Request(amazon_review_url, headers={'User-Agent': 'Mozilla/5.0'})
#         page = urlopen(req).read().decode("utf-8")
#         soup = BeautifulSoup(page, 'html.parser')
#         print(soup)
        txt = soup.find("div", id='cm_cr-review_list')

#         txt = soup.find("div", id=re.compile('^cm_cr-review_list'))
        print("txt: ")
        print(len(txt))
        try:
            for rawreview in txt.find_all('span', {'class' : 'a-size-base review-text'}):
                text = rawreview.parent.parent.parent.text
                startindex = text.index('5 stars') + 7
                endindex = text.index('Was this review helpful to you?')
                text = text[startindex:endindex]
                text = text.split("Verified Purchase")[1]
                rText = text.split(".")[:-1]
                review_text = ""
                for i in range(len(rText)):
                    review_text += rText[i]
                    review_text += "."
                if review_text is not "":
                    if "|" not in review_text:
                        reviews_list.append(review_text)
                    else:
                        rText = text.split(".")[:-2]
                        review_text = ""
                        for x in range(len(rText)):
                            review_text += rText[x]
                            review_text += "."
                        reviews_list.append(review_text)
        except AttributeError:
            review_text = "No reviews found."

    print(len(reviews_list))
    if amazon_reviews_count < len(reviews_list):
        reviews_list_final = reviews_list[:amazon_reviews_count]
    else:
        reviews_list_final = reviews_list

    # Printing book details from Amazon
    printmd('**Book Details from Amazon\n**')
    #print("Book Details from Amazon\n")
    print("Book Title: ",a_title)
    #print("\n")
    for i in range(len(book_info)):
        print(f"{book_info[i][0]} : {book_info[i][1]}")
        #print("\n")
    print("\n")
    if len(reviews_list_final) == 0:
        print(review_text)
        print("\n")
    else:
        print(f"Displaying top {amazon_reviews_count} book reviews:\n")
        for i in range(len(reviews_list_final)):
            review_txt_list = reviews_list_final[i].split(".")[:3]
            review_txt = ""
            for j in range(len(review_txt_list)):
                review_txt += review_txt_list[j]
                review_txt += "."
            review_txt += ".."
            print(review_txt)
            print("\n")

if __name__ == '__main__':
    book_details_amazon('0738206369')