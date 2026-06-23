import asyncio
import time # Measuring executed time
import cli
from modules.username_search import SiteSearch
from colorama import Fore, Style, init

init(autoreset=True)

if __name__ == "__main__":
    start_time = time.time()
    scanner_username = SiteSearch(cli.USER_NAME, cli.SITE_TO_SEARCH, cli.OUTPUT_FILE)
    asyncio.run(scanner_username.run_all())
    end_time = time.time()

    print(f"\n{Fore.MAGENTA + Style.BRIGHT}Executed time: {end_time - start_time:.2f} seconds")