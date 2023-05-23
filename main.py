from SocialMediaCrawler import SocialMediaCrawler

if __name__ == '__main__':
    crawler = SocialMediaCrawler("config.json")
    crawler.crawl()

    instagram_data = crawler.instagram_crawler.data
    facebook_data = crawler.facebook_crawler.data
    for url, url_data in facebook_data.items():
        print(f'{url} {url_data}')
        url_data = eval(url_data)
        for post_id, post_data in url_data.items():
            # Check if the 'content' field exists in the post data
            if 'content' in post_data:
                content = post_data['content']
                # Print the result
                print(f"Post ID: {post_id}, Content: {content}")
