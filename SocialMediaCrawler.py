import re
from bs4 import BeautifulSoup
from selenium import webdriver
from facebook_page_scraper import Facebook_scraper
import pandas as pd


class SocialMediaCrawler:
    def __init__(self):
        self._start_driver()
        self.broken_links = {}
        self.social_domains = ['facebook.com', 'twitter.com', 'instagram.com']
        self.url_json_dict = {}

    def _start_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("user-data-dir=C:/Users/IA_AWEEYIAL/AppData/Local/Google/Chrome/User Data/Default")
        self.driver = webdriver.Chrome(options=chrome_options)


    def _get_social_media_links(self, url):
        self.driver.get(url)
        content = self.driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            if href is not None:
                links.append(href)
        filtered_links = {link for link in links if any(domain in link for domain in self.social_domains)}
        return filtered_links

    def _scrape_facebook(self, facebook_url):
        regex = r'^https://www\.facebook\.com/(\w+)/?$'
        match = re.match(regex, facebook_url)
        if match:
            page_name = match.group(1)
            print(page_name)  # Output: CareersGov
            scraper = Facebook_scraper(page_name, 10, "chrome", headless=False,
                                       browser_profile="C:/Users/IA_AWEEYIAL/AppData/Local/Google/Chrome/User Data/Default")
            json_data = scraper.scrap_to_json()
            self.url_json_dict[facebook_url] = json_data
            return {"success": True, "data": json_data}
        else:
            return {"success": False, "data": "Invalid URL"}

    def _check_broken_link(self, url):
        facebook_regex = r'^https://www\.facebook\.com/(\w+)/?$'
        is_facebook_profile = re.match(facebook_regex, url)
        if is_facebook_profile:
            self.driver.get(url)
            error_message = "This content isn't available right now"
            if error_message in self.driver.page_source:
                print(f"The page {url} is broken.")
                return True
            print(f"The page {url} is not broken.")
            return False
        return False

    def _crawl_site(self, url):
        is_broken = self._check_broken_link(url)
        if is_broken:
            self.broken_links.add(url)
            return
        if "facebook.com" in url:
            res = self._scrape_facebook(url)
            print(res)

    def crawl(self, url_file):
        df = pd.read_excel(url_file)
        for index, row in df.iterrows():
            url = row['url']
            social_media_links = self._get_social_media_links(url)
            print(social_media_links)
            for link in social_media_links:
                self._crawl_site(link)
        self.driver.quit()
