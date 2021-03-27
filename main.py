import requests
from bs4 import BeautifulSoup
import logging
import json


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s - %(name)s - %(funcName)s() - %(lineno)d - %(message)s')

file_handler = logging.FileHandler('Statistics.log', mode='w')
file_handler.setFormatter(formatter)

stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)

logger.addHandler(file_handler)


class YahooFinancials:
    """ Scrapes data from a certain Company, from the Yahoo Fiance website."""

    def __init__(self, index):
        """ Initialize attributes for an index: AAPL, TSLA, etc"""
        self.index = index
        self.yahoo_url = None
        self.response = None
        self.content = None
        self.soup = None
        self.topic_title = None
        self.keys = []
        self.values = []
        self.parsed_list = []
        self.dictionary = {}

    def create_url(self):
        self.yahoo_url = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'.format(self.index, self.index)
        logger.info('Url to scrap: {}'.format(self.yahoo_url))
        print(self.yahoo_url)

    def get_response(self):
        """
        Downloads the .html info using the requests module.
        """
        self.response = requests.get(self.yahoo_url)
        self.content = self.response.content
        logger.info('Selected url: {}'.format(self.yahoo_url))
        self.check_response()

    def check_response(self):
        """Checks if the response was successful (200)."""
        if self.response.status_code == 200:
            logger.info('Response was successful: {}'.format(self.response))
        else:
            logger.info('Response was unsuccessful: {}'.format(self.response))

    def soup_the_response(self):
        """Creates a soup object."""
        self.soup = BeautifulSoup(self.content, 'lxml')
        logger.info('The response was souped, and a soup object was created.')

    def output_content_as_html(self):
        """Creates a file output.html where the website content will be written."""
        with open("output.html", "w", encoding="utf-8") as file:
            file.write(str(self.soup.prettify()))
            logger.info('Content file created: {}'.format(file.name))

    def match_title(self, table_title):
        """
        Creates a soup object of the valuation measures table, where all the data is available.
        Here we'll take only the title (Valuations Measures).
        """
        logger.info('Selected search criteria (html format): {}'.format(table_title))
        valuation_measures_table = self.soup.find('div', class_=table_title)
        self.topic_title = valuation_measures_table.span.text
        logger.info('Selected class (html format): {}'.format(table_title))
        logger.info('Class Title: {}'.format(self.topic_title))

    def match_keys(self, value, cls_type, some_list):
        """
        A List with all the values from the certain class type will be crated
        """
        for value in self.soup.findAll(cls_type, class_=value):
            object_value = value.span.text
            some_list.append(object_value)
        if not some_list:
            logger.info('Name list is empty, something went wrong.')
        else:
            logger.info('Value list created:{}'.format(some_list))

    def match_values(self, value, cls_type, some_list):
        """
        A List with all the values from the certain class type will be crated
        """
        for value in self.soup.findAll(cls_type, class_=value):
            object_value = value.text
            some_list.append(object_value)
        if not some_list:
            logger.info('Name list is empty, something went wrong.')
        else:
            logger.info('Value list created:{}'.format(some_list))
        self.parse_list(9, some_list)
        logger.info('Parsed list created:{}'.format(self.parsed_list))
        self.convert_values(self.parsed_list)
        logger.debug('Value list (parsed & converted):{}'.format(self.parsed_list))

    def parse_list(self, upper_limit, list_to_change):
        """Takes the first x (upper) elements of a list"""
        self.parsed_list = list_to_change[0:upper_limit]
        logger.debug("The first {} elements from {} will be taken".format(upper_limit, list_to_change))
        logger.debug("Elements in the parsed list: {}".format(self.parsed_list))

    def create_main_dictionary(self, list_1, list_2):
        """Zips(combine) the two lists into a dictionary"""
        self.dictionary_topic = {self.topic_title: dict(zip(list_1, list_2))}
        self.dictionary = {self.index: self.dictionary_topic }
        logger.info('Zipped dictionary: {}'.format(self.dictionary))

    def dict_to_json(self):
        with open (f'{self.index}.json', 'w') as json_file:
            json.dump(self.dictionary, json_file)
        logger.info('Created .json file: {}.json'.format(self.index))

    @staticmethod
    def convert_values(list_):
        """ Converts list items from string to float
         Converts T into Trillions
         Overwrite the new list
         """
        conversion_factors = {'T': 1_000_000_000_000, 'B': 1_000_000_000}
        for idx, item in enumerate(list_):
            if 'T' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                float_v_item = float(item[:-1])
                new_item = float_v_item * conversion_factors['T']
                logger.info('A conversion will be necessary for {}'.format(item))
                logger.info('Conversion factor {}'.format(conversion_factors['T']))
                logger.info('Old value: {}\nNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif 'B' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                float_v_item = float(item[:-1])
                new_item = float_v_item * conversion_factors['B']
                logger.info('A conversion will be necessary for {}'.format(item))
                logger.info('Conversion factor {}'.format(conversion_factors['B']))
                logger.info('Old value: {}\nNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif ',' in item:
                new_item = item.replace(',','')
                list_[idx] = float(new_item)

            elif type(item) == str:
                logger.info('id: {} for item:{}'.format(idx, item))
                float_v_item = float(item[:-1])
                list_[idx] = float_v_item
        logger.info('Converted list:{}'.format(list_))


if __name__ == '__main__':
    stock = YahooFinancials('TSLA')
    stock.create_url()
    stock.get_response()
    stock.soup_the_response()
    stock.output_content_as_html()
    stock.match_title('Mstart(a) Mend(a)')
    stock.match_keys('data-reactid', 'span', stock.keys)
    stock.match_values('Fw(500) Ta(end) Pstart(10px) Miw(60px)', 'td', stock.values)
    stock.create_main_dictionary(stock.keys, stock.parsed_list)
    stock.dict_to_json()