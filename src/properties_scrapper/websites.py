from typing import List
from properties_scrapper.properties import FincaraizProperty
from properties_scrapper.utils import HEADERS
from requests import get
from bs4 import BeautifulSoup
from bs4.element import Tag
from tqdm import tqdm

class FincaraizWebsite:
    url: str = 'https://www.fincaraiz.com.co/finca-raiz/'
    base_search_page: str = ("https://www.fincaraiz.com.co/finca-raiz/{}/{}/"
                             "?ad=30|{}||||1|||||55|5500006|||||||||||||||||||"
                             "1||griddate%20desc||||||||")
    property_class = FincaraizProperty
    current_search_type: str = ''
    current_search_city: str = ''
    current_page_number: int = 1
    current_search_page: str = ''
    current_response: BeautifulSoup = None
    properties: List[property_class] = []

    def __init__(self):
        pass
    
    def set_search_page(self, search_type: str = '', city: str = '',
                        page_number: int = 1):
        if search_type != '':
            self.current_search_type = search_type
        elif self.current_search_type == '':
            raise Exception('Search type not set yet. `set_search_page` '
                            'must be called first with a non-empty '
                            '`search_type`')
        
        if city != '':
            self.current_search_city = city
        elif self.current_search_city == '':
            raise Exception('Search city not set yet. `set_search_page` '
                            'must be called first with a non-empty '
                            '`city`')
        
        self.current_page_number = page_number
        self.current_search_page = self.base_search_page.format(
            self.current_search_type, self.current_search_city,
            self.current_page_number)
    
    def next_search_page(self):
        self.set_search_page(page_number=self.current_page_number+1)

    def get_current_response(self):
        response = get(self.current_search_page, HEADERS)
        self.current_response = BeautifulSoup(response.text, 'html.parser')

    def get_properties(self):
        if self.current_search_page == '':
            raise Exception('Search page not yet set. `set_search_page` must '
                            'be called first')
        self.get_current_response()
        containers = self.current_reponse.find_all(
            'ul', class_="advert Product_Code_ AD_OV")
        for container in containers:
            self.properties.append(self.property_class(container))
    
    def in_last_search_page(self):
        if self.current_search_page == '':
            raise Exception('Search page not yet set. `set_search_page` must '
                            'be called first')
        self.get_current_response()
        paginator = self.current_response.find("div", {"id": "divPaginator"})
        last_page = paginator.find_all('a')[-1].text.strip()        
        if last_page == 'Siguiente':
            return False
        if int(last_page) == self.current_page_number:
            return True            
        return False
        

    def parse_properties(self):
        if len(self.properties) == 0:
            raise Exception('Properties not found yet. `get_properties` must '
                            'be called first')
        for prop in tqdm(self.properties):
            prop.parse_property()