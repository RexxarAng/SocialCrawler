import csv
import os
import re
from instaloader import instaloader
from profanity_check import predict, predict_prob


class InstagramCrawler:
    def __init__(self, username, password):
        self.instaloader = instaloader.Instaloader()
        self.instaloader.login(username, password)
        self.data = {}

    def scrape_instagram(self, url, platform_directory, num_posts_to_retrieve=10):

        # Instagram Profile URL regex
        profile_regex = r'^https:\/\/www\.instagram\.com\/([A-Za-z0-9_]+)(?:\/channel)?\/?$'

        if re.match(profile_regex, url):
            # Matched Instagram Profile URL
            print(f'{url} is an Instagram profile URL.')
            profile_value = re.match(profile_regex, url).group(1)
            insta_profile = instaloader.Profile.from_username(self.instaloader.context, profile_value)

            # Prepare the CSV file and column names
            csv_file_path = os.path.join(platform_directory, url.split("//")[-1].replace("/", "-") + '.csv')

            # Prepare the CSV file and column names
            fieldnames = ['Date', 'URL', 'Captions', 'Likes']

            # Create the CSV file and write the header
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writeheader()
                # Counter variable
                count = 0
                data = []
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

            return {"success": True, "data": insta_profile.get_posts()}
        else:
            # No match
            return {"success": False, "data": "URL unsupported"}

    def analyse_instagram_posts(self):
        for url, posts in self.data.items():
            for post in posts:
                caption = post['Captions']
                profanity_probability = predict_prob([caption])
                print(f"URL: {url} Captions: {caption}")
                print(f"Profanity Prediction: {profanity_probability}")
                post['ProfanityProbability'] = profanity_probability

