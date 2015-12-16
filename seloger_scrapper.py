import traceback
from argparse import ArgumentParser

import requests
import bs4
import re
import csv
import argparse

from multiprocessing import Pool


class SeLogerScrapper:
    def __init__(self, thread_number=8):
        self.thread_number = thread_number

    @staticmethod
    def get_list_link(base_urls, pages_count):
        for link in base_urls:
            for page in range(1, pages_count + 1):
                yield link + str(page)

    @staticmethod
    def get_apartment_links_from_url(url):
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        result_set = {article.attrs.get('data-listing-id')
                      for article in soup.select('article.listing.life_annuity')}
        return list(result_set)

    def get_apartment_links(self, base_urls, pages_count):
        pool = Pool(self.thread_number)
        apartment_id_list = []

        results_by_page = pool.map(SeLogerScrapper.get_apartment_links_from_url,
                                   self.get_list_link(base_urls, pages_count))

        for result in results_by_page:
            apartment_id_list.extend(result)

        return apartment_id_list

    @staticmethod
    def get_apartment_url(apartment_id_list,
                          base_apartment_url="http://www.seloger.com/annonces/locations/appartement/paris-17eme-75/"):

        for id in apartment_id_list:
            yield base_apartment_url + id + '.htm'

    @staticmethod
    def get_apartment_info_from_url(url):
        try:
            response = requests.get(url)
            soup = bs4.BeautifulSoup(response.text, "lxml")
            # soup.select('h1.detail-title')
            apartment_info = {"url": url}
            title_tag = soup.find("h1", class_="detail-title")
            apartment_info["name"] = next(title_tag.stripped_strings)

            resume_info = soup.find("div", class_="resume__infos")
            price_string = next(resume_info.find(id="price").stripped_strings)
            coma = price_string.find(',')
            if coma != -1:
                price_string = price_string[:coma] #yeah it's starting to look really sad
            apartment_info["price"] = int(''.join(filter(str.isdigit, price_string)))
            #int(price_string.split()[0])

            description = soup.find(class_="detail__description")
            apartment_info["neighborhood"] = \
                SeLogerScrapper.get_string_number(description.find(class_="detail-subtitle").find("span").string)
            apartment_info["description"] = str(description.find("p", class_="description").string)

            parameter_list = description.find("ol", class_="description-liste")
            apartment_info.update(SeLogerScrapper.process_criteria(parameter_list.find_all('li')))
        except Exception:
            print(url)
            print(traceback.format_exc())
            return {}

        return apartment_info

    @staticmethod
    def process_criteria(criteria):
        processed_criteria = {"furnished": 0, "balcony": 0, "separate_toilet": 0}
        for criterion in criteria: #reorginize?
            if not criterion.string:
                continue
            elif "m²" in criterion.string:
                processed_criteria["floor_size"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "etages" in criterion.string.lower(): #i know it will overlap with etage, but considering order - it's ok
                processed_criteria["floors_total"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "etage" in criterion.string.lower():
                processed_criteria["floor"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "pièce" in criterion.string.lower():
                processed_criteria["rooms_count"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "meublé" in criterion.string.lower():
                processed_criteria["furnished"] = 1
            elif "balcon" in criterion.string.lower() or "terrasse" in criterion.string.lower():
                processed_criteria["balcony"] = 1
            elif "toilettes séparées" in criterion.string.lower():
                processed_criteria["separate_toilet"] = 1

        return processed_criteria

    @staticmethod
    def get_string_number(string):
        # return int(''.join(filter(str.isdigit, string)))
        if 'rdc' in string.lower():
            return 1
        return int(re.search(r'\d+', string).group())

    def get_apartments_info(self, base_urls, pages_count=100):
        apartment_id = self.get_apartment_links(base_urls, pages_count)

        pool = Pool(self.thread_number)
        return pool.map(SeLogerScrapper.get_apartment_info_from_url, self.get_apartment_url(apartment_id))


if __name__ == '__main__':
    selogerscrapper = SeLogerScrapper()

    parser = ArgumentParser(description="Scrapper for SeLoger.com")

    parser.add_argument('urls', metavar='URLs', type=str, nargs='+', help='List of base search URLs')
    parser.add_argument('-o', '--output', default='apartments.csv', type=str)
    parser.add_argument('-p', '--pages', default=100, type=int)

    arguments = parser.parse_args()

    with open(arguments.output, mode='w', encoding='utf-8') as csvfile:
        fieldnames = ["floor_size", "price", "furnished", "balcony", "floor", "rooms_count", "neighborhood",
                      "separate_toilet", "floors_total", "name", "description", "url"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(selogerscrapper.get_apartments_info(arguments.urls, arguments.pages))





