import csv
import os
import re
import snscrape.modules.twitter as sntwitter
from profanity_check import predict_prob


class TwitterCrawler:

    def __init__(self, max_posts):
        self.data = {}
        self.max_posts = max_posts
        self.profile_regex = r"(?:https?:\/\/)?(?:www\.)?twitter\.com\/([a-zA-Z0-9_]{1,15})"

    def __extract_twitter_username(self, url):
        # Extract the Twitter username using the pattern
        match = re.search(self.profile_regex, url)

        # Check if a match is found and return the username
        if match:
            return match.group(1)
        else:
            return None

    def scrape_twitter(self, twitter_url, platform_directory):
        # Created a list to append all tweet attributes(data)
        tweets = []

        username = self.__extract_twitter_username(twitter_url)
        if username is None:
            return {"success": False, "data": "Invalid URL"}

        # Define a regular expression pattern to match non-allowed characters
        pattern = r'[<>:"/\\|?*]'

        # Replace non-allowed characters with underscores
        filename = re.sub(pattern, '_', twitter_url.split("//")[-1])

        # Append the '.csv' extension to the modified filename
        csv_file_path = os.path.join(platform_directory, filename + '.csv')

        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)

        # Prepare the CSV file and column names
        fieldnames = ['date', 'url', 'content', 'profanity_probability']

        # Create the CSV file and write the header
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            try:
                # Using TwitterSearchScraper to scrape data and append tweets to list
                for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'from:{username}').get_items()):
                    if i > self.max_posts:
                        break
                    tweet = {
                        "date": tweet.date.isoformat(),
                        "url": tweet.url,
                        "content": tweet.rawContent,
                        'profanity_probability': predict_prob([tweet.rawContent])
                    }
                    tweets.append(tweet)
                    # Write the record to the CSV file
                    csv_writer.writerow(tweet)
            except Exception:
                return {"success": False, "data": "No posts retrieved"}

        if not tweets:
            return {"success": False, "data": "No posts retrieved"}

        self.data[twitter_url] = tweets
        return {"success": True, "data": tweets}

    def analyse_tweets(self):
        for url, tweets in self.data.items():
            for tweet in tweets:
                content = tweet['content']
                profanity_probability = predict_prob([content])
                tweet['profanity_probability'] = profanity_probability
