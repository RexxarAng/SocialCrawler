from SocialMediaCrawler import SocialMediaCrawler
from SocialMediaReportGenerator import SocialMediaReportGenerator

if __name__ == '__main__':
    crawler = SocialMediaCrawler("config.json")
    crawler.crawl()
    crawler.facebook_crawler.analyse_facebook_posts()
    crawler.instagram_crawler.analyse_instagram_posts()
    reportGenerator = SocialMediaReportGenerator()
    reportGenerator.generate_html_report(crawler.instagram_crawler.data, crawler.facebook_crawler.data, crawler.unchecked_links)
