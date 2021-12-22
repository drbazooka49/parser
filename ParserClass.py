import os
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import time
import re
import json
#TODO: from 500x500 size -- ? not sure
HEADERS = {'User-Agent': "Mozilla/5.0"}
COOKIES = {}

#Main parser class
class Parser:

    # create file for storage if doesn't exist
    def file_exists():
        if not os.path.isfile('/Img_Urls.txt'):
            file = open("/Img_Urls.txt", "w+")
            file.close()
        return

    # write to file
    def write_to_file(self, img):
        with open("/Img_Urls.txt", "a+") as myfile:
            myfile.write(str(img) + '\n')
            myfile.close()
        return

#Child Html Parser class
class Uno(Parser):

    def __init__(self):
        super().__init__()

    def product_img_thumbnails(self, product_soup):
        product_thumbnails_all = product_soup.findAll("a", {"data-fancybox": "gallery"})
        if product_thumbnails_all:
            for thumnbails_img_src in product_thumbnails_all:
                link = thumnbails_img_src["href"]
                self.write_to_file(link)
                print(link)
        else:
            return

    def product_img_link(self, product_url):
        product_page = requests.get(product_url)
        product_page.raise_for_status()
        if product_page:
            product_page_html = product_page.content
            product_soup = BeautifulSoup(product_page_html, "html.parser")
            product_img = product_soup.find("img", {"class": "product-info__image__img"})
            product_img_src = product_img["src"]
            thumbnails = self.product_img_thumbnails(product_soup)
            if not thumbnails:
                print(product_img_src)
                self.write_to_file(product_img_src)
                #print("No thumbnails")
                return
        return

    def search_result(self, url, search_results):
        results = requests.get(search_results)
        results_html = results.content
        results_soup = BeautifulSoup(results_html, "html.parser")
        products = results_soup.findAll("a", {"class": "product__title"})
        if products:
            for product in products:
                next_url = product["href"]
                new_url = str(url) + str(next_url)
                self.product_img_link(new_url)
        return

    #check if search page result exists
    def page_exists(self, page_to_inspect):
        page = requests.get(page_to_inspect)
        return page.raise_for_status()

    #TODO: add exceptions, wrong searches
    def search(self, url):
        page = requests.get(url)
        html = page.content
        soup = BeautifulSoup(html, "html.parser")
        param = "iphone"
        #max 15 search page results
        for i in range(1, 15):
            search = str(url) + "/search/" + param + "?page=" + str(i)
            exist = self.page_exists(search)
            if exist == 404:
                raise Exception("Page doesn't exist")
            else:
                self.search_result(url, search)

#Another child html Parser Class
class Altex(Parser):

    def __init__(self):
        super().__init__()

    # check if search page result exists
    def page_exists(self, page_to_inspect):
        page = requests.get(page_to_inspect)
        return page.raise_for_status()

    #gets cookies from main page session
    def get_cookies(self, session):
        COOKIES = session.cookies.get_dict()

    #gets urls of all product imgs
    def get_imgs_urls(self, url):
        product = requests.get(url, headers=HEADERS, cookies=COOKIES)
        product_soup = BeautifulSoup(product.content, 'lxml')
        imgs_urls = []
        temp_link = ''
        product_imgs = product_soup.findAll('img')
        for img_link in product_imgs:
            if re.search('/media/', str(img_link['src'])) and re.search('/product/', str(img_link['src'])):
                img_link['src'] = re.sub('/resize', '', str(img_link['src']))
                # TODO add if there are different patterns for naming places of original images
                # also error messages
                pattern = re.compile('/[^0-9]/[^0-9]/')
                result = pattern.search(str(img_link['src']))
                img_link['src'] = re.sub('/[^0-9]/[^0-9]/.*?/', str(result.group(0)), str(img_link['src']))
                #to avoid identical links
                if temp_link != img_link['src']:
                    print(img_link['src'])
                    temp_link = img_link['src']
                    imgs_urls.append(img_link['src'])

    # get all products from a subcategory -- only first 24
    def get_products(self):
        subcategory_url = 'https://altex.ro/telefoane/cpl/'
        subcategory = requests.get(subcategory_url, headers=HEADERS, cookies=COOKIES)
        subcategory_soup = BeautifulSoup(subcategory.content, 'html.parser')
        products_urls = []
        products_links = subcategory_soup.findAll("a", href=True)
        for product_link in products_links:
            if re.search('/cpd/', str(product_link['href'])):
                products_urls.append(product_link['href'])
        for product_url in products_urls:
            self.get_imgs_urls(product_url)

    # TODO get subcategories
    def get_subcategories(self):
        category = requests.get(category_url, headers=HEADERS, cookies=COOKIES)
        category_soup = BeautifulSoup(category.content, 'lxml')
        subcategories_urls = []
        subcategories = category_soup.findAll() # if no /cpd/ links means no products, then subcategory -- гений :3

        pass

    #get all categories on this website
    def get_categories(self, url):
        session = requests.get(url, headers=HEADERS)
        self.get_cookies(session)
        soup = BeautifulSoup(session.content, 'lxml')
        #print(soup.prettify())
        categories_url = []
        categories = soup.findAll('a', href=True)
        for link in categories:
            if re.search('^https', str(link['href'])) and re.search('/cpl/$', str(link['href'])):
                categories_url.append(link['href'])
                print(link['href'])
        for link in categories_url:
            pass


if __name__ == '__main__':
    uno = "https://uno.md"
    altex = "https://altex.ro"
    powerplanet = "https://www.powerplanetonline.com/en/"
    #object = Uno()
    #object.search(uno)
    obj = Altex()
    obj.get_categories(altex)