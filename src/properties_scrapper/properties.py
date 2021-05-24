from datetime import datetime, date, timedelta
from requests import get
from typing import List
import warnings
# Non-standard imports
from bs4 import BeautifulSoup
from bs4.element import Tag
from properties_scrapper.utils import HEADERS


class FincaraizProperty:
    
    base_url: str = 'https://www.fincaraiz.com.co/'
    area: float = None
    city: str = ''
    container: Tag = None
    code: str = ''
    neighborhood: str = ''
    num_rooms: int = None
    page_url: str = ''
    price: int = None
    province: str = ''
    sector: str = ''
    title: str = ''
    type_prop: str = ''
    
    _container_text: List[str] = []
    _page_response : BeautifulSoup = None
    
    def __init__(self, property_container: Tag):
        self.container = property_container
        self.__parse_metadata()
    
    def __repr__(self):
        return self.title

    def __parse_price(self):
        self.price = int(self.container.find_all('meta')[1]['content'])
    
    def __parse_area(self):
        area = (self._container_text[1]
                .replace(" ","")
                .replace(".","")
                .replace(",","."))
        area = area[:area.find('m')]
        try:
            self.area = float(area)
        except ValueError:
            warnings.warn(f'Area value {area} not convertible to float')
            self.area = area
    
    def __parse_num_rooms(self):
        try:
            self.num_rooms = int(self._container_text[3][0])
        except ValueError:
            pass
    
    def __parse_container_text(self) -> List[str]:
        self._container_text = (
            self.container.find_all('li', class_='surface li_advert')[0]
            .text.split('\n'))
    
    def __parse_metadata(self):
        details = self.container.find_all('a')[0]
        self.title = details.findChild(class_='h2-grid').text.strip()        
        self.type_prop = self.title.split(' ')[0]
        ref =  details['href']
        url_pos = ref.find('url')
        if url_pos == -1:
            self.page_url = self.base_url + ref
        else:    
            self.page_url = ref[ref.find('url')+4:]
    
    def __parse_page_response(self):
        response = get(self.page_url, headers=HEADERS)
        self._page_response = BeautifulSoup(response.text, 'html.parser')
    
    def __parse_location(self):
        beadcrumb = (self._page_response
                     .find_all('div', class_='breadcrumb left')[0]
                     .find_all('a'))
        location = [loc.text for loc in beadcrumb[1:]]
        n_missing = 4 - len(location)
        location += [''] * n_missing
        self.province, self.city, self.sector, self.neighborhood = location
    
    def __parse_update_date(self):
        info = (self._page_response
                .find_all('div', class_='box_content row historyAdvert')[0]
                .find_all('span'))
        info = [i.text for i in info]
        update_date = info[0]
        if update_date == 'Hoy':
            self.update_date = date.today()
        elif update_date == 'Ayer':
            self.update_date = date.today() - timedelta(days=1)
        else:
            self.update_date = get_date(update_date)
        
    def __parse_code(self):
        info = (self._page_response
                .find_all('div', class_='box_content row historyAdvert')[0]
                .find_all('span'))
        info = [i.text for i in info]
        self.code = info[2]
    
    def parse_property(self):
        # Parse data from property container
        self.__parse_price()
        self.__parse_container_text()
        self.__parse_area()
        self.__parse_num_rooms()        
        self.__parse_page_response()
        # Parse data from property page
        self.__parse_location()
        self.__parse_update_date()
        self.__parse_code()

def get_date(day_month):
    today = date.today()
    current_year = today.year
    new_date = datetime.strptime(f'{day_month}/{current_year}',
                                 '%d/%m/%Y').date()
    if new_date > today:
        new_date.replace(year=current_year - 1)
    return new_date