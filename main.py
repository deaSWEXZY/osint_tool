from modules import SiteSearch

# ----------- USER INPUT -----------
USER_NAME = input("Please input, the exact username: ")
SITE_TO_SEARCH = input("Please Input the site for searching information: ")

scanner = SiteSearch(USER_NAME, SITE_TO_SEARCH)
scanner.run_all()