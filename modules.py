import requests
import json
from colorama import Fore, init, Style


init(autoreset=True)
class SiteSearch:
    def __init__(self, target_username, target_site):
        self.target = target_username
        self.target_site = target_site

    def load_data(self): 
        with open("sites.json", 'r') as f:
            self.loaded_data = json.load(f)

    def check_site(self, site_name, site_data):
        url = site_data["url"]
        final_url = url.replace("{}", self.target)
        
        try:
            response = requests.get(final_url)
            
            # Check for success marker
            success_marker = site_data.get("success_text")
            if success_marker:
                if response.status_code == 200 and success_marker in response.text:
                    print(f"{Fore.GREEN + '[+]'} Found {site_name}!!\n{final_url}")
                else:
                    print(f"{Fore.RED + '[-]'} Sorry, couldn't find anything in {site_name}")
            
            # Check for error marker
            error_marker = site_data.get("error_text")
            if error_marker:
                if response.status_code == 200 and error_marker not in response.text:
                    print(f"{Fore.GREEN + '[+]'} Found {site_name}!!\n{final_url}")
                else:
                    print(f"{Fore.RED + '[-]'} Sorry, couldn't find anything in {site_name}")
                    
        except requests.exceptions.RequestException:
            print(Fore.RED + f"[!] Connection failed for {site_name}")

    def run_all(self):
        self.load_data() # Load the JSON first
        for site_name, site_data in self.loaded_data.items():
            
            # The filter logic goes here!
            if self.target_site != "" and self.target_site.lower() != site_name.lower():
                continue

            # Tell the sniper to take the shot
            self.check_site(site_name, site_data)