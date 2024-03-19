import requests
from bs4 import BeautifulSoup
import csv

class Apartment_Scraper_444_Rent:
    """A class to scrape apartment data from a website and write it to a CSV file."""

    def __init__(self, base_url, csv_file, csv_headers):
        """
        Initialize the ApartmentScraper object.

        Parameters:
            base_url (str): The base URL of the website to scrape.
            csv_file (str): The name of the CSV file to write the data to.
            csv_headers (list): A list containing the headers for the CSV file.
        """
        self.base_url = base_url
        self.csv_file = csv_file
        self.csv_headers = csv_headers

    def get_apartment_list(self):
        """
        Scrape apartment data from the website.

        Returns:
            list: A list of dictionaries containing apartment data.
        """
        total_apartments = []
        web_html_text = self.fetch_html_text(f'{self.base_url}/apartments.asp')
        soup = BeautifulSoup(web_html_text, 'lxml')
        sections = soup.find_all('table', width="100%", border="0", cellpadding="0", cellspacing="0", bgcolor="#ffffff")

        for section in sections:
            type = section.find('font', color="#FFFFFF").b.text
            section_apartments = section.find_all('tr', bgcolor=["#ffffff", "#e5e4e4"])
            
            for section_apartment in section_apartments:
                apartment = self.extract_apartment_data(section_apartment, type)
                total_apartments.append(apartment)

        return total_apartments

    def fetch_html_text(self, url):
        """Fetch HTML text from the provided URL."""
        return requests.get(url).text

    def extract_apartment_data(self, section_apartment, type):
        """Extract apartment data from the HTML section."""
        apartment = {}
        link = section_apartment.find('td').a['href']
        section_apartment_text = section_apartment.text.replace('  ', '').replace('\t', '').replace('\n\n', '\n').split('\n')
        section_apartment_text = [value.replace('\r', '').replace('\xa0', '') for value in section_apartment_text if value.strip()]

        if 'Halifax' in section_apartment_text[2]:
            apartment.update({
                'building': section_apartment_text[0],
                'unit': section_apartment_text[1],
                'location': section_apartment_text[2],
                'area': section_apartment_text[3],
                'price': section_apartment_text[4],
                'type': type
            })

            detail_html_text = self.fetch_html_text(f'{self.base_url}/{link}')
            apartment = self.extract_detailed_apartment_data(apartment, detail_html_text)

        return apartment

    def extract_detailed_apartment_data(self, apartment, detail_html_text):
        """Extract detailed apartment data from the provided HTML text."""
        detail_soup = BeautifulSoup(detail_html_text, 'lxml')
        right_section = detail_soup.find('td', style="padding-left:14px;", valign="top", align="left", width="52%")

        address = right_section.find('td', align='left', style='padding-left:4px;').text.replace('\n\n', '\n').replace('\t', '').strip().split('\n')
        address = [value.replace('\r', '').replace('\xa0', ' ') for value in address if value.strip()]
        apartment['address'] = address[0] + address[1]

        managers_info = right_section.find('div', style="margin-left:5px;margin-top:20px;").text.replace('  ','').replace('\t','').replace('\n\n','\n').split('\n')
        managers_info = [value.replace('\r', '').replace('\xa0', '').replace('|','') for value in managers_info if value.strip()] 
        
        for index, info in enumerate(managers_info):
            if "MANAGERS" in info or "MANAGER" in info:
                apartment[info] = managers_info[0]
            elif "@" in info:
                apartment['email'] = info
            elif "Website" in info:
                apartment['Website'] = managers_info[index + 1]
            elif "tel" in info:
                apartment['tel'] = managers_info[index + 1]
            elif "fax" in info:
                apartment['fax'] = managers_info[index + 1]

        tab_container = detail_soup.find('div', class_='tab_container')
        rows = tab_container.find('div', id="tab1").table.find_all('tr', recursive=False)

        for row in rows:
            key = ""
            value = ""
            cells = row.find_all('td', recursive=False)
            for cell in cells:
                if cell.find('b'):
                    key = cell.find('b').text.lower().replace(':','')

                if cell.find_all('table'):
                    list_vals = cell.find_all('table')
                    for val in list_vals:
                        value = value + val.text + ','

            apartment[key] = value

        tab_content = tab_container.find('div', id="tab4")
        rows  = tab_content.find('table', cellpadding="6")
        if rows:
            rows = rows.tr.td.find_all('table')
            apartment['other_features'] = ""
            for row in rows:
                text = row.text
                if 'floor' in text:
                    apartment['floors'] = text.split()[-2]
                elif ':' in text:
                    text = text.split(":")
                    text = [text_val.replace('\t','').replace('\n','').replace('\r','') for text_val in text]
                    apartment[text[0]] = text[1]
                else:
                    apartment['other_features'] = apartment['other_features'] + text + ', '
        rows  = tab_content.find_all('table', style="margin-top:-6px;")
        keys = []
        for row in rows:
            keys.append(row.find('b').text)


        rows = tab_content.find_all('table', width="95%")
        values = []
        for row in rows:
            text_list = []
            sub_rows = row.find_all('tr')
            for sub_row in sub_rows:
                text = sub_row.text.replace('\t', '').replace('\n', '')
                text_list.append(text)
            text_list = [val.replace('\r','').replace('\xa0','') for val in text_list]
            values.append(text_list)

        values = [','.join(sublist) for sublist in values]

        for index, key in enumerate(keys):
            apartment[key] = values[index]

        return apartment

    def write_to_csv(self, datas):
        """
        Write apartment data to a CSV file.

        Parameters:
            data (list): A list of dictionaries containing apartment data.
        """
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)
            writer.writeheader()
            for data in datas:
                row = {header: data.get(header, None) for header in self.csv_headers}
                writer.writerow(row)


if __name__ == '__main__':
    BASE_URL = "https://www.444rent.com"
    CSV_FILE = 'apartment_444_rent.csv'
    CSV_HEADERS = ['building', 'unit', 'location', 'area', 'price', 'type', 'address', 'RESIDENT MANAGERS', 'RESIDENT MANAGER', 'tel', 'fax', 'Website', 'email', 'lease', 'included', 'not included', 'parking', 'storage', 'Fridge', 'Ceiling Height', 'underground', 'Flooring', 'HRV Ventilation', 'Bathroom', 'floors', 'Appliances', 'Balcony Size', 'policy', 'Kitchen', 'deposit', 'heated underground', 'other_features']

    scraper = Apartment_Scraper_444_Rent(BASE_URL, CSV_FILE, CSV_HEADERS)
    data = scraper.get_apartment_list()
    scraper.write_to_csv(data) 