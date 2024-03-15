import requests
import csv
from bs4 import BeautifulSoup

class Parking_Scraper_444_Rent:
    """A class to scrape parking data from a website and write it to a CSV file."""

    def __init__(self, base_url, csv_file, csv_headers):
        """
        Initialize the ParkingScraper object.

        Parameters:
            base_url (str): The base URL of the website to scrape.
            csv_file (str): The name of the CSV file to write the data to.
            csv_headers (list): A list containing the headers for the CSV file.
        """
        self.base_url = base_url
        self.csv_file = csv_file
        self.csv_headers = csv_headers

    def get_parking_list(self):
        """
        Scrape parking data from the website.

        Returns:
            list: A list of dictionaries containing parking data.
        """
        total_parkings = []
        web_html_text = self.fetch_html_text(f'{self.base_url}/parking.asp')
        soup = BeautifulSoup(web_html_text, 'lxml')
        parkings = soup.find('table', width="100%", border="0", cellpadding="7", bgcolor="#ffffff").find_all('tr', bgcolor=['#e5e4e4', '#ffffff'])
        
        for parking_row in parkings:
            parking = self.extract_parking_data(parking_row)
            total_parkings.append(parking)

        return total_parkings

    def fetch_html_text(self, url):
        """Fetch HTML text from the provided URL."""
        return requests.get(url).text

    def extract_parking_data(self, parking_row):
        """Extract parking data from the HTML row."""
        parking = {}
        link = parking_row['onclick'].replace("parent.location=","").replace("'","").replace(";","")
        parking_row = parking_row.text.replace('  ', '').replace('\t', '').replace('\n\n', '\n').split('\n')
        parking_row = [value.replace('\r', '').replace('\xa0', '') for value in parking_row if value.strip()]

        parking['address'] = parking_row[0]
        parking['type'] = parking_row[1]
        parking['parking'] = parking_row[2]
        parking['available'] = parking_row[3]
        parking['price'] = parking_row[4]

        detail_html_text = self.fetch_html_text(f'{self.base_url}/{link}')
        detail_soup = BeautifulSoup(detail_html_text, 'lxml')
        right_section = detail_soup.find('td', style="padding-left:14px;", valign="top", align="left", width="52%")

        address = right_section.find('td', align='left', style='padding-left:4px;').text.replace('\n\n', '\n').replace('\t', '').strip().split('\n')
        address = [value.replace('\r', '').replace('\xa0', ' ') for value in address if value.strip()]
        parking['address'] = (address[0] + " " + address[1]) if len(address) > 3 else parking['address']

        managers_info = right_section.find('div', style="margin-left:5px;margin-top:20px;").text.replace('  ','').replace('\t','').replace('\n\n','\n').split('\n')
        managers_info = [value.replace('\r', '').replace('\xa0', '').replace('|','') for value in managers_info if value.strip()]

        for index, info in enumerate(managers_info):
            if "MANAGER" in info or "COORDINATOR" in info:
               parking[info] = managers_info[0]
            elif "@" in info:
                parking['email'] = info
            elif "Website" in info:
                parking['Website'] = managers_info[index + 1]
            elif "tel" in info:
                parking['tel'] = managers_info[index + 1]
            elif "fax" in info:
                parking['fax'] = managers_info[index + 1]

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

            parking[key] = value

        return parking

    def write_to_csv(self, datas):
        """
        Write parking data to a CSV file.

        Parameters:
            data (list): A list of dictionaries containing parking data.
        """
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)
            writer.writeheader()
            for data in datas:
                row = {header: data.get(header, None) for header in self.csv_headers}
                writer.writerow(row)



if __name__ == '__main__':
    BASE_URL = "https://www.444rent.com"
    CSV_FILE = 'parking_444_rent.csv'
    CSV_HEADERS = ['address', 'type', 'parking', 'available', 'price', 'TENANT SERVICES COORDINATOR', 'RESIDENT MANAGERS', 'COMMERCIAL PROPERTY MANAGER', 'email', 'Website', 'tel', 'fax', 'term', 'termination policy', 'rate', 'deposit']

    scraper = Parking_Scraper_444_Rent(BASE_URL, CSV_FILE, CSV_HEADERS)
    data = scraper.get_parking_list()
    scraper.write_to_csv(data) 