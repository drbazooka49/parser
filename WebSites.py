import re
import time
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

#input your browser header
HEADERS = {'User-Agent': "Mozilla/5.0"}

#main parent class
class Parser:

    def __init__(self):
        pass

    #get page content
    async def get_page(self, session, url):
        async with session.get(url) as r:
            return await r.text()

    #create all tasks for getting page contents
    async def get_all(self, session, urls):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.get_page(session, url))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

    #start main session
    async def main(self, urls):
        async with aiohttp.ClientSession() as session:
            data = await self.get_all(session, urls)
            return data

class Uno(Parser):

    def __init__(self):
        super().__init__()

    #get dict with names and images
    def product_img_link(self, names, products):
        imgs_dict = {}
        for name, product in zip(names, products):
            images = []
            product_soup = BeautifulSoup(product, "lxml")
            product_img = product_soup.find("img", {"class": "product-info__image__img"})
            product_thumbs = product_soup.find_all("a", {"data-fancybox": "gallery"})
            if product_img:
                images.append(product_img["src"])
            for thumb in product_thumbs:
                images.append(thumb['href'])
            if len(images) > 1 and product_img:
                images.pop(0)
            #key - name , data - list of links
            imgs_dict[name] = images

        return imgs_dict

    #parse main result page
    def search_result(self, param):
        url = "https://uno.md"
        search_results = str(url) + "/search/" + param + "?page=1"
        results = requests.get(search_results, headers=HEADERS)
        results_html = results.content
        results_soup = BeautifulSoup(results_html, 'lxml')
        urls = []
        names = []
        product_dict = {}
        products = results_soup.find_all("meta", {'itemprop' : 'url'})
        product_names = results_soup.find_all('img', title=True)
        if products:
            for product, name in zip(products, product_names):
                urls.append(str(url)+product['content'])
                names.append(name['title'])
            return names, urls
        else:
            return None

    #run async loop
    def to_run(self, param):
        result = self.search_result(param)
        if not result:
            return None
        else:
            titles, urls = self.search_result(param)
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            results = asyncio.run(self.main(urls))
            imgs_dict = self.product_img_link(titles, results)
            return imgs_dict


class Enter(Parser):
    def __init__(self):
        super().__init__()

    # get dict with names and images
    def get_imgs_links(self, names, products):
        imgs_dict = {}
        for name, product in zip(names, products):
            images = []
            product_soup = BeautifulSoup(product, 'lxml')
            imgs = product_soup.find_all('a', href=True)
            for img in imgs:
                if re.search('data-caption', str(img)):
                    images.append(img['href'])
                    print(f"{img['href']}")
            imgs_dict[name] = images
        # key - name , data - list of links
        return imgs_dict

    # parse main result page
    def search_page(self, param):
        url = 'https://enter.online/search/?q=' + str(param)
        main = requests.get(url, headers=HEADERS)
        main_soup = BeautifulSoup(main.content, 'lxml')
        urls = []
        titles = []
        products = main_soup.find_all('a', {'data-info_wrap': "true"})
        for product in products:
            if re.search('^https', str(product['href'])):
                urls.append(product['href'])
                titles.append(product['title'])
                print(f"{product['href']}")
                print(f"{product['title']}")
        if not urls and not titles:
            return None
        else:
            return titles, urls

    # run async loop
    def to_run(self, param):
        result = self.search_page(param)
        if not result:
            return None
        else:
            titles, urls = self.search_page(param)
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            results = asyncio.run(super().main(urls))
            imgs_dict = self.get_imgs_links(titles, results)
            return imgs_dict

class Darwin(Parser):

    def __init__(self):
        super().__init__()

    # get dict with names and images
    def get_imgs(self, names, products):
        imgs_dict = {}
        for name, product in zip(names, products):
            images = []
            product_soup = BeautifulSoup(product, 'lxml')
            imgs = product_soup('img')
            for i in imgs:
                if re.search('/product/', str(i['src'])):
                    images.append(i['src'])

            images = list(dict.fromkeys(images))
            # key - name , data - list of links
            imgs_dict[name] = images

        return imgs_dict

    def search(self, param):
        url = "https://darwin.md/"
        search_url = str(url) + 'search?search=' + str(param)
        search = requests.get(search_url, headers=HEADERS)
        products_soup = BeautifulSoup(search.content, 'lxml')
        urls = []
        names = []
        products = products_soup.find_all('a', href=True)
        temp_prod = ''
        for product in products:
            if re.search('.html', str(product['href'])) and product['href'] != temp_prod:
                urls.append(product['href'])
                temp_prod = product['href']
        temp_name = ''
        products_names = products_soup.find_all('figcaption', {'class': "info-wrap"})
        for name in products_names:
            if name['data-prods'] != temp_name:
                names.append(name['data-prods'])
                temp_name = name['data-prods']
        urls.pop(0)
        if not names:
            return None
        else:
            return names, urls

    # run async loop
    def to_run(self, param):
        result = self.search(param)
        if not result:
            return None
        else:
            titles, urls = self.search(param)
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            results = asyncio.run(super().main(urls))
            imgs_dict = self.get_imgs(titles, results)
            return imgs_dict
