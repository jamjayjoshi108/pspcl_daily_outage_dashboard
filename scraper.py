#====================================================================================================================================
#====================================================================================================================================
V3
#====================================================================================================================================
#====================================================================================================================================
import time
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CLOUD CONFIGURATION ---
download_dir = os.getcwd() 

chrome_options = Options()
chrome_options.add_argument("--headless=new") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)

try:
    # ---------------------------------------------------------
    # STEPS 1-4: Login 
    # ---------------------------------------------------------
    driver.get("https://distribution.pspcl.in/returns/login.php")
    
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
    )
    username_field.send_keys("PDC / Jay Joshi")

    password_field = driver.find_element(By.CSS_SELECTOR, "#password")
    password_field.send_keys("pspcl123") 

    login_button = driver.find_element(By.XPATH, "//*[@id='bname_login']")
    login_button.click()

    # ---------------------------------------------------------
    # STEPS 5-7: Navigate to Outage Reports
    # ---------------------------------------------------------
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("leftFrame"))

    outage_management_btn = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='Outage_Management']//*[contains(text(), 'Outage Management')]"))
    )
    outage_management_btn.click()
    time.sleep(2) 

    supply_status_btn = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@title='Supply Status (Outage Report)']"))
    )
    supply_status_btn.click()

    driver.switch_to.default_content()
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))
    driver.switch_to.default_content()
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))
    driver.switch_to.default_content()
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))

    # ---------------------------------------------------------
    # STEP 8: Calculate All Date Ranges for Outages
    # ---------------------------------------------------------
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_minus_1 = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    today_minus_5 = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    
    try:
        last_year = today.replace(year=today.year - 1)
    except ValueError:
        last_year = today.replace(year=today.year - 1, day=28)
        
    ly_str = last_year.strftime("%Y-%m-%d")
    ly_minus_1 = (last_year - timedelta(days=1)).strftime("%Y-%m-%d")
    ly_minus_5 = (last_year - timedelta(days=5)).strftime("%Y-%m-%d")

    outage_ranges = [
        (today_str, today_str, f"{today_str}_Outages_Today.csv"),
        (today_minus_5, today_minus_1, f"{today_str}_Outages_Last_5_Days.csv"),
        (ly_str, ly_str, f"{ly_str}_Outages_Today_Last_Year.csv"),
        (ly_minus_5, ly_minus_1, f"{ly_str}_Outages_Last_5_Days_Last_Year.csv")
    ]

    # ---------------------------------------------------------
    # STEP 9: Loop and Download Outage Files
    # ---------------------------------------------------------
    for start_dt, end_dt, final_name in outage_ranges:
        print(f"\n--- Downloading Outages: {start_dt} to {end_dt} ---")
        
        start_date_elem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="startdate"]')))
        driver.execute_script(f"arguments[0].value = '{start_dt}';", start_date_elem)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", start_date_elem)

        end_date_elem = driver.find_element(By.XPATH, '//*[@id="enddate"]')
        driver.execute_script(f"arguments[0].value = '{end_dt}';", end_date_elem)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", end_date_elem)
        time.sleep(3) 

        input_file = os.path.join(download_dir, "export.csv")
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(os.path.join(download_dir, final_name)): os.remove(os.path.join(download_dir, final_name))

        WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, "//img[@title='Export to Spreadsheet']"))).click()

        timeout, elapsed = 120, 0
        while not os.path.exists(input_file) and elapsed < timeout:
            time.sleep(1)
            elapsed += 1
            
        if not os.path.exists(input_file): raise FileNotFoundError(f"Download timed out for {final_name}!")
        
        os.rename(input_file, os.path.join(download_dir, final_name))
        print(f"File saved: {final_name}")
        time.sleep(3) 

    # ---------------------------------------------------------
    # STEP 10: Navigate to PTW Requests
    # ---------------------------------------------------------
    print("\n--- Switching to PTW Extraction ---")
    driver.switch_to.default_content()
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("leftFrame"))
    
    view_ptw_btn = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@title='View PTW Requests']"))
    )
    view_ptw_btn.click()

    driver.switch_to.default_content()
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))

    # Rolling 7-day period for PTW (aligning with portal updates)
    ptw_to_date = today_str
    ptw_from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    ptw_filename = f"{today_str}_PTW_Last_7_Days.csv"

    print(f"PTW Cycle locked in! From: {ptw_from_date} To: {ptw_to_date}")

    from_date_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='fromdate']")))
    driver.execute_script(f"arguments[0].value = '{ptw_from_date}';", from_date_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", from_date_input)
    time.sleep(3) 

    to_date_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//*[@id='todate']")))
    driver.execute_script(f"arguments[0].value = '{ptw_to_date}';", to_date_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", to_date_input)
    time.sleep(3) 

    input_file = os.path.join(download_dir, "export.csv")
    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(os.path.join(download_dir, ptw_filename)): os.remove(os.path.join(download_dir, ptw_filename))

    download_btn = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//img[@title='Export to Spreadsheet']")))
    download_btn.click()
    
    timeout, elapsed = 120, 0
    while not os.path.exists(input_file) and elapsed < timeout:
        time.sleep(1)
        elapsed += 1
        
    if not os.path.exists(input_file): raise FileNotFoundError("PTW Download timed out!")
    
    os.rename(input_file, os.path.join(download_dir, ptw_filename))
    print(f"PTW File saved: {ptw_filename}")

finally:
    driver.quit()




#====================================================================================================================================
#====================================================================================================================================
V2
#====================================================================================================================================
#====================================================================================================================================

# import time
# import os
# from datetime import datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # --- CLOUD CONFIGURATION ---
# download_dir = os.getcwd() 

# chrome_options = Options()
# chrome_options.add_argument("--headless=new") 
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")

# prefs = {
#     "download.default_directory": download_dir,
#     "download.prompt_for_download": False,
#     "directory_upgrade": True
# }
# chrome_options.add_experimental_option("prefs", prefs)

# driver = webdriver.Chrome(options=chrome_options)

# try:
#     # ---------------------------------------------------------
#     # STEPS 1-4: Login (Only happens ONCE now)
#     # ---------------------------------------------------------
#     driver.get("https://distribution.pspcl.in/returns/login.php")
    
#     username_field = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
#     )
#     username_field.send_keys("PDC / Jay Joshi")

#     password_field = driver.find_element(By.CSS_SELECTOR, "#password")
#     password_field.send_keys("pspcl123") 

#     login_button = driver.find_element(By.XPATH, "//*[@id='bname_login']")
#     login_button.click()

#     # ---------------------------------------------------------
#     # STEPS 5-7: Navigate the iFrames (Only happens ONCE now)
#     # ---------------------------------------------------------
#     WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("leftFrame"))

#     outage_management_btn = WebDriverWait(driver, 60).until(
#         EC.element_to_be_clickable((By.XPATH, "//*[@id='Outage_Management']//*[contains(text(), 'Outage Management')]"))
#     )
#     outage_management_btn.click()
#     time.sleep(2) 

#     supply_status_btn = WebDriverWait(driver, 60).until(
#         EC.element_to_be_clickable((By.XPATH, "//a[@title='Supply Status (Outage Report)']"))
#     )
#     supply_status_btn.click()

#     driver.switch_to.default_content()
#     WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))
#     driver.switch_to.default_content()
#     WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))
#     driver.switch_to.default_content()
#     WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))

#     # ---------------------------------------------------------
#     # STEP 8: Calculate All Date Ranges
#     # ---------------------------------------------------------
#     today = datetime.now()
#     today_str = today.strftime("%Y-%m-%d")
#     today_minus_1 = (today - timedelta(days=1)).strftime("%Y-%m-%d")
#     today_minus_5 = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    
#     # Safely subtract exactly one year
#     try:
#         last_year = today.replace(year=today.year - 1)
#     except ValueError:
#         last_year = today.replace(year=today.year - 1, day=28)
        
#     ly_str = last_year.strftime("%Y-%m-%d")
#     ly_minus_1 = (last_year - timedelta(days=1)).strftime("%Y-%m-%d")
#     ly_minus_5 = (last_year - timedelta(days=5)).strftime("%Y-%m-%d")

#     # Combine all 4 required reports into one master list
#     date_ranges = [
#         # Current Dates
#         (today_str, today_str, f"{today_str}_Outages_Today.csv"),
#         (today_minus_5, today_minus_1, f"{today_str}_Outages_Last_5_Days.csv"),
#         # Last Year Dates
#         (ly_str, ly_str, f"{ly_str}_Outages_Today_Last_Year.csv"),
#         (ly_minus_5, ly_minus_1, f"{ly_str}_Outages_Last_5_Days_Last_Year.csv")
#     ]

#     # ---------------------------------------------------------
#     # STEP 9: Loop and Download All 4 Files
#     # ---------------------------------------------------------
#     for start_dt, end_dt, final_name in date_ranges:
#         print(f"\n--- Processing range: {start_dt} to {end_dt} ---")
        
#         start_date_elem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="startdate"]')))
#         driver.execute_script(f"arguments[0].value = '{start_dt}';", start_date_elem)
#         driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", start_date_elem)

#         end_date_elem = driver.find_element(By.XPATH, '//*[@id="enddate"]')
#         driver.execute_script(f"arguments[0].value = '{end_dt}';", end_date_elem)
#         driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", end_date_elem)
#         time.sleep(3) 

#         # Delete any leftover generic export file
#         input_file = os.path.join(download_dir, "export.csv")
#         if os.path.exists(input_file): os.remove(input_file)
#         if os.path.exists(os.path.join(download_dir, final_name)): os.remove(os.path.join(download_dir, final_name))

#         download_btn = WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, "//img[@title='Export to Spreadsheet']")))
#         download_btn.click()

#         # Wait for the file to appear
#         timeout, elapsed = 120, 0
#         while not os.path.exists(input_file) and elapsed < timeout:
#             time.sleep(1)
#             elapsed += 1
            
#         if not os.path.exists(input_file):
#             raise FileNotFoundError(f"Download timed out for {final_name}!")
        
#         os.rename(input_file, os.path.join(download_dir, final_name))
#         print(f"File saved directly to GitHub workspace as: {final_name}")
#         time.sleep(3) # Short breather before the next loop iteration

# finally:
#     driver.quit()
#====================================================================================================================================
#====================================================================================================================================
V1
#====================================================================================================================================
#====================================================================================================================================
# import time
# import os
# import pandas as pd
# from datetime import datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # --- CLOUD CONFIGURATION ---
# # Get the current working directory of the GitHub Actions runner
# download_dir = os.getcwd() 

# chrome_options = Options()
# chrome_options.add_argument("--headless=new") # Crucial for cloud execution
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")

# # Tell Chrome to download directly to our GitHub workspace without prompting
# prefs = {
#     "download.default_directory": download_dir,
#     "download.prompt_for_download": False,
#     "directory_upgrade": True
# }
# chrome_options.add_experimental_option("prefs", prefs)

# driver = webdriver.Chrome(options=chrome_options)

# try:
#     # ---------------------------------------------------------
#     # STEPS 1-4: Login
#     # ---------------------------------------------------------
#     driver.get("https://distribution.pspcl.in/returns/login.php")
    
#     username_field = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
#     )
#     username_field.send_keys("PDC / Jay Joshi")

#     password_field = driver.find_element(By.CSS_SELECTOR, "#password")
#     password_field.send_keys("pspcl123") # We will discuss securing this later

#     login_button = driver.find_element(By.XPATH, "//*[@id='bname_login']")
#     login_button.click()

#     # ---------------------------------------------------------
#     # STEPS 5-7: Navigate the iFrames
#     # ---------------------------------------------------------
#     WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it("leftFrame"))

#     outage_management_btn = WebDriverWait(driver, 15).until(
#         EC.element_to_be_clickable((By.XPATH, "//*[@id='Outage_Management']//*[contains(text(), 'Outage Management')]"))
#     )
#     outage_management_btn.click()
#     time.sleep(2) 

#     supply_status_btn = WebDriverWait(driver, 15).until(
#         EC.element_to_be_clickable((By.XPATH, "//a[@title='Supply Status (Outage Report)']"))
#     )
#     supply_status_btn.click()

#     driver.switch_to.default_content()
#     WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))
#     driver.switch_to.default_content()
#     WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))
#     driver.switch_to.default_content()
#     WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it("workFrame"))

#     # ---------------------------------------------------------
#     # STEPS 8 & 9: Set Dates and Download Two Files
#     # ---------------------------------------------------------
#     today = datetime.now()
#     today_str = today.strftime("%Y-%m-%d")

#     date_ranges = [
#         (today_str, today_str, f"{today_str}_Outages_Today.csv"),
#         ((today - timedelta(days=5)).strftime("%Y-%m-%d"), (today - timedelta(days=1)).strftime("%Y-%m-%d"), f"{today_str}_Outages_Last_5_Days.csv")
#     ]

#     for start_dt, end_dt, final_name in date_ranges:
#         print(f"\n--- Processing range: {start_dt} to {end_dt} ---")
        
#         start_date_elem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="startdate"]')))
#         driver.execute_script(f"arguments[0].value = '{start_dt}';", start_date_elem)
#         driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", start_date_elem)

#         end_date_elem = driver.find_element(By.XPATH, '//*[@id="enddate"]')
#         driver.execute_script(f"arguments[0].value = '{end_dt}';", end_date_elem)
#         driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", end_date_elem)
#         time.sleep(3) 

#         # Delete old files in the cloud workspace if they exist to prevent numbering issues (like export(1).csv)
#         input_file = os.path.join(download_dir, "export.csv")
#         if os.path.exists(input_file): os.remove(input_file)
#         if os.path.exists(os.path.join(download_dir, final_name)): os.remove(os.path.join(download_dir, final_name))

#         download_btn = WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, "//img[@title='Export to Spreadsheet']")))
#         download_btn.click()

#         timeout, elapsed = 120, 0
#         while not os.path.exists(input_file) and elapsed < timeout:
#             time.sleep(1)
#             elapsed += 1
            
#         if not os.path.exists(input_file):
#             raise FileNotFoundError(f"Download timed out!")
        
#         os.rename(input_file, os.path.join(download_dir, final_name))
#         print(f"File saved directly to GitHub workspace as: {final_name}")
#         time.sleep(5)

# finally:
#     driver.quit()
