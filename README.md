# SocialCrawler

## Table of contents
* [Project Description](#Project-Decription)
* [Setup](#Setup)
* [Technologies](#Technologies)
* [Report](#Report)

## Project Description
The SocialCrawler is a web scraping and analysis tool designed to assess the authenticity of social media websites by analyzing the posts and content within user accounts. The project aims to provide a means to verify the legitimacy of social media platforms and detect potential fake or fraudulent accounts.

## Setup

* Install Python3 from the official website: https://www.python.org/downloads/
* Download the appropriate version of chromedriver for your Chrome browser from the official website: https://chromedriver.chromium.org/home. Make sure to download the version that matches your Chrome browser version.
* Extract the chromedriver executable from the downloaded archive.
* Place the chromedriver executable in a directory that is included in the system's PATH environment variable.
* Run this command ```pip install -r requirements.txt``` in the project directory
* Update the config.json file
  * browser profile with your facebook and instagram logged in
  * Instagram username and password

## Technologies
Project is created with:
* selenium
* instaloader
* facebook_page_scraper

## Report
Definitions:
* Broken links: These are profile links on Facebook, Instagram, and Twitter that are no longer accessible or lead to non-existent pages.
* Unchecked profile links: These are private profiles on Facebook, Instagram, and Twitter where the tool is unable to extract any posts or data due to restricted access.
* Unchecked links: These are links that the tool does not support for checking. The tool may not be able to process or extract data from these links.
