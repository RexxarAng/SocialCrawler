import csv
import os
import re
from instaloader import instaloader
from profanity_check import predict_prob


class InstagramCrawler:
    def __init__(self, username, password):
        self.instaloader = instaloader.Instaloader()
        self.instaloader.login(username, password)
        self.profile_regex = r'^https:\/\/www\.instagram\.com\/(?!(?:p|reel)\/)([A-Za-z0-9_]+).*'
        self.data = {}

    def scrape_instagram(self, url, platform_directory, num_posts_to_retrieve=10):

        # Instagram Profile URL regex

        if re.match(self.profile_regex, url):
            # Matched Instagram Profile URL
            profile_value = re.match(self.profile_regex, url).group(1)
            insta_profile = instaloader.Profile.from_username(self.instaloader.context, profile_value)

            # Define a regular expression pattern to match non-allowed characters
            pattern = r'[<>:"/\\|?*]'

            # Replace non-allowed characters with underscores
            filename = re.sub(pattern, '_', url.split("//")[-1])

            # Append the '.csv' extension to the modified filename
            csv_file_path = os.path.join(platform_directory, filename + '.csv')

            if os.path.exists(csv_file_path):
                os.remove(csv_file_path)

            # Prepare the CSV file and column names
            fieldnames = ['date', 'url', 'content']

            # Create the CSV file and write the header
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writeheader()
                # Counter variable
                count = 0
                data = []
                for post in insta_profile.get_posts():

                    # Extract relevant data from the node and organize it into a dictionary
                    record = {
                        'date': post.date,
                        'url': f"https://www.instagram.com/p/{post.shortcode}",
                        'content': post.caption
                    }

                    # Append the record to the data list
                    data.append(record)

                    # Write the record to the CSV file
                    csv_writer.writerow(record)

                    # Increment the counter
                    count += 1

                    # Break the loop if the desired number of posts is reached
                    if count >= num_posts_to_retrieve:
                        break

            # Store the data list as JSON in self.url_dict_json
            self.data[url] = data

            return {"success": True, "data": data}
        else:
            # No match
            return {"success": False, "data": "URL unsupported"}

    def analyse_instagram_posts(self):
        for url, posts in self.data.items():
            for post in posts:
                content = post['content']
                profanity_probability = predict_prob([content])
                post['profanity_probability'] = profanity_probability
