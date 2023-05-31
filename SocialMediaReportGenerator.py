import json

import jinja2
import os
from datetime import datetime


def truncate_url(url, max_length=30):
    if len(url) <= max_length:
        return url
    else:
        truncated_url = url[:max_length] + "..."
        return truncated_url


class SocialMediaReportGenerator:
    def generate_html_report(self, instagram_data, facebook_data, twitter_data, broken_links, unchecked_links):
        # Get the absolute path of the script
        script_path = os.path.abspath(__file__)

        # Get the directory containing the script
        script_dir = os.path.dirname(script_path)

        # Change the current working directory
        os.chdir(script_dir)

        # Load the HTML template
        template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        template_env = jinja2.Environment(loader=template_loader)
        # Register the custom filter
        template_env.filters["truncate_url"] = truncate_url
        template = template_env.get_template("report_template.html")

        # Prepare the data for the template
        instagram_report_data = []
        for url, posts in instagram_data.items():
            for post in posts:
                url = post['URL']
                caption = post['Captions']
                probability = post['ProfanityProbability']
                instagram_report_data.append(
                    {'platform': "Instagram", 'url': url, 'caption': caption, 'probability': probability})

        facebook_report_data = []
        # Iterate over each URL in the data
        for url, url_data in facebook_data.items():
            # Iterate over each post in the URL data
            for post_id, post_data in url_data.items():
                print(post_data)
                # Check if the 'content' field exists in the post data
                if 'content' in post_data:
                    content = post_data['content']
                    probability = post_data['ProfanityProbability']
                    facebook_report_data.append(
                        {'platform': "Facebook", 'url': post_data['post_url'], 'content': content, 'probability': probability})

        # Prepare the data for the template
        twitter_report_data = []
        for url, tweets in twitter_data.items():
            for tweet in tweets:
                content = tweet['Content']
                url = tweet['URL']
                probability = tweet['ProfanityProbability']
                twitter_report_data.append(
                    {'platform': "Twitter", 'url': url, 'content': content, 'probability': probability})

        # Render the template with the data
        report_data = []
        if facebook_report_data:
            report_data.append(facebook_report_data)
        if instagram_report_data:
            report_data.append(instagram_report_data)
        if twitter_report_data:
            report_data.append(twitter_report_data)
        # Render the template with the data
        html_output = template.render(report_data=report_data, broken_links=broken_links, unchecked_links=unchecked_links)

        # Create the reports folder if it doesn't exist
        os.makedirs("reports", exist_ok=True)

        # Generate the filename with current datetime
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"reports/social_media_report_{current_datetime}.html"

        # Save the HTML report
        with open(report_filename, 'w', encoding='utf-8') as file:
            file.write(html_output)

            # Get the absolute path of the file
            abs_path = os.path.abspath(report_filename)

            # Print the file location
            print(f"HTML report saved at: {abs_path}")
