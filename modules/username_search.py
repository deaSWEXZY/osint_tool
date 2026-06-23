import json
import csv
from config import USER_AGENTS, TOR_PROXY
from colorama import Fore, init
from random import choice

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
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
        self.results = [] # Result List of Data

        # Saving In Directory, if user wants
        self.SAVE_DIR = "results_search"    
        self.PATH_FOR_RESULTS_JSON = f"{self.SAVE_DIR}/{self.target}_results.json"
        self.PATH_FOR_RESULTS_CSV = f"{self.SAVE_DIR}/{self.target}_result.csv"

    # ----------- Loading Json Data -----------
    def load_data(self): 
        with open("sites.json", 'r') as f:
            self.loaded_data = json.load(f)

    # ----------- CHECKING SITE FUNCTION(request) -----------
    async def check_site(self, session, site_name, site_data):
        url = site_data["url"]
        final_url = url.replace("{}", self.target)
        headers = {"User-Agent": choice(USER_AGENTS)}

        try:
            async with session.get(final_url, headers=headers,proxy=TOR_PROXY ,timeout=10) as response:
                html_content = await response.text()
                
                if "Not Found" not in html_content:
                    print(f"Found on {site_name}!")
                    self.results.append({"platform": site_name, "url": final_url})
                    
        except Exception as e: print(f"Error on {site_name}: {e}")

    # ----------- CHECKING SITE FUNCTION(Selenium) -----------
    def check_site_selenium(self, site_name, site_data):
        options = Options()
        options.add_argument("--headless=new") # Opening Web without GUI

        driver = webdriver.Chrome(options=options)
        url = site_data["url"]
        final_url = url.replace("{}", self.target)

        try:
            driver.get(final_url)
            error_marker = site_data.get("error_text")
            page_source = driver.page_source

            is_found = error_marker not in page_source

            if is_found:
                print(f"{Fore.GREEN}[+] Found {site_name}!!\n{final_url}")
                soup = BeautifulSoup(page_source, "html.parser")
                metadata = self.extract_metadata(site_data, soup)
                for key, value in metadata.items():
                    if len(value) == 0: print(f"{Fore.CYAN}{key}: Empty Here!!") #If no info
                    else: print(f"{Fore.CYAN}{key}: {value}") #Like name: peter

                # Adding Results Via Threads
                with self.lock:
                    self.results.append({
                        "platform": site_name,
                        "url": final_url,
                        **metadata
                    })
            else: print(f"{Fore.RED}[-] Sorry, couldn't find anything in {site_name}")
            
            try: driver.quit()
            except Exception: pass

        except requests.exceptions.RequestException:
            print(Fore.RED + f"[!] Connection failed for {site_name}\n")

    # ----------- SAVING RESULTS -----------
    def results_data(self):
        if self.export_file == "json": # Only touch the hard drive if the user opted in!
            os.makedirs(self.SAVE_DIR, exist_ok=True) 
            self.file_format_json()
            print(Fore.CYAN + f"[*] Results securely saved to {self.PATH_FOR_RESULTS_JSON}")
        elif self.export_file == "csv":
            os.makedirs(self.SAVE_DIR, exist_ok=True)
            self.file_format_csv()
            print(Fore.CYAN + f"[*] Results securely saved to {self.PATH_FOR_RESULTS_CSV}")
        
        else:
            print(Fore.CYAN + "[*] Scan complete. (Data not saved to disk)")
            
    # ----------- RUN FUNCTION -----------
    async def run_all(self):
        self.load_data()
        async with aiohttp.ClientSession() as session:
        
            # 2. Create a list of 'slips' (Tasks) for every site
            tasks = []
            for name, data in self.loaded_data.items():
                if data.get("needs_browser"):
                    task = asyncio.to_thread(self.check_site_selenium, name, data)
                else:
                    task = self.check_site(session, name, data)
                tasks.append(task)

            await asyncio.gather(*tasks)
        self.results_data()

    
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
    def site_reach_errors(self, ping, site_name):
        error_codes = {
            403: (Fore.YELLOW, "Blocked"),
            404: (Fore.RED, "Not found"),
            429: (Fore.YELLOW, "Rate limited"),
        }

        if ping.status_code in error_codes:
            color, message = error_codes[ping.status_code]
            print(color + f"[~] {message} on {site_name} ({ping.status_code})\n")
            return True

        if ping.status_code >= 400:
            print(Fore.YELLOW + f"[~] Unexpected status {ping.status_code} on {site_name}\n")
            return True
        return None

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