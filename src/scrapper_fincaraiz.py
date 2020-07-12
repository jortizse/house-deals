from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from requests import get
import numpy as np
import pandas as pd
from time import sleep
from tqdm import tqdm
import sys


class ScrapperFincaraiz:

    def __init__(self, verbose=True, sleep_minutes=1):
        self.base_url = "https://www.fincaraiz.com.co/"
        self.attributes = ['Code', 'Title', 'Type', 'Sector', 'Neighborhood',
                           'Price (COP)', 'Area', 'Num. rooms', 'Update Date',
                           'City', 'Province', 'URL']
        self.verbose = verbose
        self.headers = ({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) '
                                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                                       'Chrome/41.0.2228.0 Safari/537.36'})
        self.sleep = sleep_minutes

    def search_properties(self):
        """Execute a search in the website under certain parameters (e.g., city
        and return the """
        base_url = self.base_url
        first_url = ''
        return base_url, first_url

    def parse_property(self, property_container):
        """"""

        def get_date(day_month):
            today = date.today()
            current_year = today.year
            new_date = datetime.strptime(f'{day_month}/{current_year}',
                                         '%d/%m/%Y').date()
            if new_date > today:
                new_date.replace(year=current_year - 1)
            return new_date

        def parse_property_page(house_page_url, headers):
            house_response = get(house_page_url, headers=headers)
            house_soup = BeautifulSoup(house_response.text, 'html.parser')
            location = house_soup.find_all('div', class_='breadcrumb left')[
                0].find_all('a')
            location = [loc.text for loc in location[1:]]
            n_missing = 4 - len(location)
            location += [''] * n_missing
            info = \
                house_soup.find_all('div',
                                    class_='box_content row historyAdvert')[
                    0].find_all('span')
            info = [i.text for i in info]
            if info[0] == 'Hoy':
                up_date = date.today()
            elif info[0] == 'Ayer':
                up_date = date.today() - timedelta(days=1)
            else:
                up_date = get_date(info[0])
            local_code = info[2]
            return tuple(location) + (up_date, local_code)

        property_details = property_container.find_all('a')[0]
        property_page = property_details['href']
        title = property_details.findChild(class_='h2-grid').text.strip()
        type_ = title.split(' ')[0]
        property_page_url = self.base_url + property_page
        price = int(property_container.find_all(
            'meta', itemprop='price')[0]['content'])
        text = property_container.find_all(
            'li', class_='surface li_advert')[0].text.split('\n')
        area = text[1].replace(" ", "").replace(".", "").replace(",", ".")
        area = float(area[:area.find('m')])
        try:
            num_rooms = int(text[3][0])
        except ValueError:
            num_rooms = ''

        parsed_data = parse_property_page(property_page_url, self.headers)
        dep, city, sector, neighborhood, update_date, code = parsed_data
        data = [code, title, type_, sector, neighborhood, price, area,
                num_rooms, update_date, city, dep, property_page_url]
        return data

    def parse_search_page(self, search_page_soup, properties_df=None):
        """Takes a parsed html search page (soup) and returns a pandas.DataFrame
        that contains the parsed information of every property in the page"""
        if properties_df is None:
            properties_df = pd.DataFrame(columns=self.attributes)

        properties_containers = search_page_soup.find_all(
            'ul', class_="advert Product_Code_ AD_OV")
        n_properties = len(properties_containers)

        for h, property_container in tqdm(enumerate(properties_containers),
                                          total=n_properties):
            try:
                property_data = self.parse_property(property_container)
                properties_df = properties_df.append(
                    pd.DataFrame([property_data], columns=self.attributes),
                    ignore_index=True, sort=False)
            except Exception as e:
                print(e)
                pass
            sleep(self.sleep)
        return properties_df

    def parse_search_results(self, reference_url, save_file_name,
                             max_pages=np.inf) -> pd.DataFrame:
        """"""
        properties_df = pd.DataFrame(columns=self.attributes)
        page = 1
        while page <= max_pages:
            if self.verbose:
                print('Page: ', page)
            url = reference_url.format(page)
            if self.verbose:
                print(url)
            page_response = get(url, headers=self.headers)
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            properties_df = self.parse_search_page(page_soup,
                                                   properties_df=properties_df)
            next_page = page_soup.find_all('a',
                                           title='Ir a la pagina Siguiente')
            page += 1
            properties_df.to_csv(f'{save_file_name}.csv')
            if len(next_page) == 0:
                break

        return properties_df
