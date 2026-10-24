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
    
    expand_btn = driver.find_element(By.CSS_SELECTOR, "table tbody tr td.details-control")
    driver.execute_script("arguments[0].click();", expand_btn)
    
    time.sleep(3)
    
    print("--- BODY HTML ---")
    print(driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")[:20000])
    print("--- END BODY HTML ---")

finally:
    driver.quit()
