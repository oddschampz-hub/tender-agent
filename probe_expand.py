from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    url = "https://www.etenders.gov.za/Home/opportunities?id=1"
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
    
    # Click the expansion button of the first row
    expand_btn = driver.find_element(By.CSS_SELECTOR, "table tbody tr td.details-control")
    driver.execute_script("arguments[0].click();", expand_btn)
    
    # Wait for the child row to appear
    time.sleep(2)
    
    # The child row usually follows the parent row
    # Let's get all text from the expanded area
    expanded_content = driver.find_element(By.CSS_SELECTOR, "table tbody tr.dt-hasFold").find_element(By.CSS_SELECTOR, "td").text
    print(f"Expanded Content: {expanded_content}")
    
    # Also look for any links to a dedicated detail page
    links = driver.find_elements(By.TAG_NAME, "a")
    for l in links:
        print(f"Link: {l.text} -> {l.get_attribute('href')}")

finally:
    driver.quit()
