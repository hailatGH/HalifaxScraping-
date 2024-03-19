import time, csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

browser = webdriver.Chrome()

browser.get('https://public.tableau.com/views/RenterHouseholds21CSD/CRHI_RenterHouseholds?:embed=y&&:showVizHome=n&:tabs=n&showShareOptions=true&:apiID=host0#navType=1&navSrc=Parse')

tabComboBoxButton = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'tabComboBoxButton')))
tabComboBoxButton.click()

britishColumbia = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, 'FI_federated.1q7wp8v03tgzs01ayah960u2wsjl,none:province_code:nk1404768988825249081_17797799621814179364_1')))
britishColumbia_input_element = britishColumbia.find_element(By.XPATH, "./div/input")
britishColumbia_input_element.click()

novaSoctia = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, 'FI_federated.1q7wp8v03tgzs01ayah960u2wsjl,none:province_code:nk1404768988825249081_17797799621814179364_6')))
novaSoctia_input_element = novaSoctia.find_element(By.XPATH, "./div/input")
novaSoctia_input_element.click()

action = ActionChains(browser)
action.move_by_offset(0, 0)
action.click()
action.perform()

tabZoneId53 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'tabZoneId53')))
tabComboBoxButton = WebDriverWait(tabZoneId53, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'tabComboBoxButton')))
tabComboBoxButton.click()

halfix_wraper = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'tableau_base_widget_LegacyCategoricalQuickFilter_1_menu')))
halfix = WebDriverWait(halfix_wraper, 10).until(EC.presence_of_element_located((By.ID, 'FI_federated.1q7wp8v03tgzs01ayah960u2wsjl,province_code &amp; Name (Combined)1404768988825249081_17797799621814179364_12')))
halfix_input_element = halfix.find_element(By.XPATH, "./div/input")
halfix_input_element.click()

action = ActionChains(browser)
action.move_by_offset(0, 0)
action.click()
action.perform()

time.sleep(5)

tabZoneId49 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'tabZoneId49')))

text_value = tabZoneId49.text
text = text_value.split('\n')
text = text[1:text.index('Studio')]

data_list = [['Province', 'Name', 'Household Income Range', 'Quartile', 'Average Income']]

province = []
name = []
household_income_range = []
quartile = []
average_income = []

for index, val in enumerate(text):
    if index == 0:
        province.append(val)
    
    if index == 1:
        name.append(val)

    if ("$" in val and "to" in val) or ("$" in val and  "+" in val):
        household_income_range.append(val)
    elif "Q" in val:
        quartile.append(val)
    elif ("$" in val ) and "+" not in val and "to" not in val:
        average_income.append(val)

count = 0
while True:
    data = []

    if (count >= len(province) and count >= len(name) and count >= len(household_income_range) and count >= len(quartile) and count >= len(average_income)):
        break

    if count < len(province):
        data.append(province[count])
    else: 
        data.append("-")
        
    if count < len(name):
        data.append(name[count])
    else: 
        data.append("-")

    if count < len(household_income_range):
        data.append(household_income_range[count])
    else: 
        data.append("-")

    if count < len(quartile):
        data.append(quartile[count])
    else: 
        data.append("-")

    if count < len(average_income):
        data.append(average_income[count])
    else: 
        data.append("-")

    data_list.append(data)
    count = count + 1

with open("regional_districts.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data_list)