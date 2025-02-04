from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

def search(driver, date):
    """
    Date in mm/dd/yyyy
    """
    driver.get("https://merolagani.com/Floorsheet.aspx")
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/form/div[4]/div[4]/div/div/div[1]/div[4]/input"))
    )
    date_input = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[4]/div/div/div[1]/div[4]/input')
    search_btn = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[4]/div/div/div[2]/a[1]')
    date_input.send_keys(date)
    search_btn.click()
    if driver.find_elements(By.XPATH, "//*[contains(text(), 'Could not find floorsheet matching the search criteria')]"):
        print("No data found for the given search.")
        print("Script Aborted")
        driver.close()
        sys.exit()

def get_page_table(driver, table_class):
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/form/div[4]/div[5]/div/div[4]/table"))
    )
    soup = BeautifulSoup(driver.page_source,'html.parser')
    table = soup.find("table", {"class":table_class})
    tab_data = [[cell.text.replace('\r', '').replace('\n', '') for cell in row.find_all(["th","td"])]
                        for row in table.find_all("tr")]
    df = pd.DataFrame(tab_data)
    return df

def scrape_data(driver, date):
    search(driver, date = date)
    df = pd.DataFrame()
    count = 0
    while True:
        count += 1
        print(f"Scraping page {count}")
        page_table_df = get_page_table(driver, table_class="table table-bordered table-striped table-hover sortable")
        df = df.append(page_table_df, ignore_index = True)
        try:
            next_btn = driver.find_element(By.LINK_TEXT, 'Next')
            driver.execute_script("arguments[0].click();", next_btn)
        except NoSuchElementException:
            break
    driver.close()
    return df

def clean_df(df):
    new_df = df.drop_duplicates(keep='first') # Dropping Duplicates
    new_header = new_df.iloc[0] # grabing the first row for the header
    new_df = new_df[1:] # taking the data lower than the header row
    new_df.columns = new_header # setting the header row as the df header
    new_df.drop(["#"], axis=1, inplace=True)
    new_df["Rate"] = new_df["Rate"].apply(lambda x:float(x.replace(",", ""))) # Convert Rate to Float
    new_df["Amount"] = new_df["Amount"].apply(lambda x:float(x.replace(",", ""))) # Convert Amount to Float
    return new_df

def main():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options) # Start Browser
    driver.set_page_load_timeout(240)
    date = datetime.today().strftime('%m/%d/%Y') # Get today's date
    search(driver, date) # Search the webpage
    df = scrape_data(driver, date) # Scraping
    final_df = clean_df(df) # Cleaning
    file_name = date.replace("/", "_")
    final_df.to_csv(f"data/{file_name}.csv", index=False) # Save file

if __name__ == "__main__":
    main()
