import json
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from FacebookCrawler import FacebookCrawler
from InstagramCrawler import InstagramCrawler
from SocialMediaReportGenerator import SocialMediaReportGenerator
from TwitterCrawler import TwitterCrawler


class SocialMediaCrawler:
    def __init__(self, config_file):
        # Create the "data" directory if it doesn't exist
        self.data_directory = os.path.join(os.getcwd(), "data")
        os.makedirs(self.data_directory, exist_ok=True)

        self.social_domains = ['facebook.com', 'twitter.com', 'instagram.com']
        self.config_file = config_file
        self.__read_config()

        self.broken_links = set()
        self.unchecked_links = []

        # need to specify a browser profile with facebook logged in (asia region requires login)
        self.browser_profile = self.config_data['browser_profile']
        self.facebook_crawler = FacebookCrawler(self.browser_profile)
        # Change to your own username, password in the config.json file
        self.instagram_crawler = InstagramCrawler(self.config_data['instagram_credentials']['username'],
                                                  self.config_data['instagram_credentials']['password'])
        self.twitter_crawler = TwitterCrawler()

        self.__start_driver()

    def __read_config(self):
        with open(self.config_file, 'r') as file:
            self.config_data = json.load(file)

    def __start_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--user-data-dir="+self.browser_profile)
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    def __get_social_media_links(self, url):
        self.driver.get(url)
        content = self.driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            if href is not None:
                links.add(href)
        filtered_links = {link for link in links if any(domain in link for domain in self.social_domains)}
        print(f"Extracted from {url}: {filtered_links}")
        return filtered_links

    def __check_broken_link(self, url, error_message):
        self.driver.get(url)
        try:
            # Wait for the error message to appear in the page source
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), error_message)
            )
            return True
        except:
            return False

    def __check_broken_link_platform(self, url):
        is_facebook_profile = re.match(self.facebook_crawler.profile_regex, url)
        is_instagram_profile = re.match(self.instagram_crawler.profile_regex, url)
        is_twitter_profile = re.match(self.twitter_crawler.profile_regex, url)

        if is_facebook_profile:
            error_message = "This content isn't available right now"
            return self.__check_broken_link(url, error_message)
        elif is_instagram_profile:
            error_message = "Sorry, this page isn't available."
            return self.__check_broken_link(url, error_message)
        elif is_twitter_profile:
            error_message = "This account doesn’t exist"
            return self.__check_broken_link(url, error_message)

        return False

    def __crawl_site(self, url, main_directory):
        if self.__check_broken_link_platform(url):
            self.broken_links.add(url)
            return

        platform_directory = os.path.join(main_directory, self.__get_platform_name(url))
        os.makedirs(platform_directory, exist_ok=True)

        if "facebook.com" in url:
            res = self.facebook_crawler.scrape_facebook(url, platform_directory)
        elif "instagram.com" in url:
            res = self.instagram_crawler.scrape_instagram(url, platform_directory)
        elif "twitter.com" in url:
            res = self.twitter_crawler.scrape_twitter(url, platform_directory)
        else:
            self.unchecked_links.append(url)
            return

        if not res["success"]:
            self.unchecked_links.append(url)

    def __get_platform_name(self, url):
        for domain in self.social_domains:
            if domain in url:
                return domain.split('.')[0].capitalize()
        return "Unknown"

    def crawl(self):
        for url in self.config_data['urls']:
            # Create the main directory with the main URL name inside the "data" directory
            main_directory = os.path.join(self.data_directory, url.split("//")[-1].replace("/", "-"))
            os.makedirs(main_directory, exist_ok=True)
            social_media_links = self.__get_social_media_links(url)
            social_media_links.add("https://www.facebook.com/SingaporeDSTA555")
            social_media_links.add("https://www.instagram.com/SingaporeDSTA555")
            social_media_links.add("https://www.twitter.com/SingaporeDSTA555")
            for link in social_media_links:
                self.__crawl_site(link, main_directory)

        self.driver.quit()
        self.facebook_crawler.analyse_facebook_posts()
        self.instagram_crawler.analyse_instagram_posts()
        self.twitter_crawler.analyse_tweets()

        reportGenerator = SocialMediaReportGenerator()
        reportGenerator.generate_html_report(self.instagram_crawler.data,
                                             self.facebook_crawler.data,
                                             self.twitter_crawler.data,
                                             self.broken_links,
                                             self.unchecked_links)

