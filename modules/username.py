import requests
import json
from colorama import Fore, init
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import csv
from config import USER_AGENTS, TOR_PROXY
from random import choice

init(autoreset=True) #Colorama Color Reset

class SiteSearch:
    def __init__(self, target_username, target_site, export_file=""):
        self.target = target_username.strip()
        self.target_site = target_site
        self.export_file = export_file
        self.lock = threading.Lock()
        self.results = []

        # Result Directory Handling

        self.save_dir = "results_search"    
        self.PATH_FOR_RESULTS_JSON = f"{self.save_dir}/{self.target}_results.json"
        self.PATH_FOR_RESULTS_CSV = f"{self.save_dir}/{self.target}_result.csv"

    # ----------- Loading Json Data -----------
    def load_data(self): 
        with open("sites.json", 'r') as f:
            self.loaded_data = json.load(f)

    # ----------- PINGING SITES -----------
    def check_site(self, site_name, site_data):
        url = site_data["url"] # Checking values in data file
        final_url = url.replace("{}", self.target) # Changing {} to username
        headers = {"User-Agent": choice(USER_AGENTS)} # Choice is from random library

        # ----------- MAIN PING LOGIC -----------
        try:
            response = requests.get(final_url, headers=headers, proxies=TOR_PROXY, timeout=10)
            if self.site_reach_errors(ping=response, site_name=site_name):
                return 

            success_marker = site_data.get("success_text")
            error_marker = site_data.get("error_text")

            # One Line Check
            is_found = (success_marker in response.text) if success_marker else (error_marker not in response.text)

            if is_found:
                print(f"{Fore.GREEN}[+] Found {site_name}!!\n{final_url}\n")
                with self.lock:
                    self.results.append({
                        "platform": site_name, 
                        "url": final_url
                })

            else:
                print(f"{Fore.RED}[-] Sorry, couldn't find anything in {site_name}\n")
    
        except requests.exceptions.RequestException:
            print(Fore.RED + f"[!] Connection failed for {site_name}\n")

    # ----------- SAVING RESULTS -----------
    def results_data(self):
        if self.export_file == "json": # Only touch the hard drive if the user opted in!
            os.makedirs(self.save_dir, exist_ok=True) 
            self.file_format_json()
            print(Fore.CYAN + f"[*] Results securely saved to {self.PATH_FOR_RESULTS_JSON}")
        elif self.export_file == "csv":
            os.makedirs(self.save_dir, exist_ok=True)
            self.file_format_csv()
            print(Fore.CYAN + f"[*] Results securely saved to {self.PATH_FOR_RESULTS_CSV}")
        
        else:
            print(Fore.CYAN + "[*] Scan complete. (Data not saved to disk)")
        
    # ----------- RUN FUNCTION -----------
    def run_all(self):
        self.load_data()
        
        # Filtered dict first
        sites = {
            name: data for name, data in self.loaded_data.items()
            if not self.target_site or self.target_site.lower() == name.lower()
        }
        
        # Run With Threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            for name, data in sites.items():
                executor.submit(self.check_site, name, data)
        self.results_data()
    
    # Creating CSV file for results(user-input)
    def file_format_csv(self):
        with open(self.PATH_FOR_RESULTS_CSV, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['platform', 'url'])
            writer.writeheader()
            writer.writerows(self.results)
    
    # Creating JSON file for results(user-input)
    def file_format_json(self):
        with open(self.PATH_FOR_RESULTS_JSON, 'w') as file:
            json.dump(self.results, file, indent=4)

    # ----------- WEB PINGING ERRORS DEBUG -----------
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