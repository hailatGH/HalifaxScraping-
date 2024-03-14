from .apartment_scraper_444_rent import Apartment_Scraper_444_Rent

if __name__ == '__main__':
    BASE_URL = "https://www.444rent.com"
    CSV_FILE = '444rent.csv'
    CSV_HEADERS = ['building', 'unit', 'location', 'area', 'price', 'type', 'address', 'resident_managers', 'tel', 'fax', 'website', 'email', 'lease', 'included', 'not included', 'parking', 'storage', 'Fridge', 'Ceiling Height', 'underground', 'Flooring', 'HRV Ventilation', 'Bathroom', 'floors', 'Appliances', 'Balcony Size', 'policy', 'Kitchen', 'deposit', 'heated underground', 'other_features']

    scraper = Apartment_Scraper_444_Rent(BASE_URL, CSV_FILE, CSV_HEADERS)
    data = scraper.get_apartment_list()
    scraper.write_to_csv(data) 