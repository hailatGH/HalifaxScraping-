import time, csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Rent_Faster_Scraper:

    def __init__(self, base_url, csv_file):
        self.base_url = base_url
        self.csv_file = csv_file

    def get_data_list(self):
        browser = webdriver.Chrome()
        browser.get(self.base_url)

        wait = WebDriverWait(browser, 30)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "button.is-rounded.is-round.ng-binding.ng-scope")))
        time.sleep(10)

        html = browser.page_source

        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find('div', class_='listings listings-list').find_all('div', class_='listing-preview-wrap ng-scope')

        total_data = []
        for card in cards:
            data = {}
            data['image'] = card.find('img')['src']
            data['price'] = card.find('a', class_='dnt infobox-price has-text-black is-size-3').text.replace('\n','')
            
            wrapper = card.find('div', class_='my-3 is-clear').text.replace('  ','').replace('\n\n','\n').split('\n')
            wrapper = [val for val in wrapper if val]
            wrapper = [val for val in wrapper if val != ' ']
            data['type'] = wrapper[0]
            data['address'] = wrapper[1]
            data['district'] = wrapper[2]

            wrappers = card.find_all('div', class_='level-left')
            for wrapper in wrappers:
                wrapper = wrapper.text.replace('\n\n','\n').replace('  ','').split('\n')
                wrapper = [val.strip() for val in wrapper if val]
                wrapper = [val for val in wrapper if val != '•']
                if 'bd' in wrapper and 'ba' in wrapper:
                    data['bedroom'] = ' '.join(wrapper[:wrapper.index('bd')])
                    data['bathrom'] = ' '.join(wrapper[wrapper.index('bd') + 1:wrapper.index('ba')])
                elif 'bd' not in wrapper and 'studio' in wrapper and 'ba' in wrapper:
                    data['bedroom'] = wrapper[0]
                    data['bathrom'] = ' '.join(wrapper[wrapper.index('studio') + 1:wrapper.index('ba')])
                else:
                    if 'ft2' in wrapper:
                        data['area'] = ' '.join(wrapper[:wrapper.index('ft2')])
                        data['pet'] = ' '.join(wrapper[wrapper.index('ft2') + 1:])
                    else:
                        data['pet'] = wrapper[0]

            wrapper = card.find('div', class_='ng-binding ng-scope').text.replace('  ','').replace('\n\n','\n').replace('availability', '').split('\n')
            wrapper = [val.strip() for val in wrapper if val]
            data['availability'] = wrapper[0]

            wrapper = card.find('div', class_='has-text-grey dnt ng-binding is-size-8').text.replace('  ','').replace('ID ','').replace('\n\n','\n').split('\n')
            wrapper = [val for val in wrapper if val]
            data['id'] = wrapper[0]

            total_data.append(data)

        return total_data
    
    def write_to_csv(self, datas):
        """
        Write data to a CSV file.

        Parameters:
            data (list): A list of dictionaries containing data.
        """
        all_keys = set().union(*(d.keys() for d in datas))

        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=all_keys)
            writer.writeheader()
            for data in datas:
                row = {header: data.get(header, None) for header in all_keys}
                writer.writerow(row)

if __name__ == '__main__':
    BASE_URL = "https://www.rentfaster.ca/ns/halifax/rentals#dialog-listview"
    CSV_FILE = 'rentfaster.csv'

    scraper = Rent_Faster_Scraper(BASE_URL, CSV_FILE)
    data = scraper.get_data_list()
    scraper.write_to_csv(data) 