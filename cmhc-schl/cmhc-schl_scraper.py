import csv
import pandas as pd
from openpyxl import Workbook

class CMHC_SCHL_Scraper:
    """A class to scrape apartment data from a website and write it to a CSV file."""

    def __init__(self, csv_file, csv_file_output):
        """
        Initialize the ApartmentScraper object.

        Parameters:
            base_url (str): The base URL of the website to scrape.
            csv_file (str): The name of the CSV file to write the data to.
            csv_headers (list): A list containing the headers for the CSV file.
        """
        self.csv_file = csv_file
        self.csv_file_output = csv_file_output

    def get_data_list(self):
        total_data = {}

        sheets = pd.ExcelFile(self.csv_file).sheet_names[1:]
        for sheet in sheets:
            sheet_data = []
            data = pd.read_excel(self.csv_file, sheet_name=sheet)

            if sheet == "Table 1.0":
                for index, row in data.iterrows():
                    if index == 4:
                        parent_header = row.tolist()
                        sheet_data.append(parent_header)

                    if index == 5:
                        header = row.tolist()
                        sheet_data.append(header)

                    if index > 5 and index < 61:
                        data = row.tolist()
                        for val in data:
                            if "Halifax" in str(val):
                                sheet_data.append(data)

                total_data[sheet] = sheet_data

            if sheet == "Table 4.1":
                for index, row in data.iterrows():
                    if index == 4:
                        parent_header = row.tolist()
                        sheet_data.append(parent_header)

                    if index == 5:
                        header = row.tolist()
                        sheet_data.append(header)

                    if index > 5 and index < 24:
                        data = row.tolist()
                        for val in data:
                            if "Halifax" in str(val):
                                sheet_data.append(data)

                total_data[sheet] = sheet_data

            if sheet == "Table 4.2":
                for index, row in data.iterrows():
                    if index == 4:
                        parent_header = row.tolist()
                        sheet_data.append(parent_header)

                    if index == 5:
                        header = row.tolist()
                        sheet_data.append(header)

                    if index > 5 and index < 24:
                        data = row.tolist()
                        for val in data:
                            if "Halifax" in str(val):
                                sheet_data.append(data)

                total_data[sheet] = sheet_data

            if sheet == "Table 5.0":
                for index, row in data.iterrows():
                    if index == 14:
                        parent_header = row.tolist()
                        sheet_data.append(parent_header)

                    if index > 14 and index < 70:
                        data = row.tolist()
                        for val in data:
                            if "Halifax" in str(val):
                                sheet_data.append(data)

                total_data[sheet] = sheet_data

            if sheet == "Table 6.0":
                for index, row in data.iterrows():
                    if index == 5:
                        parent_header = row.tolist()
                        sheet_data.append(parent_header)

                    if index == 6:
                        sub_header = row.tolist()
                        sheet_data.append(sub_header)

                    if index == 7:
                        child_header = row.tolist()
                        sheet_data.append(child_header)

                    if index > 7 and index < 64:
                        data = row.tolist()
                        for val in data:
                            if "Halifax" in str(val):
                                sheet_data.append(data)

                total_data[sheet] = sheet_data
            
            if sheet == "Table 6.1":
                for index, row in data.iterrows():
                    if index == 5:
                        parent_header = row.tolist()
                        sheet_data.append(parent_header)

                    if index == 6:
                        sub_header = row.tolist()
                        sheet_data.append(sub_header)

                    if index == 7:
                        child_header = row.tolist()
                        sheet_data.append(child_header)

                    if index > 7 and index < 63:
                        data = row.tolist()
                        for val in data:
                            if "Halifax" in str(val):
                                sheet_data.append(data)

                total_data[sheet] = sheet_data

        return total_data
    

    def create_excel_file(self, sheet_data):
        wb = Workbook()
        
        for sheet_name, data in sheet_data.items():
            ws = wb.create_sheet(title=sheet_name)
            
            for row in data:
                ws.append(row)
        
        wb.save(self.csv_file_output)

if __name__ == '__main__':
    CSV_FILE = 'cmhc-schl.xlsx'
    CSV_FILE_OUTPUT = 'cmhc-schl-output.xlsx'

    scraper = CMHC_SCHL_Scraper(CSV_FILE, CSV_FILE_OUTPUT)
    data = scraper.get_data_list()
    scraper.create_excel_file(data) 