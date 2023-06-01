import json
import os
import re
from facebook_page_scraper import Facebook_scraper
from profanity_check import predict, predict_prob


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
            scraper.scrap_to_csv(filename, platform_directory)
            json_data = scraper.scrap_to_json()
            self.data[facebook_url] = json_data
            return {"success": True, "data": json_data}
        else:
            return {"success": False, "data": "URL unsupported"}

    def analyse_facebook_posts(self):
        print("Analysing facebook posts")
        # Iterate over each URL in the data
        for url, url_data in self.data.items():
            url_data = json.loads(url_data)
            # Iterate over each post in the URL data
            for post_id, post_data in url_data.items():
                # Check if the 'content' field exists in the post data
                if 'content' in post_data:
                    content = post_data['content']
                    profanity_probability = predict_prob([content])
                    print(f"Content: {content}")
                    print(f"Profanity Prediction: {predict_prob([content])}")
                    post_data['ProfanityProbability'] = profanity_probability
            # Update the url_data in self.data with the modified url_data
            self.data[url] = url_data
