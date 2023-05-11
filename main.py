import re
from bs4 import BeautifulSoup
from selenium import webdriver
from facebook_page_scraper import Facebook_scraper
import pandas as pd

# Set up Selenium driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
# chrome_options.add_argument("user-data-dir=C:/Users/IA_AWEEYIAL/AppData/Local/Google/Chrome/User Data/Default")
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
    if "facebook.com" in url:
        res = scrape_facebook(url)
        if res['success']:
            print(res['data'])


def scrape_facebook(facebook_url):
    regex = r'^https://www\.facebook\.com/(\w+)/?$'
    match = re.match(regex, facebook_url)
    if match:
        page_name = match.group(1)
        print(page_name)  # Output: CareersGov
        scraper = Facebook_scraper(page_name, 10, "chrome", headless=False,
                                   browser_profile="C:/Users/IA_AWEEYIAL/AppData/Local/Google/Chrome/User Data/Default")
        json_data = scraper.scrap_to_json()
        return {"success": True, "data": json_data}
    else:
        return {"success": False, "data": "Invalid URL"}


# def login_facebook():
#     # Navigate to Facebook login page
#     driver.get("https://www.facebook.com/")
#
#     # Enter login credentials and submit
#     email_input = driver.find_element(By.ID, "email")
#     password_input = driver.find_element(By.ID, "pass")
#     login_button = driver.find_element(By.NAME, "login")
#
#     email_input.send_keys("test@test.com")
#     password_input.send_keys("test")
#     login_button.click()
#
#     # Check if login was successful
#     if "facebook.com/login" not in driver.current_url:
#         print("Login successful!")
#     else:
#         print("Login failed.")


if __name__ == '__main__':
    # Replace `url.xlsx` with the actual file name
    df = pd.read_excel('url.xlsx')

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        url = row['url']
        # Crawl the site for social media links
        social_media_links = get_social_media_links(url)
        print(social_media_links)
        # Crawl the data in the different social media sites
        for link in social_media_links:
            crawl_site(link)
