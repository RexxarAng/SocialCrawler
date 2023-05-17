import csv
import os
import re
from instaloader import instaloader


class InstagramCrawler:
    def __init__(self, username, password, url_dict_json):
        self.instaloader = instaloader.Instaloader()
        self.instaloader.login(username, password)

    def scrape_instagram(self, url, platform_directory, num_posts_to_retrieve=10):

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
            fieldnames = ['Date', 'URL', 'Captions', 'Likes']

            # Create the CSV file and write the header
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writeheader()
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
