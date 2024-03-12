import requests
import csv
from bs4 import BeautifulSoup


class ApartmentScraper:
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
            list: A list of lists containing apartment data.
        """
        # Get HTML content of the webpage
        web_html_text = requests.get(
            f'{self.base_url}/apartments.asp').text
        soup = BeautifulSoup(web_html_text, 'lxml')

        apartments_list = []
        # Find all apartment rows with specified background colors
        apartments = soup.find_all('tr', bgcolor=["#ffffff", "#e5e4e4"])
        for apartment in apartments:
            apartment_list = ['' for _ in self.csv_headers]
            # Split apartment text and clean it
            apartment_text = apartment.text.replace(
                '  ', '').replace('\t', '').replace('\n\n', '\n').split('\n')
            apartment_text = [value.replace('\r', '').replace(
                '\xa0', '') for value in apartment_text if value.strip()]
            # Check if apartment is in Halifax
            if "Halifax" in apartment_text[2]:
                # Extract relevant apartment information
                apartment_list[0] = apartment_text[0]
                apartment_list[3] = apartment_text[1]
                apartment_list[9] = apartment_text[3]
                apartment_list[10] = apartment_text[2].replace('Halifax ', '')
                link = apartment.find('td').a['href']
                detail_html_text = requests.get(
                    f'{self.base_url}/{link}').text
                detail_soup = BeautifulSoup(detail_html_text, 'lxml')
                location = detail_soup.find(
                    'td', align='left', style='padding-left:4px;').text.replace('\n\n', '\n').replace('\t', '').strip().split('\n')
                location = [value.replace('\r', '').replace(
                    '\xa0', ' ') for value in location if value.strip()]
                apartment_list[1] = location[0] + " " + location[1]
                tab_content = detail_soup.find(
                    'div', id='tab4', class_='tab_content').find('table').tr.td.find_all('table')
                for content in tab_content:
                    tds = content.tr.find_all('td')
                    for td in tds:
                        td_text = td.text
                        if "Unit is on floor" in td_text:
                            apartment_list[2] = td_text.split()[-2]
                apartments_list.append(apartment_list)
        return apartments_list

    def write_to_csv(self, data):
        """
        Write apartment data to a CSV file.

        Parameters:
            data (list): A list of lists containing apartment data.
        """
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.csv_headers)
            for row in data:
                writer.writerow(row)


if __name__ == '__main__':
    BASE_URL = "https://www.444rent.com"
    CSV_FILE = 'data.csv'
    CSV_HEADERS = ["Property Name", "Civic Address", "Floors", "Units", "Developer",
                   "Proposed/ Under Development/ Completed", "Website", "Condo or Rental",
                   "Estimated Time of Completion", "Retail Square Footage", "District", "Image"]

    scraper = ApartmentScraper(BASE_URL, CSV_FILE, CSV_HEADERS)
    data = scraper.get_apartment_list()
    scraper.write_to_csv(data)
