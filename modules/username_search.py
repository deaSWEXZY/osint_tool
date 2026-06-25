import json
import csv
from config import USER_AGENTS, TOR_PROXY
from colorama import Fore, init, Style
from random import choice
from time import sleep
import os
import subprocess
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
import asyncio
import aiohttp

init(autoreset=True) #Colorama Color Reset

class SiteSearch:
    def __init__(self, target_username, target_site, export_file=""):
        self.loaded_data = None
        self.target = target_username.strip() # Handling whitespaces.
        self.target_site = target_site
        self.export_file = export_file
        self.lock = threading.Lock() # Threadings
        self.browser_semaphore = asyncio.Semaphore(2) # This limits Selenium to 2 concurrent browsers
        self.results = [] # Result List of Data

        self.SAVE_DIR = "results_search" # Directory Name For Results
        self.PATH_FOR_RESULTS_JSON = f"{self.SAVE_DIR}/{self.target}_results.json"
        self.PATH_FOR_RESULTS_CSV = f"{self.SAVE_DIR}/{self.target}_result.csv"

    # ----------- Loading Json Data -----------
    def load_data(self): 
        with open("sites.json", 'r') as f:
            self.loaded_data = json.load(f)

    # ----------- CHECKING SITE FUNCTION(async) -----------
    async def check_site(self, session, site_name, site_data):
        url = site_data["url"]
        final_url = url.format(self.target)
        headers = {"User-Agent": choice(USER_AGENTS)}

        try:
            async with session.get(final_url, headers=headers,timeout=10) as response:

                if self.site_reach_errors(response, site_name): return

                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")
                metadata = self.extract_metadata(site_data, soup)
        
                error_marker = site_data.get("error_text")
                success_marker = site_data.get("success_text")

                check_type = site_data.get("check_type", "error_text")
 
                if check_type == "success_text":
                    success_marker = site_data.get("success_text")
                    is_found = success_marker in html_content if success_marker else True
                else:
                    error_marker = site_data.get("error_text")
                    is_found = error_marker not in html_content if error_marker else True

                if is_found:
                    print(f"{Fore.GREEN}[+] Found {site_name}!\n{final_url}\n")
                    for key, value in metadata.items():
                        if len(value) == 0: print(f"{Fore.CYAN}{key}: Empty Here!!") #If no info
                        else: print(f"{Fore.CYAN}{key}: {value}") #Like name: peter
                        
                    self.results.append({"platform": site_name, "url": final_url})
                    
        except Exception as e: print(f"Error on {site_name}: {e}")

    # ----------- CHECKING SITE FUNCTION(Selenium) -----------
    def check_site_selenium(self, site_name, site_data):
        options = Options() # Chromium Setting
        options.add_argument("--headless=new") # Opening Web without GUI

        # --- RAM & Stability Optimization Flags ---
        options.add_argument("--no-sandbox") # Bypasses OS security model layer (essential for resource limits)
        options.add_argument("--disable-dev-shm-usage") # Forces Chrome to use disk instead of RAM for temporary files
        options.add_argument("--disable-gpu") # Disables hardware acceleration hardware mapping

        # --- Bypass Linux Snap /tmp Permissions ---
        options.add_argument(f"--user-data-dir={os.getcwd()}/chrome-data")
        
        headers = choice(USER_AGENTS)
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            url = site_data["url"]

            stealth(driver,
                languages=['en-US', 'en'],
                user_agent=headers,
                platform="Win32",
                vendor="Google Inc.",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True
            )
            
            final_url = url.format(self.target)
            
            driver.get(final_url)
            sleep(3)
            error_marker = site_data.get("error_text")
            page_source = driver.page_source

            is_found = error_marker not in page_source

            if is_found:
                print(f"{Fore.GREEN}[+] Found {site_name}!\n{final_url}\n")
                soup = BeautifulSoup(page_source, "html.parser")
                metadata = self.extract_metadata(site_data, soup)
                for key, value in metadata.items():
                    if len(value) == 0: print(f"{Fore.CYAN}{key}: Empty Here!!") #If no info
                    else: print(f"{Fore.CYAN}{key}: {value}\n") #Like name: peter

                # Adding Results Via Threads
                with self.lock:
                    self.results.append({
                        "platform": site_name,
                        "url": final_url,
                        **metadata
                    })

            else: print(f"{Fore.RED}[-] Sorry, couldn't find anything in {site_name}")

        # except Exception as e:
        #     print(Fore.RED + f"[!] Connection failed for {site_name}: {e}\n")
        #     print(url)
        
        finally: driver.quit() if driver else print("No Web Driver.")

    # ----------- SELENIUM IN ASYNC(Semaphore) -----------
    async def selenium_runner(self, site_name, site_data):
        async with self.browser_semaphore:
            await asyncio.to_thread(self.check_site_selenium, site_name, site_data)

    # ----------- SAVING RESULTS -----------
    def results_data(self):
        if self.export_file == "json": # Only touch the hard drive if the user opted in!
            os.makedirs(self.SAVE_DIR, exist_ok=True) # Making Directory For Results
            self.file_format_json()
            print(Fore.CYAN + f"[*] Results securely saved to {self.PATH_FOR_RESULTS_JSON}")
        elif self.export_file == "csv":
            os.makedirs(self.SAVE_DIR, exist_ok=True) # Making Directory For Results
            self.file_format_csv()
            print(Fore.CYAN + f"[*] Results securely saved to {self.PATH_FOR_RESULTS_CSV}")
        
        else:
            print(Fore.CYAN + "[*] Scan complete. (Data not saved to disk)")
            
    # ----------- RUN FUNCTION -----------
    async def run_all(self):
        self.load_data()

        async with aiohttp.ClientSession() as session:                   
            tasks = [] # List Of Tasks
            for name, data in self.loaded_data.items(): #Looping Data
                if data.get("needs_browser"):
                    task = self.selenium_runner(name, data)
                else:
                    task = self.check_site(session, name, data) # Running Asyncio Session
                tasks.append(task)

            await asyncio.gather(*tasks)

        self.results_data()
        self.deleting_browser_data()
    
    # ----------- DELETING BROWSER DATA -----------
    def deleting_browser_data(self):
        user_input = input(f"\n{Fore.RED + Style.DIM}Do you want to delete browser data directory?\n'Y'/'N': ").lower()

        subprocess.run(['rm', '-rf', f"{os.getcwd()}/chrome-data"]) if user_input == 'y' else None

    # Creating CSV file for results(user-input)
    def file_format_csv(self):
        with open(self.PATH_FOR_RESULTS_CSV, 'w', newline='') as file:
            try:
                writer = csv.DictWriter(file, fieldnames=['platform', 'url'])
                writer.writeheader()
                writer.writerows(self.results)
            except ValueError:
                writer = csv.DictWriter(file)
    # Creating JSON file for results(user-input)
    def file_format_json(self):
        with open(self.PATH_FOR_RESULTS_JSON, 'w') as file:
            json.dump(self.results, file, indent=4)

    # ----------- WEB ERRORS DEBUG -----------
    def site_reach_errors(self, response, site_name):
        error_codes = {
            403: (Fore.YELLOW, "Blocked"),
            404: (Fore.RED, "Not found"),
            429: (Fore.YELLOW, "Rate limited"),
        }

        if response.status in error_codes:
            color, message = error_codes[response.status]
            print(color + f"[~] {message} on {site_name} ({response.status})\n")
            return True

        if response.status >= 400:
            print(Fore.YELLOW + f"[~] Unexpected status {response.status} on {site_name}\n")
            return True
        
        return False

    # ----------- METADATA EXTRACTING FUNCTION(soup) -----------
    def extract_metadata(self, site_data, soup):
        metadata = {}
        fields = site_data.get("metadata", {})

        for field, selector in fields.items():
            if "class" in selector:
                element = soup.find(selector["tag"], class_=selector["class"])
            else:
                element = None
            if element:
                metadata[field] = element.text.strip()
        return metadata
    