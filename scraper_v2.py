import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
BASE_URL = "https://www.etenders.gov.za/Home/opportunities?id=1"
PROVINCES = ["Gauteng", "North West"]
KEYWORDS = ['stationery', 'consumables', 'hardware', 'refreshments', 'cleaning', 'ppe', 'groceries', 'supply and delivery']
PRIORITY_KEYWORDS = ['RFQ', 'Panel of suppliers', 'Supply and Delivery']
OUTPUT_FILE = "C:/TenderAgent/tenders.csv"

def extract_detail_info(driver, row):
    """Expands a row and extracts detailed information from the expanded content."""
    try:
        expand_btn = row.find_element(By.CSS_SELECTOR, "td.details-control")
        driver.execute_script("arguments[0].click();", expand_btn)
        time.sleep(2)
        
        # The expanded content is usually in the immediate next row
        parent_row = row.find_element(By.XPATH, "..")
        expanded_row = parent_row.find_element(By.XPATH, "following-sibling::tr[1]")
        content_text = expanded_row.text
        
        links = expanded_row.find_elements(By.TAG_NAME, "a")
        docs = []
        for link in links:
            href = link.get_attribute("href")
            if href and (".pdf" in href.lower() or "download" in href.lower()):
                docs.append(f"{link.text.strip()} ({href})")

        return {
            "raw_details": content_text,
            "documents": " | ".join(docs) if docs else "None"
        }
    except Exception as e:
        return {"raw_details": "No details available", "documents": "None"}

def scrape_tenders():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    all_matching_tenders = []

    try:
        for province in PROVINCES:
            print(f"Searching in {province}...")
            driver.get(BASE_URL)
            
            wait = WebDriverWait(driver, 10)
            province_select_el = wait.until(EC.presence_of_element_located((By.ID, "provincelist")))
            
            driver.execute_script(f'''
                const select = document.getElementById("provincelist");
                const option = Array.from(select.options).find(o => o.text === "{province}");
                if (option) {{
                    select.value = option.value;
                    select.dispatchEvent(new Event("change", {{ bubbles: true }}));
                }}
            ''')
            
            filter_btn = driver.find_element(By.ID, "btnFilter")
            driver.execute_script("arguments[0].click();", filter_btn)
            
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr td")) > 0 and 
                              d.find_elements(By.CSS_SELECTOR, "table tbody tr td")[0].text.strip() != ""
                )
            except:
                print("Timeout waiting for table content to load.")
            
            page_num = 1
            while True:
                print(f"Scraping page {page_num} for {province}...")
                
                # Find only main rows (exclude the expanded child rows)
                rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr:not(.dt-hasFold)")
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) < 6: continue
                    
                    title = cols[2].text.strip()
                    closing_date = cols[4].text.strip()
                    
                    if not title: continue
                    
                    title_lower = title.lower()
                    if any(k.lower() in title_lower for k in KEYWORDS):
                        priority = "Low"
                        if any(p.lower() in title_lower for p in PRIORITY_KEYWORDS):
                            priority = "High"
                        
                        print(f"Extracting details for: {title}")
                        details = extract_detail_info(driver, row)
                        
                        all_matching_tenders.append({
                            "Title": title,
                            "Province": province,
                            "Closing Date": closing_date,
                            "Priority": priority,
                            "Raw Details": details["raw_details"],
                            "Documents": details["documents"]
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

    if all_matching_tenders:
        keys = all_matching_tenders[0].keys()
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_matching_tenders)
        print(f"Successfully saved {len(all_matching_tenders)} detailed tenders to {OUTPUT_FILE}")
        return all_matching_tenders
    else:
        print("No matching tenders found.")
        return []

if __name__ == "__main__":
    scrape_tenders()
