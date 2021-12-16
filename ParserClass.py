import os
import requests
from bs4 import BeautifulSoup

#TODO: from 500x500 size

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
class Html(Parser):

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

??
class Html2(Parser):

    def __init__(self):
        super().__init__()

    def search(self, url):
        page = requests.get_data(url)
        self._content = bytes().join(self.iter_content(10240))
        response_data = s.post(url=url, data=data, stream=True, verify=False).raw.read()
        print(response_data)
        #headers = page.requests.headers()
        #html = page.content
        #soup = BeautifulSoup(html, "html.parser")
        #print(soup.prettify())



if __name__ == '__main__':
    #Url = "https://uno.md"
    Url = "https://www.powerplanetonline.com/en/"
    #object = Html()
    #object.search(Url)
    obj = Html2()
    obj.search(Url)