from SocialMediaCrawler import SocialMediaCrawler

if __name__ == '__main__':
    crawler = SocialMediaCrawler("config.json")
    crawler.crawl()
    crawler.facebook_crawler.analyse_facebook_posts()
