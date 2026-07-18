from colorama import Fore, Style, init
import argparse

init(autoreset=True)

print(Fore.GREEN + Style.BRIGHT + r"""
      _,.
    ,` -.)
   ( _/-\\-._
  /,|`--._,-^|
    |        |              / _ \/ ___|_ _| \ | |_   _|
    |        |             | | | \___ \| ||  \| | | |  
    |        |             | |_| |___) | || |\  | | |  
    |        |              \___/|____/___|_| \_| |_|         
  \_| |`-._/||          ,'|
    |  `-, / |         /  /
    |     || |        /  /
     `r-._||/   __   /  /
 __,-<_     )`-/  `./  /
'  \   `---'   \   /  /
    |           |./  /
    /           //  /
\_/' \         |/  /
 |    |   _,^-'/  /
 |    , ``  (\/  /_
  \,.->._    \X-=/^
  (  /   `-._//^`
   `Y-.____(__}
    |     {__)
          ()

""" + Style.RESET_ALL + Style.DIM + "Username Scanner by Swexzy.\n")

# ----------- ARGUMENTS HANDLING CLI -----------
parser = argparse.ArgumentParser(description="")
parser.add_argument("username")
parser.add_argument("--site", default="")
parser.add_argument("--similiarity", type=float, default=0.90, help="Similiarity threshold(more precise)")
parser.add_argument("--output", choices=['json', 'csv'], help='Save results as CSV or JSON.')
args = parser.parse_args()

# ----------- USER INPUT -----------
USER_NAME = args.username.strip()
SITE_TO_SEARCH = args.site or ""
OUTPUT_FILE = args.output
SIMILIARITY = args.similiarity
