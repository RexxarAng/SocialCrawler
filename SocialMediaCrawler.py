import csv
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from facebook_page_scraper import Facebook_scraper
import pandas as pd
import instaloader


class SocialMediaCrawler:
    def __init__(self):
        self._start_driver()
        self.broken_links = {}
        self.social_domains = ['facebook.com', 'twitter.com', 'instagram.com']
        self.url_json_dict = {}
        self.browser_profile = "C:/Users/IA_AWEEYIAL/AppData/Local/Google/Chrome/User Data/Default"
        self.instaloader = instaloader.Instaloader()
        # Change to your own username, password
        self.instaloader.login("test", "test")

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

    def _scrape_facebook(self, facebook_url, platform_directory):
        regex = r'^https://www\.facebook\.com/(\w+)/?$'
        match = re.match(regex, facebook_url)
        if match:
            page_name = match.group(1)
            print(page_name)  # Output: CareersGov
            scraper = Facebook_scraper(page_name, 10, "chrome", headless=False,
                                       browser_profile=self.browser_profile)
            scraper.scrap_to_csv(facebook_url.split("//")[-1].replace("/", "-"), platform_directory)
            json_data = scraper.scrap_to_json()
            self.url_json_dict[facebook_url] = json_data
            return {"success": True, "data": json_data}
        else:
            return {"success": False, "data": "Invalid URL"}

    def _scrape_instagram(self, url, platform_directory):

        # Instagram Profile URL regex
        profile_regex = r'^https:\/\/www\.instagram\.com\/([A-Za-z0-9_]+)(?:\/channel)?\/?$'

        # Instagram Post URL regex
        post_regex = r'^https:\/\/www\.instagram\.com\/p\/(.+)\/$'

        if re.match(profile_regex, url):
            # Matched Instagram Profile URL
            print(f'{url} is an Instagram profile URL.')
            profile_value = re.match(profile_regex, url).group(1)
            insta_profile = instaloader.Profile.from_username(self.instaloader.context, profile_value)

            # Prepare the CSV file and column names
            csv_file_path = os.path.join(platform_directory, url.split("//")[-1].replace("/", "-") + '.csv')

            # Prepare the CSV file and column names
            fieldnames = ['Date', 'URL', 'Captions', 'Likes']  # Replace with your column names

            # Create the CSV file and write the header
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writeheader()
                num_posts_to_retrieve = 10
                # Counter variable
                count = 0
                for post in insta_profile.get_posts():
                    # Access the properties and methods of the Post object
                    print(f'Post caption: {post.caption}')
                    print(f'Number of likes: {post.likes}')

                    # Extract relevant data from the node and organize it into a dictionary
                    record = {
                        'Date': post.date,
                        'URL': post.url,
                        'Captions': post.caption,
                        'Likes': post.likes
                    }

                    # Write the record to the CSV file
                    csv_writer.writerow(record)

                    # Increment the counter
                    count += 1

                    # Break the loop if the desired number of posts is reached
                    if count >= num_posts_to_retrieve:
                        break
            return insta_profile.get_posts()
        # To test if this works
        elif re.match(post_regex, url):
            # Matched Instagram Post URL
            print(f'{url} is an Instagram post URL.')
            post_value = re.match(post_regex, url).group(1)
            insta_post = instaloader.Post.from_mediaid(self.instaloader.context, post_value)
            return insta_post
        else:
            # No match
            print(f'{url} does not match any of the patterns.')
            return "No valid instagram url"

    def _check_broken_link(self, url):
        facebook_regex = r'^https://www\.facebook\.com/(\w+)/?$'
        is_facebook_profile = re.match(facebook_regex, url)
        if is_facebook_profile:
            self.driver.get(url)
            error_message = "This content isn't available right now"
            if error_message in self.driver.page_source:
                # print(f"The page {url} is broken.")
                return True
            # print(f"The page {url} is not broken.")
            return False
        return False

    def _crawl_site(self, url, main_directory):
        is_broken = self._check_broken_link(url)
        if is_broken:
            self.broken_links.add(url)
            return
        if "facebook.com" in url:
            platform_directory = os.path.join(main_directory, "Facebook")
            os.makedirs(platform_directory, exist_ok=True)
            res = self._scrape_facebook(url, platform_directory)
            print(res)
        if "instagram.com" in url:
            platform_directory = os.path.join(main_directory, "Instagram")
            os.makedirs(platform_directory, exist_ok=True)
            res = self._scrape_instagram(url, platform_directory)
            print(res)

    def crawl(self, url_file):
        df = pd.read_excel(url_file)
        # Create the "data" directory if it doesn't exist
        data_directory = os.path.join(os.getcwd(), "data")
        os.makedirs(data_directory, exist_ok=True)

        for index, row in df.iterrows():
            url = row['url']
            # Create the main directory with the main URL name inside the "data" directory
            main_directory = os.path.join(data_directory, url.split("//")[-1].replace("/", "-"))
            os.makedirs(main_directory, exist_ok=True)
            social_media_links = self._get_social_media_links(url)
            print(social_media_links)
            for link in social_media_links:
                self._crawl_site(link, main_directory)
        self.driver.quit()
