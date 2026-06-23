from colorama import Fore, Style, init
import argparse
from config import TOR_PROXY


init(autoreset=True)

print(Fore.CYAN + Style.BRIGHT + r"""
  ___  ____ ___ _   _ _____ 
 / _ \/ ___|_ _| \ | |_   _|
| | | \___ \| ||  \| | | |  
| |_| |___) | || |\  | | |  
 \___/|____/___|_| \_| |_|  
      Username Scanner
""" + Style.RESET_ALL)

# def check_tor():
#     try:
#       r = requests.get("https://httpbin.org/ip", proxies=TOR_PROXY)
#       print(Fore.MAGENTA + f"[*] Tor IP: {r.json()['origin']}\n")

#     except requests.exceptions.ConnectionError:
#       print(Fore.RED + "[!] Tor is not running!")
#     except requests.exceptions.Timeout:
#       print(Fore.YELLOW + "[!] Tor check timed out, but might still be working")
#     except Exception:
#       print(Fore.YELLOW + "[~] Tor check inconclusive, but continuing scan")

# check_tor()

# ----------- ARGUMENTS HANDLING CLI -----------
parser = argparse.ArgumentParser(description="")
parser.add_argument("username")
parser.add_argument("--site", default="")
parser.add_argument("--output", choices=['json', 'csv'], help='Save results as CSV or JSON.')
args = parser.parse_args()

# ----------- USER INPUT -----------
USER_NAME = args.username.strip()
SITE_TO_SEARCH = args.site or ""
OUTPUT_FILE = args.output
