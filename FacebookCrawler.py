import csv
import json
import os
import re
from facebook_page_scraper import Facebook_scraper
from profanity_check import predict_prob


class FacebookCrawler:
    def __init__(self, browser_profile):
        self.profile_regex = r'^https://www\.facebook\.com/(\w+)/?$'
        self.browser_profile = browser_profile
        self.data = {}

    def scrape_facebook(self, facebook_url, platform_directory, num_posts_to_retrieve=10):
        match = re.match(self.profile_regex, facebook_url)
        if match:
            page_name = match.group(1)
            print(page_name)  # Output: CareersGov

            # Define a regular expression pattern to match non-allowed characters
            pattern = r'[<>:"/\\|?*]'

            # Replace non-allowed characters with underscores
            filename = re.sub(pattern, '_', facebook_url.split("//")[-1])

            # Append the '.csv' extension to the modified filename
            csv_file_path = os.path.join(platform_directory, filename + '.csv')

            if os.path.exists(csv_file_path):
                os.remove(csv_file_path)

            scraper = Facebook_scraper(page_name, num_posts_to_retrieve, "chrome", headless=True,
                                       browser_profile=self.browser_profile)
            json_data = scraper.scrap_to_json()
            # Prepare the CSV file and column names
            fieldnames = ['date', 'url', 'content']

            # Create the CSV file and write the header
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writeheader()

                data = []
                json_data = json.loads(json_data)
                for post_id, post_data in json_data.items():
                    # Extract relevant data and organize it into a dictionary
                    record = {
                        'date': post_data['posted_on'],
                        'url': post_data['post_url'],
                        'content': post_data['content']
                    }

                    data.append(record)

                    # Write the record to the CSV file
                    csv_writer.writerow(record)

            self.data[facebook_url] = data
            return {"success": True, "data": json_data}
        else:
            return {"success": False, "data": "URL unsupported"}

    def analyse_facebook_posts(self):
        for url, posts in self.data.items():
            for post in posts:
                content = post['content']
                profanity_probability = predict_prob([content])
                post['profanity_probability'] = profanity_probability
