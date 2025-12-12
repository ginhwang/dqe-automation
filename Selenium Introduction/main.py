import time
import os
import pandas as pd
import base64

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from itertools import product



class SeleniumWebDriverContextManager:
    def __init__(self):
        self.driver = None

    def __enter__(self):
        self.driver = webdriver.Chrome()
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()

def extract_table_to_csv(driver, file_path):
    driver.get(f"file://{file_path}")
    driver.implicitly_wait(10)

    columns = driver.find_elements(By.CSS_SELECTOR, 'g.column-block[id^="cells"]')
    if not columns:
        print("Could not find columns")
        return
    else:
        print(f"Found {len(columns)} columns")

    # extract text for columns
    col_data = []
    for idx, col in enumerate(columns):
        texts = col.find_elements(By.XPATH, './/*[local-name()="text" and contains(@class, "cell-text")]')
        column_values = [t.text for t in texts]
        col_data.append(column_values)

    print(f"col_data (all columns): {col_data}")

    # find headers
    header_names = []
    header_blocks = driver.find_elements(By.TAG_NAME, 'g')
    for block in header_blocks:
        if block.get_attribute('id') == 'header':
            headers = block.find_elements(By.TAG_NAME, 'text')
            for h in headers:
                if 'cell-text' in h.get_attribute('class'):
                    header_names.append(h.text)
    print(f"Headers: {header_names}")

    n_fields = len(header_names)
    if len(col_data) % n_fields != 0:
        print("Column count does not match header count, cannot proceed.")
        return

    cols_per_field = len(col_data) // n_fields
    grouped_cols = []
    for i in range(n_fields):
        combined = []
        for j in range(cols_per_field):
            combined.extend(col_data[i * cols_per_field + j])
        grouped_cols.append(combined)

    min_len = min(len(col) for col in grouped_cols)
    if min_len == 0:
        print("One of the columns is empty, cannot proceed.")
        return

    truncated_cols = [col[:min_len] for col in grouped_cols]
    rows = list(zip(*truncated_cols))
    df = pd.DataFrame(rows, columns=header_names)
    df.to_csv("table.csv", index=False)
    print("Saved table.csv")

def extract_doughnut_chart_with_filtering(driver, file_path):
    driver.get(f"file://{file_path}")
    driver.implicitly_wait(10)
    action = ActionChains(driver)

    # Initial extraction (default state)
    extract_doughnut_chart_data_screenshot(driver, file_path, 0)
    print('Default legend state extracted')

    items_count = len(driver.find_elements(By.CSS_SELECTOR, 'g.groups > g.traces'))

    for indx in range(items_count):
        # Re-find items after each refresh
        items_for_filter = driver.find_elements(By.CSS_SELECTOR, 'g.groups > g.traces')
        item = items_for_filter[indx]

        # Wait for item to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'g.groups > g.traces')))
        

        # Find the toggle inside the trace group
        toggle = item.find_element(By.CSS_SELECTOR, 'rect.legendtoggle')
        item.click()
        time.sleep(5)
        print(f'Legend item {indx} clicked')

        extract_doughnut_chart_data_screenshot(driver, file_path, indx+1)

        # Refresh for next iteration
        driver.refresh()
        driver.implicitly_wait(10)

    driver.refresh()
    driver.implicitly_wait(10)

    for indx in range(items_count):
        # Re-find items after each refresh
        items_for_filter = driver.find_elements(By.CSS_SELECTOR, 'g.groups > g.traces')
        item = items_for_filter[indx]

        # Wait for item to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'g.groups > g.traces')))
        

        # Find the toggle inside the trace group
        toggle = item.find_element(By.CSS_SELECTOR, 'rect.legendtoggle')
        item.click()
        time.sleep(5)
        print(f'Legend item {indx} clicked')

    second_items_count = items_count+1
    extract_doughnut_chart_data_screenshot(driver, file_path, second_items_count )
    
    driver.refresh()
    driver.implicitly_wait(10)

    for indx in range(items_count):
        # Re-find items after each refresh
        items_for_filter = driver.find_elements(By.CSS_SELECTOR, 'g.groups > g.traces')
        item = items_for_filter[indx]

        # Wait for item to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'g.groups > g.traces')))
        

        # Find the toggle inside the trace group
        toggle = item.find_element(By.CSS_SELECTOR, 'rect.legendtoggle')
        action.double_click(on_element=item).perform()
        time.sleep(5)
        print(f'Legend item {indx} clicked')

        extract_doughnut_chart_data_screenshot(driver, file_path, second_items_count+ indx+1)

        # Refresh for next iteration
        driver.refresh()
        driver.implicitly_wait(10)



def extract_doughnut_chart_data_screenshot(driver, file_path, n):
    filename = f'doughnut{n}.csv'
    screenshotname = f'screenshot{n}.png'
    data = []
    
    slice_texts = driver.find_elements(By.CSS_SELECTOR, 'g.pielayer g.slice g.slicetext text.slicetext')
    for st in slice_texts:
        lines = st.find_elements(By.TAG_NAME, 'tspan')
        if len(lines) >= 2:
            label = lines[0].text.strip()
            value = lines[1].text.strip()
            data.append([label, value])
    if not data:
        legend_labels = driver.find_elements(By.CSS_SELECTOR, 'g.legend text.legendtext')
        for label in legend_labels:
            data.append([label.text.strip(), ""])
    import pandas as pd
    df = pd.DataFrame(data, columns=["Facility Type", "Min Average Time Spent"])
    df.to_csv(filename, index=False)
    print(f"Saved {filename}")

    driver.save_screenshot(screenshotname)
    print(f"Saved {screenshotname}")



if __name__ == "__main__":
    file_path = os.path.abspath("Selenium Introduction/report.html")
    with SeleniumWebDriverContextManager() as driver:
        # Open the HTML report
        driver.get(f"file://{file_path}")

        # Extract table to CSV
        extract_table_to_csv(driver, file_path)
        # Extract data from doughnut chart and take screenshots for all possible options
        extract_doughnut_chart_with_filtering(driver, file_path)
        