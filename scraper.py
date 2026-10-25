import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
BASE_URL = "https://www.etenders.gov.za/Home/opportunities?id=1"
PROVINCES = ["Gauteng", "North West"]
KEYWORDS = ['stationery', 'consumables', 'hardware', 'refreshments', 'cleaning', 'ppe', 'groceries', 'supply and delivery']
PRIORITY_KEYWORDS = ['RFQ', 'Panel of suppliers', 'Supply and Delivery']
OUTPUT_FILE = "tenders.csv"

def scrape_tenders():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    all_matching_tenders = []

    try:
        for province in PROVINCES:
            print(f"Searching in {province}...")
            driver.get(BASE_URL)
            
            # Wait for the province dropdown to be present
            wait = WebDriverWait(driver, 10)
            province_select_el = wait.until(EC.presence_of_element_located((By.ID, "provincelist")))
            
            # Select province using JavaScript to avoid ElementNotInteractableException
            driver.execute_script(f'''
                const select = document.getElementById("provincelist");
                const option = Array.from(select.options).find(o => o.text === "{province}");
                if (option) {{
                    select.value = option.value;
                    select.dispatchEvent(new Event("change", {{ bubbles: true }}));
                }}
            ''')
            
            # Click Filter button
            filter_btn = driver.find_element(By.ID, "btnFilter")
            driver.execute_script("arguments[0].click();", filter_btn)
            
            # Wait for the table to populate with actual content
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr td")) > 0 and 
                              d.find_elements(By.CSS_SELECTOR, "table tbody tr td")[0].text.strip() != ""
                )
            except:
                print("Timeout waiting for table content to load.")
            
            # Scrape all available rows on current and subsequent pages
            page_num = 1
            while True:
                print(f"Scraping page {page_num} for {province}...")
                
                # Use JS to extract data to avoid empty text issues
                data = driver.execute_script('''
                    return Array.from(document.querySelectorAll("table tbody tr")).map(row => {
                        const cols = row.querySelectorAll("td");
                        return {
                            title: cols[2] ? cols[2].innerText.trim() : "",
                            closingDate: cols[5] ? cols[5].innerText.trim() : ""
                        };
                    });
                ''')
                
                for item in data:
                    title = item['title']
                    closing_date = item['closingDate']
                    if not title: continue
                    
                    print(f"DEBUG: Found tender: {title}")
                    title_lower = title.lower()
                    
                    if any(k.lower() in title_lower for k in KEYWORDS):
                        priority = "Low"
                        if any(p.lower() in title_lower for p in PRIORITY_KEYWORDS):
                            priority = "High"
                        
                        all_matching_tenders.append({
                            "Province": province,
                            "Title": title,
                            "Closing Date": closing_date,
                            "Priority": priority
                        })
                
                try:
                    next_btn = driver.find_element(By.ID, "tendeList_next")
                    if not next_btn.is_displayed() or "disabled" in next_btn.get_attribute("class"):
                        break
                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(5)
                    page_num += 1
                except:
                    break
                    
    finally:
        driver.quit()

    # Save to CSV
    if all_matching_tenders:
        print("\n--- First 5 Local Matches ---")
        for t in all_matching_tenders[:5]:
            print(f"[{t['Priority']}] {t['Province']}: {t['Title']}")
        print("----------------------------\n")
        
        keys = all_matching_tenders[0].keys()
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_matching_tenders)
        print(f"Successfully saved {len(all_matching_tenders)} tenders to {OUTPUT_FILE}")
    else:
        print("No matching tenders found.")

if __name__ == "__main__":
    scrape_tenders()
