from modules import SiteSearch
from colorama import Fore, Style, init

init(autoreset=True)

print(Fore.CYAN + Style.BRIGHT + """
  ___  ____ ___ _   _ _____ 
 / _ \/ ___|_ _| \ | |_   _|
| | | \___ \| ||  \| | | |  
| |_| |___) | || |\  | | |  
 \___/|____/___|_| \_| |_|  
      Username Scanner
""" + Style.RESET_ALL)

# ----------- USER INPUT -----------
USER_NAME = input("Please input, the exact username: ")
SITE_TO_SEARCH = input("Please Input the site for searching information: ")
SAVE_RESULTS = input("Save results in memory?\nY / N: ").lower()

save_or_not = False

if SAVE_RESULTS == 'y':
    save_or_not = True
elif SAVE_RESULTS == 'n':
    save_or_not = False
else:
    print("Please type 'Y' or 'N'...")

scanner = SiteSearch(USER_NAME, SITE_TO_SEARCH, save_or_not)
scanner.run_all()
