from requests import get
from typing import List, Optional

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from time import sleep
from tqdm import tqdm
from properties_scrapper.websites import FincaraizWebsite


class FincaraizScrapper:
    website_class = FincaraizWebsite
    attributes: List[str] = [
        'Code', 'Title', 'Type', 'Sector', 'Neighborhood', 'Price (COP)',
        'Area (m2)', 'Num. rooms', 'Update Date', 'City', 'Province', 'URL']
    properties_df: pd.DataFrame = pd.DataFrame(columns=attributes)
    def __init__(self, verbose=True, sleep_minutes=1):        
        self.website = self.website_class()
        self.verbose = verbose
        self.sleep = sleep_minutes


    def search_properties(self, search_type: str, city: str,
                          max_pages: Optional[int] = None):
        """Execute a search in the website under certain parameters (e.g., city
        and return the """
        self.website.set_search_page(search_type, city)
        self.website.get_properties()

        first_url = ''
        return base_url, first_url

    
        # dep, city, sector, neighborhood, update_date, code = parsed_data
        # data = [code, title, type_, sector, neighborhood, price, area,
        #         num_rooms, update_date, city, dep, property_page_url]
        

    def parse_search_page(self, search_page_soup, properties_df=None):
        """Takes a parsed html search page (soup) and returns a pandas.DataFrame
        that contains the parsed information of every property in the page"""
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
