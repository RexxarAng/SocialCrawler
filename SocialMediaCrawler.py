import json
import re
import os
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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

        self.config_file = config_file
        self.__read_config()

        self.broken_links = set()
        self.unchecked_links = set()
        self.data = {}

        self.facebook_crawler = FacebookCrawler(self.browser_profile, self.max_posts)
        # Change to your own username, password in the config.json file
        self.instagram_crawler = InstagramCrawler(self.instagram_username,
                                                  self.instagram_password,
                                                  self.max_posts)
        self.twitter_crawler = TwitterCrawler(self.max_posts)

        self.__start_driver()

    def __read_config(self):
        with open(self.config_file, 'r') as file:
            self.config_data = json.load(file)
        self.social_domains = self.config_data['social_domains']
        self.instagram_username = self.config_data['instagram_credentials']['username']
        self.instagram_password = self.config_data['instagram_credentials']['password']
        self.browser_profile = self.config_data['browser_profile']
        self.max_depth = self.config_data['crawl_options']['depth']
        self.max_posts = self.config_data['crawl_options']['max_posts']

    def __start_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--user-data-dir=" + self.browser_profile)
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    # def __get_social_media_links(self, url):
    #     self.driver.get(url)
    #     content = self.driver.page_source
    #     soup = BeautifulSoup(content, 'html.parser')
    #     links = set()
    #     for a_tag in soup.find_all('a'):
    #         href = a_tag.get('href')
    #         if href is not None:
    #             links.add(href)
    #     filtered_links = {link for link in links if any(domain in link for domain in self.social_domains)}
    #     print(f"Extracted from {url}: {filtered_links}")
    #     return filtered_links

    def __get_social_media_links(self, url, domain, depth=0, visited_links=None):
        if depth > self.max_depth:
            return set()

        if visited_links is None:
            visited_links = set()

        self.driver.get(url)
        content = self.driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        social_media_links = set()
        print(f"Visiting {url} (depth: {depth})")
        visited_links.add(url)
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            if href is not None and not any(char in href for char in ['?', '#']):
                parsed_url = urlparse(href)
                if parsed_url.netloc == '':
                    # Relative URL, construct absolute URL
                    href = urljoin(url, href)
                href_domain = urlparse(href).netloc
                # visit links within same domain recursively using DFS
                if domain in href_domain and href not in visited_links:
                    visited_links.add(href)
                    social_media_links.update(
                        self.__get_social_media_links(href, domain, depth + 1, visited_links))
                elif self.__is_social_media_link(href):
                    social_media_links.add(href)
        return social_media_links

    def __is_social_media_link(self, url):
        return any(domain in url for domain in self.social_domains)

    def __check_broken_link(self, url, error_message):
        self.driver.get(url)
        try:
            # Wait for the error message to appear in the page source
            WebDriverWait(self.driver, 10).until(
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
        elif is_instagram_profile:
            error_message = "Sorry, this page isn't available."
        elif is_twitter_profile:
            error_message = "This account doesn’t exist"
        else:
            return False
        return self.__check_broken_link(url, error_message)

    def __crawl_site(self, main_url, url, main_directory):
        if self.__check_broken_link_platform(url):
            self.broken_links.add(url)
            self.data.setdefault(main_url, {}).setdefault('Broken Links', set()).add(url)
            return

        platform_directory = os.path.join(main_directory, self.__get_platform_name(url))
        os.makedirs(platform_directory, exist_ok=True)

        if "facebook.com" in url:
            res = self.facebook_crawler.scrape_facebook(url, platform_directory)
            if res["success"]:
                self.data.setdefault(main_url, {}).setdefault('platform', {}).setdefault('Facebook', {})[url] = res[
                    'data']
        elif "instagram.com" in url:
            res = self.instagram_crawler.scrape_instagram(url, platform_directory)
            if res["success"]:
                self.data.setdefault(main_url, {}).setdefault('platform', {}).setdefault('Instagram', {})[url] = res[
                    'data']
        elif "twitter.com" in url:
            res = self.twitter_crawler.scrape_twitter(url, platform_directory)
            if res["success"]:
                self.data.setdefault(main_url, {}).setdefault('platform', {}).setdefault('Twitter', {})[url] = res[
                    'data']
        else:
            self.unchecked_links.add(url)
            self.data.setdefault(main_url, {}).setdefault('Unchecked Links', set()).add(url)

        if not res["success"]:
            if res["data"] == "No posts retrieved":
                self.data.setdefault(main_url, {}).setdefault('Unchecked Profile Links', set()).add(url)
            else:
                self.unchecked_links.add(url)
                self.data.setdefault(main_url, {}).setdefault('Unchecked Links', set()).add(url)

    def sort_data(self):
        for main_url in self.data:
            data = self.data[main_url]

            # Add the keys with values in the desired order
            ordered_data = {}
            if data.get('Broken Links'):
                ordered_data['Broken Links'] = data['Broken Links']
            if data.get('Unchecked Profile Links'):
                ordered_data['Unchecked Profile Links'] = data['Unchecked Profile Links']
            if data.get('Unchecked Links'):
                ordered_data['Unchecked Links'] = data['Unchecked Links']

            # Sort the platforms keys within the 'platform' dictionary
            platform_data = data.setdefault('platform', {})
            sorted_platform_data = {
                'Facebook': platform_data.pop('Facebook', {}),
                'Instagram': platform_data.pop('Instagram', {}),
                'Twitter': platform_data.pop('Twitter', {}),
            }
            platform_data.update(sorted_platform_data)
            ordered_data['platform'] = {}
            # Include specific platforms in the desired order
            if platform_data.get('Facebook'):
                ordered_data['platform']['Facebook'] = platform_data['Facebook']
            if platform_data.get('Instagram'):
                ordered_data['platform']['Instagram'] = platform_data['Instagram']
            if platform_data.get('Twitter'):
                ordered_data['platform']['Twitter'] = platform_data['Twitter']

            self.data[main_url] = ordered_data  # Update self.data with the desired order

    def __get_platform_name(self, url):
        for domain in self.social_domains:
            if domain in url:
                return domain.split('.')[0].capitalize()
        return "Unknown"

    def crawl(self):
        for main_url in self.config_data['urls']:
            # Create the main directory with the main URL name inside the "data" directory
            main_directory = os.path.join(self.data_directory, main_url.split("//")[-1].replace("/", "-"))
            os.makedirs(main_directory, exist_ok=True)
            parsed_url = urlparse(main_url)
            domain = parsed_url.netloc
            social_media_links = self.__get_social_media_links(main_url, domain)
            social_media_links.add("https://www.facebook.com/SingaporeDSTA555")
            social_media_links.add("https://www.facebook.com/rexxarang")
            social_media_links.add("https://www.instagram.com/SingaporeDSTA555")
            social_media_links.add("https://www.instagram.com/rexxarang")

            social_media_links.add("https://www.twitter.com/SingaporeDSTA555")
            social_media_links.add("https://www.twitter.com/rexxarang")

            for link in social_media_links:
                self.__crawl_site(main_url, link, main_directory)
        print(self.data)
        self.driver.quit()
        self.facebook_crawler.analyse_facebook_posts()
        self.instagram_crawler.analyse_instagram_posts()
        self.twitter_crawler.analyse_tweets()

        reportGenerator = SocialMediaReportGenerator()
        # reportGenerator.generate_html_report(self.instagram_crawler.data,
        #                                      self.facebook_crawler.data,
        #                                      self.twitter_crawler.data,
        #                                      self.broken_links,
        #                                      self.unchecked_links)
        self.sort_data()
        reportGenerator.generate_html_report(self.data)
