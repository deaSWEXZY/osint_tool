from colorama import Fore, Style, init
import argparse

init(autoreset=True)

print(Fore.CYAN + Style.BRIGHT + r"""
  ___  ____ ___ _   _ _____ 
 / _ \/ ___|_ _| \ | |_   _|
| | | \___ \| ||  \| | | |  
| |_| |___) | || |\  | | |  
 \___/|____/___|_| \_| |_|
        
Username Scanner by Swexzy.
""" + Style.RESET_ALL)

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
