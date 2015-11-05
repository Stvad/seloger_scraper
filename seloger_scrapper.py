import requests
import bs4
from multiprocessing import Pool


class SeLogerScrapper:
    def __init__(self):
        self.apartment_id_list = []
        self.base_links = ["http://www.seloger.com/list.htm?cp=75&idtt=1&idtypebien=1,13,14,2,9&photo=15&pxmax=2000&rayon=15&tri=a_px_loyer&LISTING-LISTpg=",
                           "http://www.seloger.com/list.htm?cp=75&idtt=1&idtypebien=1,13,14,2,9&photo=15&pxmax=2000&rayon=15&tri=d_px_loyer&LISTING-LISTpg="]
        self.pages_count = 100

    def get_list_link(self):
        for link in self.base_links:
            for page in range(1, self.pages_count + 1):
                if not page % 10:
                    print(page)

                yield link + str(page)

    def get_apartment_links_from_page(self, url):
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return [article.attrs.get('data-listing-id')
                                  for article in soup.select('article.listing.life_annuity')]

    def get_apartment_links(self):
        pool = Pool(8)
        results_by_page = pool.map(self.get_apartment_links_from_page, self.get_list_link())
        for result in results_by_page:
            self.apartment_id_list.extend(result)


if __name__ == '__main__':
    selogerscrapper = SeLogerScrapper()

    # selogerscrapper.get_apartment_links_from_page("http://www.seloger.com/list.htm?cp=75&idtt=1&idtypebien=1,13,14,2,9&photo=15&pxmax=2000&rayon=15&tri=a_px_loyer&LISTING-LISTpg=1")
    # print(selogerscrapper.apartment_id_list)
    selogerscrapper.get_apartment_links()
    with open("idfile", mode='w', encoding='utf-8') as idfile:
        idfile.write('\n'.join(selogerscrapper.apartment_id_list) + '\n')


