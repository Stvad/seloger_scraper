import requests
import bs4
import re
from multiprocessing import Pool


class SeLogerScrapper:
    def __init__(self):
        self.apartment_id_list = []
        self.base_links = ["http://www.seloger.com/list.htm?cp=75&idtt=1&idtypebien=1,13,14,2,9&photo=15&pxmax=2000&rayon=15&tri=a_px_loyer&LISTING-LISTpg=",
                           "http://www.seloger.com/list.htm?cp=75&idtt=1&idtypebien=1,13,14,2,9&photo=15&pxmax=2000&rayon=15&tri=d_px_loyer&LISTING-LISTpg="]

        self.pages_count = 100

        self.apartments = []

    def get_list_link(self):
        for link in self.base_links:
            for page in range(1, self.pages_count + 1):
                yield link + str(page)

    @staticmethod
    def get_apartment_links_from_url(url):
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return [article.attrs.get('data-listing-id')
                                  for article in soup.select('article.listing.life_annuity')]

    def get_apartment_links(self):
        pool = Pool(8)
        results_by_page = pool.map(SeLogerScrapper.get_apartment_links_from_url, self.get_list_link())
        for result in results_by_page:
            self.apartment_id_list.extend(result)

    def get_apartment_url(self):
        base_apartment_url = "http://www.seloger.com/annonces/locations/appartement/paris-17eme-75/"
        for id in self.apartment_id_list:
            yield base_apartment_url + id + '.htm'

    @staticmethod
    def get_apartment_info_from_url(url):
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        # soup.select('h1.detail-title')
        apartment_info = {"url": url}
        title_tag = soup.find("h1", class_="detail-title")
        apartment_info["name"] = next(title_tag.stripped_strings)

        resume_info = soup.find("div", class_="resume__infos")
        price_string = next(resume_info.find(id="price").stripped_strings)
        apartment_info["price"] = int(price_string.split()[0])

        description = soup.find(class_="detail__description")
        apartment_info["description"] = description.find("p", class_="description").string

        apartment_info.update(SeLogerScrapper.process_criteria(
            description.find_all("li", class_="liste__item liste__item-switch")))

        return apartment_info

    @staticmethod
    def process_criteria(criteria):
        processed_criteria = {}
        for criterion in criteria: #reorginize?
            if "m²" in criterion.string:
                processed_criteria["floor_size"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "etage" in criterion.string.lower():
                processed_criteria["floor"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "etages" in criterion.string.lower():
                processed_criteria["floors_total"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "pièce" in criterion.string.lower() or "pièces" in criterion.string.lower():
                processed_criteria["rooms_count"] = SeLogerScrapper.get_string_number(criterion.string)
            elif "meublé" in criterion.string.lower():
                processed_criteria["furnished"] = True

        return processed_criteria

    @staticmethod
    def get_string_number(string):
        # return int(''.join(filter(str.isdigit, string)))
        return int(re.search(r'\d+', string).group())

    def get_apartments_info(self):
        pool = Pool(8)
        self.apartments = pool.map(SeLogerScrapper.get_apartment_info_from_url, self.get_apartment_url())


if __name__ == '__main__':
    selogerscrapper = SeLogerScrapper()

    # selogerscrapper.get_apartment_links_from_page("http://www.seloger.com/list.htm?cp=75&idtt=1&idtypebien=1,13,14,2,9&photo=15&pxmax=2000&rayon=15&tri=a_px_loyer&LISTING-LISTpg=1")
    # print(selogerscrapper.apartment_id_list)


    # selogerscrapper.get_apartment_links()
    # with open("idfile", mode='w', encoding='utf-8') as idfile:
    #     idfile.write('\n'.join(selogerscrapper.apartment_id_list) + '\n')

    print(selogerscrapper.get_apartment_info_from_url("http://www.seloger.com/annonces/locations/appartement/paris-20eme-75/gambetta/103726133.htm"))


