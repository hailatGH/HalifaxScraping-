import requests
import csv
from bs4 import BeautifulSoup


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
            list: A list of lists containing apartment data.
        """
        total_apartments = []
        web_html_text = requests.get(f'{self.base_url}/apartments.asp').text
        soup = BeautifulSoup(web_html_text, 'lxml')

        sections =  soup.find_all('table', width="100%", border="0", cellpadding="0", cellspacing="0", bgcolor="#ffffff")

        for section in sections:
            type = section.find('font', color="#FFFFFF").b.text
            section_apartments = section.find_all('tr', bgcolor=["#ffffff", "#e5e4e4"])
            
            for section_apartment in section_apartments:
                apartment = {}
                link = section_apartment.find('td').a['href']

                section_apartment = section_apartment.text.replace('  ', '').replace('\t', '').replace('\n\n', '\n').split('\n')
                section_apartment = [value.replace('\r', '').replace('\xa0', '') for value in section_apartment if value.strip()]

                if 'Halifax' in section_apartment[2]:

                    apartment['building'] = section_apartment[0]
                    apartment['unit'] = section_apartment[1]
                    apartment['location'] = section_apartment[2]
                    apartment['area'] = section_apartment[3]
                    apartment['price'] = section_apartment[4]
                    apartment['type'] = type

                    detail_html_text = requests.get(f'{self.base_url}/{link}').text
                    detail_soup = BeautifulSoup(detail_html_text, 'lxml')

                    right_section = detail_soup.find('td', style="padding-left:14px;", valign="top", align="left", width="52%")

                    address = right_section.find('td', align='left', style='padding-left:4px;').text.replace('\n\n', '\n').replace('\t', '').strip().split('\n')
                    address = [value.replace('\r', '').replace('\xa0', ' ') for value in address if value.strip()]
                    apartment['address'] = address[0] + address[1]

                    managers_info = right_section.find('div', style="margin-left:5px;margin-top:20px;").text.replace('  ','').replace('\t','').replace('\n\n','\n').split('\n')
                    managers_info = [value.replace('\r', '').replace('\xa0', '').replace('|','') for value in managers_info if value.strip()] 
                    managers_info = [value for value in managers_info if value not in ['RESIDENT MANAGERS', 'tel', 'fax', 'Website']]
                    if len(managers_info) == 5:
                        apartment['resident_managers'] = managers_info[0]
                        apartment['tel'] = managers_info[1]
                        apartment['fax'] = managers_info[2]
                        apartment['website'] = managers_info[3]
                        apartment['email'] = managers_info[4]

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

                    total_apartments.append(apartment)

        return total_apartments

    def write_to_csv(self, datas):
        """
        Write apartment data to a CSV file.

        Parameters:
            data (list): A list of lists containing apartment data.
        """
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)
            writer.writeheader()
            for data in datas:
                row = {header: data.get(header, None) for header in self.csv_headers}
                writer.writerow(row)