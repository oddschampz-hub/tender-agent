from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    url = "https://www.etenders.gov.za/Home/opportunities?id=1"
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
    
    js_script = """
    const row = document.querySelector("table tbody tr");
    if (!row) return "No row";
    return row.innerHTML;
    """
    html = driver.execute_script(js_script)
    print(f"Row HTML: {html}")

finally:
    driver.quit()
