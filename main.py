import requests
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from facebook_scraper import get_posts, get_page_info

# Set up Selenium driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.36'}

# List of common social media domains
social_domains = ['facebook.com', 'twitter.com', 'instagram.com']


def get_social_media_links(url):
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    links = []
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if href is not None:
            links.append(href)
    # Filter out links that contain a social media domain
    filtered_links = [link for link in links if any(domain in link for domain in social_domains)]
    return filtered_links


def crawl_site(url):
    driver.get(url)
    # time.sleep(5)
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    if "facebook.com" in url:
        regex = r'^https://www\.facebook\.com/(\w+)/?$'
        match = re.match(regex, url)
        if match:
            page_name = match.group(1)
            print(page_name)  # Output: CareersGov
            credentials = ("test@test.com", "test")
            for post in get_posts(page_name, pages=5, credentials=credentials):
                print(post['text'][:50])


def login_facebook():
    # Navigate to Facebook login page
    driver.get("https://www.facebook.com/")

    # Enter login credentials and submit
    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "pass")
    login_button = driver.find_element(By.NAME, "login")

    email_input.send_keys("test@test.com")
    password_input.send_keys("test")
    login_button.click()

    # Check if login was successful
    if "facebook.com/login" not in driver.current_url:
        print("Login successful!")
    else:
        print("Login failed.")


if __name__ == '__main__':
    login_facebook()
    social_media_links = get_social_media_links("https://www.careers.gov.sg/")
    print(social_media_links)
    for link in social_media_links:
        crawl_site(link)
