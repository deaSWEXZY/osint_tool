if __name__ == "__main__":
    import cli
    from modules.username_search import SiteSearch
    scanner_username = SiteSearch(cli.USER_NAME, cli.SITE_TO_SEARCH, cli.OUTPUT_FILE)
    scanner_username.run_all()