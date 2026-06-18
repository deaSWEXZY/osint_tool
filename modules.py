import requests
import json
from colorama import Fore, init
import os

init(autoreset=True) #Colorama Color Reset

class SiteSearch:
    def __init__(self, target_username, target_site, export_json=False):
        self.target = target_username
        self.target_site = target_site
        self.export_json = export_json
        self.results = []

        # Result Directory Handling

        self.save_dir = "results_search"    
        self.PATH_FOR_RESULTS = f"{self.save_dir}/{self.target}_results.json"

    # ----------- Loading Json Data -----------
    def load_data(self): 
        with open("sites.json", 'r') as f:
            self.loaded_data = json.load(f)

    # ----------- PINGING SITES -----------
    def check_site(self, site_name, site_data):
        url = site_data["url"] # Checking values in data file
        final_url = url.replace("{}", self.target) # Changing {} to username
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        # ----------- MAIN PING LOGIC -----------
        try:
            response = requests.get(final_url, headers=headers, timeout=5)
            success_marker = site_data.get("success_text")
            error_marker = site_data.get("error_text")

            # One Line Check
            is_found = (success_marker in response.text) if success_marker else (error_marker not in response.text)

            if response.status_code == 200 and is_found:
                print(f"{Fore.GREEN}[+] Found {site_name}!!\n{final_url}")
                self.results.append({
                    "platform": site_name, 
                    "url": final_url
                })

            else:
                print(f"{Fore.RED}[-] Sorry, couldn't find anything in {site_name}")
    
        except requests.exceptions.RequestException:
            print(Fore.RED + f"[!] Connection failed for {site_name}")

    # ----------- Temporary Results -----------
    def results_data(self):
        if self.export_json: # Only touch the hard drive if the user opted in!
            os.makedirs(self.save_dir, exist_ok=True) 
            with open(self.PATH_FOR_RESULTS, 'w') as file:
                json.dump(self.results, file, indent=4)
            print(Fore.CYAN + f"[*] Results securely saved to {self.PATH_FOR_RESULTS}")
        else:
            print(Fore.CYAN + "[*] Scan complete. (Data not saved to disk)")

    def run_all(self):
        self.load_data()
        for site_name, site_data in self.loaded_data.items():   
            
            # Filter For User_Input
            if self.target_site != "" and self.target_site.lower() != site_name.lower():
                continue

            # Chrcking sites
            self.check_site(site_name, site_data)
        self.results_data()