import csv, re
from bs4 import BeautifulSoup
from requests_html import HTMLSession

class Zumper_Scraper:
    """A class to scrape data from a website and write it to a CSV file."""

    def __init__(self, base_url, csv_file):
        """
        Initialize the Scraper object.

        Parameters:
            base_url (str): The base URL of the website to scrape.
            csv_file (str): The name of the CSV file to write the data to.
            csv_headers (list): A list containing the headers for the CSV file.
        """
        self.base_url = base_url
        self.csv_file = csv_file

    def get_data_list(self):
        """
        Scrape data from the website.

        Returns:
            list: A list of dictionaries containing data.
        """
        total_datas = []
        page = 1

        while True:
            session = HTMLSession()
            response = session.get(f"{self.base_url}{page}")
            response.html.render(timeout=4000, scrolldown=4000)

            soup = BeautifulSoup(response.html.html, 'html.parser')
            cards = soup.find_all("div", class_="css-8a605h")
            
            print(len(cards))
            if len(cards) <= 0:
                break
        
            for card in cards:
                data = {}

                images = card.find_all('img')
                for index, image in enumerate(images):
                    img_src = image.get('src')
                    if img_src:
                        data[f'image_{index}'] = img_src

                content = card.find('div', class_='css-0 e1k4it830')
                if content:
                    building = content.find('a')
                    data['bulding'] = building.text if building else ""
                    sections = content.find_all('div')
                    for section in sections:
                        sub_sections = section.find_all('div')
                        for sub_section in sub_sections:
                            text = sub_section.text
                            parts = None
                            
                            has_comma, has_no_dollar = self.check_comma_non_number(text)
                            if has_comma and has_no_dollar:
                                data['address'] = text
                            
                            
                            if "$" in text:
                                data['price'] = text
                            elif "beds" in text:
                                parts = text.split("beds") 
                            elif "bed" in text:
                                parts = text.split("bed") 
                            elif "|" in text:
                                data['other_features'] = text    
                           
                            if parts:
                                data['beds_count'] = parts[0]
                                data['baths_count'] = parts[1].split()[0]

                total_datas.append(data)
            
            page = page + 1

        return total_datas
    
    def check_comma_non_number(self, string):
        has_comma = "," in string
        has_no_dollar = "$" not in string
        
        return has_comma, has_no_dollar


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
    BASE_URL = "https://www.zumper.com/apartments-for-rent/halifax-ns?page="
    CSV_FILE = 'zumper.csv'

    scraper = Zumper_Scraper(BASE_URL, CSV_FILE)
    data = scraper.get_data_list()
    scraper.write_to_csv(data) 