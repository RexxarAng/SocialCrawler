import re
from facebook_page_scraper import Facebook_scraper


class FacebookCrawler:
    def __init__(self, facebook_profile_regex, browser_profile, url_json_dict):
        self.facebook_profile_regex = facebook_profile_regex
        self.browser_profile = browser_profile
        self.url_json_dict = url_json_dict

    def scrape_facebook(self, facebook_url, platform_directory, num_posts_to_retrieve=10):
        match = re.match(self.facebook_profile_regex, facebook_url)
        if match:
            page_name = match.group(1)
            print(page_name)  # Output: CareersGov
            scraper = Facebook_scraper(page_name, num_posts_to_retrieve, "chrome", headless=False,
                                       browser_profile=self.browser_profile)
            scraper.scrap_to_csv(facebook_url.split("//")[-1].replace("/", "-"), platform_directory)
            json_data = scraper.scrap_to_json()
            self.url_json_dict[facebook_url] = json_data
            return {"success": True, "data": json_data}
        else:
            return {"success": False, "data": "Invalid URL"}
