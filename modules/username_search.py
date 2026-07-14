import json
import pandas as pd
from config import USER_AGENTS
from colorama import Fore, init, Style
import random
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
from aiohttp_socks import ProxyConnector
import Algorithm.data_vector as dt
import string

init(autoreset=True) #Colorama Color Reset

class SiteSearch:
    def __init__(self, target_username, target_site, export_file=""):
        self.loaded_data = None
        self.target = target_username.strip() # Handling whitespaces.
        self.target_site = target_site
        self.export_file = export_file
        self.lock = threading.Lock() 
        self.browser_semaphore = asyncio.Semaphore(2) # This limits Selenium to 2 concurrent browsers
        self.results = [] # Result List of Data
        self.not_found = 0
        self.alphabet = string.ascii_lowercase + string.digits + "_"

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
        headers = {"User-Agent": random.choice(USER_AGENTS)}

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
                        if metadata[key] is not None:
                            if len(value) == 0: pass
                            else: print(f"{Fore.CYAN}{key}: {value}")
                        else: pass

                    with self.lock:
                        self.results.append({
                            "platform": site_name,
                            "url": final_url,
                            **metadata
                        })
                    
        except Exception as e: print(f"Error on {site_name}: {type(e).__name__}: {e}")

    # ----------- CHECKING SITE FUNCTION(Selenium) -----------
    def check_site_selenium(self, site_name, site_data):
        options = Options() # Chromium Setting
        options.add_argument("--headless=new") # Opening Web without GUI

        # --- RAM and Stability Optimization ---
        options.add_argument("--no-sandbox") # Bypasses OS security model layer
        options.add_argument("--disable-dev-shm-usage") # Forces Chrome to use disk instead of RAM for temporary files
        options.add_argument("--disable-gpu") # Disables hardware acceleration hardware mapping

        # --- Bypassing Linux Snap /tmp Permissions ---
        options.add_argument(f"--user-data-dir={os.getcwd()}/chrome-data/{site_name}")

        # options.add_argument('--proxy-server=socks5://10.64.0.1:1080') # Proxy WireGuard

        headers = random.choice(USER_AGENTS)
        
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
            sleep(2)
            error_marker = site_data.get("error_text")
            page_source = driver.page_source
            is_found = error_marker not in page_source

            if is_found:
                print(f"{Fore.GREEN}[+] Found {site_name}!\n{final_url}\n")
                soup = BeautifulSoup(page_source, "html.parser")
                metadata = self.extract_metadata(site_data, soup)
                for key, value in metadata.items():
                    if metadata[key] is not None:
                        if len(value) == 0: pass
                        else: print(f"{Fore.CYAN}{key}: {value}\n")
                # Adding Results Via Threads
                with self.lock:
                    self.results.append({
                        "platform": site_name,
                        "url": final_url,
                        **metadata
                    })

            else:
                print(f"{Fore.RED}[-] Sorry, couldn't find anything in {site_name}\n")
                self.not_found += 1

        except Exception as e:
            print(Fore.RED + f"[!] Connection failed for {site_name}: {e}\n")
        
        finally:
            if driver is not None:
                driver.quit()
            else: print("No Web Driver...")

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
        
        connector = ProxyConnector.from_url('socks5://10.64.0.1:1080')

        async with aiohttp.ClientSession() as session:                   
            tasks = [] # List Of Tasks
            for name, data in self.loaded_data.items(): #Looping Data
                if data.get("needs_browser"):
                    task = self.selenium_runner(name, data)
                else:
                    task = self.check_site(session, name, data) # Running Asyncio Session
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                tasks.append(task)

            await asyncio.gather(*tasks)

        self.suggestions(username=self.target, alphabet=self.alphabet)
        self.results_data()
        self.deleting_browser_data()
    
    # ----------- DELETING BROWSER DATA -----------
    def deleting_browser_data(self):
        user_input = input(f"\n{Fore.RED + Style.DIM}Do you want to delete browser data directory?\n'Y'/'N': ").lower()

        subprocess.run(['rm', '-rf', f"{os.getcwd()}/chrome-data"]) if user_input == 'y' else None

    # Creating CSV file for results(user-input)
    def file_format_csv(self):
        pd.DataFrame(self.results).to_csv(self.PATH_FOR_RESULTS_CSV, index=False, encoding='utf-8')
                
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
            self.not_found += 1
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
            tag = selector["tag"]
            if "attr" and "value" in selector:
                attr_name = selector["attr"]
                attr_value = selector["value"]

                element = soup.find(tag, attrs={attr_name: attr_value})

            elif "class" in selector:
                element = soup.find(tag, class_=selector["class"])

            else: element = soup.find(tag)

            if element:
                if tag == "meta":
                    metadata[field] = element.get("content", "").strip()
                else: metadata[field] = element.text.strip()
            else:
                metadata[field] = None
        return metadata
    
    def suggestions(self, username, alphabet):
        accurates_usname = dt.most_accurate(username=username, alphabet=alphabet)
        
        count = 1
        if self.not_found > 3:
            print(f"{Fore.GREEN + Style.BRIGHT}Maybe you mean\n---------------")
            for name in accurates_usname:
                print(f"{count}.{name}")
                count += 1
            