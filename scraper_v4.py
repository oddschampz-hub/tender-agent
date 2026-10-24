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
        time.sleep(3)
        
        # In DataTables, the child row is a separate <tr> inserted after the parent
        # Use JS to find the next sibling that is a <tr>
        content_text = driver.execute_script('''
            var row = arguments[0];
            var child = row.nextElementSibling;
            return child ? child.innerText : "No child row found";
        ''', row)
        
        # Extract PDF links from that same child row
        links_data = driver.execute_script('''
            var row = arguments[0];
            var child = row.nextElementSibling;
            if (!child) return [];
            var links = Array.from(child.querySelectorAll("a"));
            return links.map(a => ({text: a.innerText, href: a.href}))
                        .filter(l => l.href.toLowerCase().includes(".pdf") || l.href.toLowerCase().includes("download"));
        ''', row)
        
        docs = [f"{l['text'].strip()} ({l['href']})" for l in links_data]

        return {
            "raw_details": content_text,
            "documents": " | ".join(docs) if docs else "None"
        }
    except Exception as e:
        return {"raw_details": f"Error: {str(e)}", "documents": "None"}

def scrape_tenders():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    all_matching_tenders = []

    try:
        for province in PROVINCES:
            print(f"Searching in {province}...")
            driver.get(BASE_URL)
            
            wait = WebDriverWait(driver, 15)
            province_select_el = wait.until(EC.presence_of_element_located((By.ID, "provincelist")))
            
            # Use a simpler JS trigger for the dropdown
            driver.execute_script(f'''
                var select = document.getElementById("provincelist");
                var option = Array.from(select.options).find(o => o.text === "{province}");
                if (option) {{
                    select.value = option.value;
                    select.dispatchEvent(new Event("change", {{ bubbles: true }}));
                }}
            ''')
            
            filter_btn = driver.find_element(By.ID, "btnFilter")
            driver.execute_script("arguments[0].click();", filter_btn)
            
            # Wait for the table to update. We look for a row that contains a known province or just a basic table row
            try:
                wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr td")) > 0)
                time.sleep(5) # Extra buffer for AJAX
            except:
                print(f"Timeout waiting for table content for {province}")
                continue
            
            page_num = 1
            while True:
                print(f"Scraping page {page_num} for {province}...")
                
                # Target only the main rows (those with the expand button)
                main_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td.details-control")
                
                # To avoid stale element exceptions, we get the count and iterate by index or re-find
                row_count = len(main_rows)
                for i in range(row_count):
                    # Re-find elements each time to prevent stale element errors after expanding/collapsing
                    current_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    # Filter for the main rows (the ones that have the expand button in the first cell)
                    valid_rows = [r for r in current_rows if r.find_elements(By.CSS_SELECTOR, "td.details-control")]
                    
                    if i >= len(valid_rows): break
                    row = valid_rows[i]
                    
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) < 6: continue
                    
                    title = cols[2].text.strip()
                    closing_date = cols[4].text.strip() if len(cols) > 4 else "N/A"
                    
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
                        # Collapse the row back
                        driver.execute_script("arguments[0].click();", row.find_element(By.CSS_SELECTOR, "td.details-control"))
                
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
