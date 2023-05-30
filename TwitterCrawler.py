import csv
import os
import re
import snscrape.modules.twitter as sntwitter
from profanity_check import predict_prob


class TwitterCrawler:

    def __init__(self):
        self.data = {}

    def __extract_twitter_username(self, url):
        # Regular expression pattern to extract the Twitter username
        pattern = r"(?:https?:\/\/)?(?:www\.)?twitter\.com\/([a-zA-Z0-9_]{1,15})"

        # Extract the Twitter username using the pattern
        match = re.search(pattern, url)

        # Check if a match is found and return the username
        if match:
            return match.group(1)
        else:
            return None

    def scrape_twitter(self, twitter_url, platform_directory, num_tweets=15):
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
        fieldnames = ['Date', 'URL', 'Content']

        # Create the CSV file and write the header
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            # Using TwitterSearchScraper to scrape data and append tweets to list
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'from:{username}').get_items()):
                if i > num_tweets:
                    break
                tweet = {
                    "Date": tweet.date.isoformat(),
                    "URL": tweet.url,
                    "Content": tweet.rawContent
                }
                tweets.append(tweet)
                # Write the record to the CSV file
                csv_writer.writerow(tweet)
        self.data[twitter_url] = tweets
        print(tweets)
        return {"success": True, "data": tweets}

    def analyse_tweets(self):
        for url, tweets in self.data.items():
            for tweet in tweets:
                content = tweet['Content']
                profanity_probability = predict_prob([content])
                print(f"URL: {url} Content: {content}")
                print(f"Profanity Prediction: {profanity_probability}")
                tweet['ProfanityProbability'] = profanity_probability
