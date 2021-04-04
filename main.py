import requests
from bs4 import BeautifulSoup
import logging
import json
import re


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

    def match_keys_and_values(self):
        """
        A List with all the keys and values from the certain class type will be crated
        """
        for key in self.soup.findAll('td', class_=re.compile("Pos")):
            self.keys.append(key.span.text.strip())

        for value in self.soup.findAll('td', class_=re.compile("Pstart")):
            self.values.append(value.text.strip())
        self.check_if_list_empty(self.keys)
        self.check_if_list_empty(self.values)
        self.convert_values(self.values)

    @staticmethod
    def check_if_list_empty(list_):
        if not list_:
            logger.debug('List is empty. Something went wrong.'.format(list_))
        else:
            logger.debug('List created:{}'.format(list_))
            logger.info('List hast this many elements:{}'.format(len(list_)))

    def parse_list(self, upper_limit, list_to_change):
        """Takes the first x (upper) elements of a list"""
        self.parsed_list = list_to_change[0:upper_limit]
        logger.debug("The first {} elements from {} will be taken".format(upper_limit, list_to_change))
        logger.debug("Elements in the parsed list: {}".format(self.parsed_list))

    def create_index_dictionary(self, list_1, list_2):
        """Hard coded dictionary, specifically built for the Yahoo Scraper"""
        all_dict = {
            'Valuation Measures': dict(zip(list_1[:9], list_2[:9])),
            'Fiscal Year': dict(zip(list_1[37:39], list_2[37:39])),
            'Profitability': dict(zip(list_1[39:41], list_2[39:41])),
            'Management Effectiveness': dict(zip(list_1[41:43], list_2[41:43])),
            'Income Statement': dict(zip(list_1[43:51], list_2[43:51])),
            'Balance Sheet': dict(zip(list_1[51:57], list_2[51:57])),
            'Cash Flow Statement': dict(zip(list_1[57:59], list_2[57:59])),
        }
        self.dictionary = {self.index: all_dict}
        logger.info('Zipped dictionary: {}'.format(self.dictionary))

    def dict_to_json(self):
        with open(f'{self.index}.json', 'w') as json_file:
            json.dump(self.dictionary, json_file)
        logger.info('Created .json file: {}.json'.format(self.index))

    @staticmethod
    def convert_values(list_):
        """ Converts list items from string to float
         Converts T into Trillions
         Overwrite the new list
         """
        conversion_factors = {
            'T': 1_000_000_000_000,
            'B': 1_000_000_000,
            'M': 1_000_000
        }
        regex_date = re.compile(r'\D{3}\s\d{2}.\s\d{4}')  # Example: Aug 30, 2020
        for idx, item in enumerate(list_):
            if 'T' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                float_v_item = float(item[:-1])
                new_item = float_v_item * conversion_factors['T']
                logger.info('A conversion will be necessary for {}'.format(item))
                logger.info('Conversion factor {}'.format(conversion_factors['T']))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif 'B' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                float_v_item = float(item[:-1])
                new_item = float_v_item * conversion_factors['B']
                logger.info('A conversion will be necessary for {}'.format(item))
                logger.info('Conversion factor {}'.format(conversion_factors['B']))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif 'M' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                float_v_item = float(item[:-1])
                new_item = float_v_item * conversion_factors['M']
                logger.info('A conversion will be necessary for {}'.format(item))
                logger.info('Conversion factor {}'.format(conversion_factors['M']))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif regex_date.search(item) is not None:  # Example: Aug 30, 2020
                logger.info('id: {} for item: {}'.format(idx, item))
                new_item = str(item)
                logger.info('Date format found: {}'.format(item))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif ',' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                new_item = item.replace(',', '')
                logger.info('\',\'Found in list: {}'.format(item))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = float(new_item)
            elif 'N/A' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                new_item = item
                logger.info('N/A element found in list: {}'.format(new_item))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif '%' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                new_item = float(item[:-1])
                logger.info('Percentage symbol found in list: '.format(item))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = float(new_item)
            elif ':' in item:
                logger.info('id: {} for item: {}'.format(idx, item))
                new_item = str(item)
                logger.info('Colon symbol found in list: '.format(item))
                logger.info('Old value: {}\n\tNew value: {}'.format(item, new_item))
                list_[idx] = new_item
            elif type(item) == str:
                logger.info('id: {} for item: {}'.format(idx, item))
                new_item = float(item)
                logger.info('Type {} found in list.\nTransformed in type: for item:{}'.format(type(item), type(new_item)))
                list_[idx] = new_item
        logger.info('Converted list:{}'.format(list_))
        logger.info('Converted list length:{}'.format(len(list_)))

stock_list = ['AAPL', 'TSLA']

with open(f'Yahoo_Financials.json', 'a') as json_file:
    json_file.write('{')
    for item in stock_list:
        if __name__ == '__main__':
            stock = YahooFinancials(item)
            stock.create_url()
            stock.get_response()
            stock.soup_the_response()
            stock.output_content_as_html()
            stock.match_keys_and_values()
            stock.create_index_dictionary(stock.keys, stock.values)
            stock.dict_to_json()
        json.dump(stock.dictionary, json_file,indent=2)
        json_file.write('{')
        logger.info('Created .json file: Yahoo_Financials.json')
