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
    const rows = document.querySelectorAll("table tbody tr");
    if (rows.length > 0) {
        const cols = rows[0].querySelectorAll("td");
        if (cols.length > 2) {
            const link = cols[2].querySelector("a");
            return link ? link.href : "No link in 3rd col";
        }
    }
    return "No rows or cols found";
    """
    link = driver.execute_script(js_script)
    print(f"Result: {link}")
    
    if link and link.startswith('http'):
        driver.get(link)
        print("--- PAGE SOURCE ---")
        print(driver.page_source[:30000])
        print("--- END PAGE SOURCE ---")

finally:
    driver.quit()
