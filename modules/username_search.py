import json
import pandas as pd
import config as cfg
from colorama import Fore, init, Style
import random
import os
import threading
from bs4 import BeautifulSoup
import asyncio
import nodriver as uc
import Algorithm.data_vector as dt
import string
from curl_cffi.requests import AsyncSession

init(autoreset=True)

class SiteSearch:
    def __init__(self, target_username, target_site="", similiarity=0.6, export_file=""):
        self.loaded_data = None
        self.target = target_username.strip()
        self.target_site = target_site
        self.export_file = export_file
        self.lock = threading.Lock() 
        
        # Limits concurrency
        self.http_semaphore = asyncio.Semaphore(50) 
        self.browser_semaphore = asyncio.Semaphore(2) 
        
        self.results = [] 
        self.not_found = 0
        self.similiarity = similiarity
        self.alphabet = string.ascii_lowercase + string.digits + "_"

        self.SAVE_DIR = "results_search"
        self.PATH_FOR_RESULTS_JSON = f"{self.SAVE_DIR}/{self.target}_results.json"
        self.PATH_FOR_RESULTS_CSV = f"{self.SAVE_DIR}/{self.target}_result.csv"

    # ----------- Loading Json Data -----------
    def load_data(self): 
        with open("sites.json", 'r') as f:
            self.loaded_data = json.load(f)

    # ----------- CHECKING SITE FUNCTION (async HTTP) -----------
    async def check_site(self, session, site_name, site_data):
        async with self.http_semaphore:
            url = site_data.get("url", "")
            if not url:
                return
                
            final_url = url.format(self.target)
            headers = {"User-Agent": random.choice(cfg.USER_AGENTS)}

            try:
                response = await session.get(final_url, headers=headers, timeout=8)
                if response.status_code == 429:
                    print(f"{Fore.YELLOW}[~] Rate limited on {site_name} (429). Backing off...")
                    await asyncio.sleep(5.0)
                    self.not_found += 1
                    return
                
                if self.site_reach_errors(response, site_name): 
                    return

                error_type = site_data.get("errorType", "message")
                html_content = response.text
                error_marker = site_data.get("errorMsg")

                if error_type == "status_code":
                    is_found = (response.status_code == 200)
                else:
                    error_marker = site_data.get("errorMsg")
                    if isinstance(error_marker, list):
                        is_found = not any(msg in html_content for msg in error_marker)
                    elif error_marker:
                        is_found = error_marker not in html_content
                    else:
                        is_found = True

                soup = await asyncio.to_thread(BeautifulSoup, html_content, "html.parser")
                metadata = self.extract_metadata(site_data, soup)

                page_title = (metadata.get("title") or "").lower()
                page_bio = (metadata.get("bio") or "").lower()

                if any(err in page_title or err in page_bio for err in cfg.generic_errors):
                    is_found = False
                has_valid_metadata = any(bool(v) for v in metadata.values()) # If there is boolean assign to var

                if is_found and has_valid_metadata:
                    print(f"{Fore.GREEN}[+] Found {site_name}!\n{final_url}")

                    for key, value in metadata.items():
                        if value:
                            print(f"  └─ {Fore.CYAN}{key}: {value}")
                        print()
                        
                    with self.lock:
                        self.results.append({
                            "platform": site_name,
                            "url": final_url,
                            **metadata
                        })
                else:
                    self.not_found += 1
                        
            except Exception:
                self.not_found += 1

    # ----------- CHECKING SITE FUNCTION (NODRIVER) -----------
    async def check_site_nodriver(self, site_name, site_data):
        async with self.browser_semaphore:
            try:
                await asyncio.wait_for(
                    self._run_nodriver_logic(site_name, site_data), 
                    timeout=15.0
                )
            except asyncio.TimeoutError:
                print(f"{Fore.RED}[!] Timeout on {site_name} (took longer than 15s)\n")
                self.not_found += 1
            except Exception as e:
                print(f"{Fore.RED}[!] Error on {site_name}: {e}\n")

    async def _run_nodriver_logic(self, site_name, site_data):
        url = site_data["url"].format(self.target)
        browser = None
        try:
            browser = await uc.start(
                headless=True,
                browser_args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            page = await browser.get(url)
            await page.sleep(4)
            page_source = await page.get_content()

            error_marker = site_data.get("error_text") or site_data.get("errorMsg")
            if isinstance(error_marker, list):
                is_found = not any(msg in page_source for msg in error_marker)
            elif error_marker:
                is_found = error_marker not in page_source
            else:
                is_found = True

            if is_found:
                print(f"{Fore.GREEN}[+] Found {site_name}!\n{url}\n")
                soup = BeautifulSoup(page_source, "html.parser")
                metadata = self.extract_metadata(site_data, soup)
                
                for key, value in metadata.items():
                    if value:
                        print(f"  └─ {Fore.CYAN}{key}: {value}")
                print()

                with self.lock:
                    self.results.append({"platform": site_name, "url": url, **metadata})
            else:
                self.not_found += 1
        finally:
            if browser:
                browser.stop()  

    # ----------- SAVING RESULTS -----------
    def results_data(self):
        if self.export_file == "json":
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
        async with AsyncSession(impersonate="chrome124") as session:    
            tasks = []
            for name, data in self.loaded_data.items():
                if data.get("needs_browser"):
                    tasks.append(self.check_site_nodriver(name, data))
                else:
                    tasks.append(self.check_site(session, name, data))

            await asyncio.gather(*tasks)

        self.suggestions(username=self.target, alphabet=self.alphabet)
        self.results_data()

    def file_format_csv(self):
        pd.DataFrame(self.results).to_csv(self.PATH_FOR_RESULTS_CSV, index=False, encoding='utf-8')
                
    def file_format_json(self):
        with open(self.PATH_FOR_RESULTS_JSON, 'w') as file:
            json.dump(self.results, file, indent=4)

    # ----------- WEB ERRORS DEBUG -----------
    def site_reach_errors(self, response):
        error_codes = {
            403: (Fore.YELLOW, "Blocked"),
            404: (Fore.RED, "Not found"),
        }

        if response.status_code in error_codes:
            self.not_found += 1
            return True

        if response.status_code >= 400:
            self.not_found += 1
            return True
        
        return False

   # ----------- METADATA EXTRACTING FUNCTION -----------
    def extract_metadata(self, site_data, soup):
        metadata = {}

        # 1. Custom JSON selectors (if available)
        if "metadata" in site_data:
            fields = site_data.get("metadata", {})
            for field, selector in fields.items():
                tag = selector.get("tag")
                if not tag:
                    continue

                element = None
                if "attr" in selector and "value" in selector:
                    element = soup.find(tag, attrs={selector["attr"]: selector["value"]})
                elif "class" in selector:
                    element = soup.find(tag, class_=selector["class"])
                else:
                    element = soup.find(tag)

                if element:
                    if tag == "meta":
                        metadata[field] = (element.get("content") or "").strip()
                    else:
                        metadata[field] = (element.text or "").strip()
                else:
                    metadata[field] = None
            return metadata

        # 2. Meta Tag Fallback
        og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "og:title"})
        if og_title and og_title.get("content"):
            metadata["title"] = og_title["content"].strip()
        elif soup.title and soup.title.string:
            clean_title = soup.title.string.strip()
            if len(clean_title) < 100:
                metadata["title"] = clean_title

        og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if og_desc and og_desc.get("content"):
            metadata["bio"] = og_desc["content"].strip()

        return metadata

    # ----------- USERNAME SUGGESTIONS ALGORITHM CALL -----------
    def suggestions(self, username, alphabet):
        try:
            accurates_usname = dt.most_accurate(username=username, alphabet=alphabet, similiarity=self.similiarity)
            if self.not_found > 3 and accurates_usname:
                print(f"{Fore.GREEN + Style.BRIGHT}Maybe you mean\n---------------")
                for count, name in enumerate(accurates_usname, 1):
                    print(f"{count}. {name}")
        except Exception:
            pass