import requests
import csv
from bs4 import BeautifulSoup


class Commercial_Scraper_444_Rent:
    """A class to scrape commercial data from a website and write it to a CSV file."""

    def __init__(self, base_url, csv_file, csv_headers):
        """
        Initialize the CommercialScraper object.

        Parameters:
            base_url (str): The base URL of the website to scrape.
            csv_file (str): The name of the CSV file to write the data to.
            csv_headers (list): A list containing the headers for the CSV file.
        """
        self.base_url = base_url
        self.csv_file = csv_file
        self.csv_headers = csv_headers

    def get_commercial_list(self):
        """
        Scrape commercial data from the website.

        Returns:
            list: A list of dictionaries containing commercial data.
        """
        total_commercials = []
        web_html_text = self.fetch_html_text(f'{self.base_url}/commercial.asp')
        soup = BeautifulSoup(web_html_text, 'lxml')

        commercials = soup.find_all('tr', bgcolor=['#e5e4e4','#ffffff'])
        for commercial_row in commercials:
            commercial = self.extract_commercial_data(commercial_row)
            total_commercials.append(commercial)

        return total_commercials

    def fetch_html_text(self, url):
        """Fetch HTML text from the provided URL."""
        return requests.get(url).text

    def extract_commercial_data(self, commercial_row):
        """Extract commercial data from the HTML row."""
        commercial = {}
        link = commercial_row['onclick'].replace("location.href=", '').replace("'","")
        commercial_row_text = commercial_row.text.replace('  ', '').replace('\t', '').replace('\n\n', '\n').split('\n')
        commercial_row_text = [value.replace('\r', '').replace('\xa0', '') for value in commercial_row_text if value.strip()]

        commercial.update({
            'building': commercial_row_text[0],
            'unit': commercial_row_text[1],
            'area': commercial_row_text[2],
            'type': commercial_row_text[3],
            'available': commercial_row_text[4],
            'rent': commercial_row_text[5]
        })

        detail_html_text = self.fetch_html_text(f'{self.base_url}/{link}')
        commercial = self.extract_detailed_commercial_data(commercial, detail_html_text)

        return commercial

    def extract_detailed_commercial_data(self, commercial, detail_html_text):
        """Extract detailed commercial data from the provided HTML text."""
        detail_soup = BeautifulSoup(detail_html_text, 'lxml')
        right_section = detail_soup.find('td', style="padding-left:14px;", valign="top", align="left", width="52%")

        address = right_section.find('td', align='left', style='padding-left:4px;').text.replace('\n\n', '\n').replace('\t', '').strip().split('\n')
        address = [value.replace('\r', '').replace('\xa0', ' ') for value in address if value.strip()]
        commercial['address'] = address[0] + " " + address[1]

        managers_info = right_section.find('div', style="margin-left:5px;margin-top:20px;").text.replace('  ','').replace('\t','').replace('\n\n','\n').split('\n')
        managers_info = [value.replace('\r', '').replace('\xa0', '').replace('|','') for value in managers_info if value.strip()] 

        for index, info in enumerate(managers_info):
            if "MANAGER" in info or "COORDINATOR" in info:
                commercial[info] = managers_info[0]
            elif "@" in info:
                commercial['email'] = info
            elif "Website" in info:
                commercial['Website'] = managers_info[index + 1]
            elif "tel" in info:
                commercial['tel'] = managers_info[index + 1]
            elif "fax" in info:
                commercial['fax'] = managers_info[index + 1]

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
                if not key == "call now" and not value == "":
                    commercial[key] = value

        tab_content = tab_container.find('div', id="tab4")
        rows  = tab_content.find('table', cellpadding="6")
        if rows:
            rows = rows.tr.td.find_all('table')
            commercial['other_features'] = ""
            for row in rows:
                text = row.text
                if 'floor' in text:
                    commercial['floors'] = text.split()[-2]
                elif ':' in text:
                    text = text.split(":")
                    text = [text_val.replace('\t','').replace('\n','').replace('\r','') for text_val in text]
                    commercial[text[0]] = text[1]
                else:
                    commercial['other_features'] = commercial['other_features'] + text + ', '
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
            commercial[key] = values[index]

        return commercial

    def write_to_csv(self, datas):
        """
        Write commercial data to a CSV file.

        Parameters:
            data (list): A list of dictionaries containing commercial data.
        """
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)
            writer.writeheader()
            for data in datas:
                row = {header: data.get(header, None) for header in self.csv_headers}
                writer.writerow(row)


if __name__ == '__main__':
    BASE_URL = "https://www.444rent.com"
    CSV_FILE = 'commercial_444_rent.csv'
    CSV_HEADERS = ['building', 'unit', 'area', 'type', 'available', 'rent', 'address', 'COMMERCIAL PROPERTY MANAGER', 'tel', 'Website', 'email', 'rent includes', 'lease', 'tenant pays', 'rentable area', 'Ceiling Height', 'heated underground', 'useable area', 'parking', 'HRV Ventilation', 'other_features']

    scraper = Commercial_Scraper_444_Rent(BASE_URL, CSV_FILE, CSV_HEADERS)
    data = scraper.get_commercial_list()
    scraper.write_to_csv(data) 
    
    