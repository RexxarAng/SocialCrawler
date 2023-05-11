from SocialMediaCrawler import SocialMediaCrawler

if __name__ == '__main__':
    crawler = SocialMediaCrawler()
    crawler.crawl('url.xlsx')
    print(crawler.broken_links)
    print(crawler.url_json_dict)
