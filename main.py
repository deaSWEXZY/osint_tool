if __name__ == "__main__":
    import cli
    from modules import SiteSearch
    scanner = SiteSearch(cli.USER_NAME, cli.SITE_TO_SEARCH, cli.OUTPUT_FILE)
    scanner.run_all()