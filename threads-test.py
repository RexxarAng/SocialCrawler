from threads import Threads

threads = Threads()

user_id = threads.public_api.get_user_id("alexaubreypoetry")
user_threads = threads.public_api.get_user_threads(user_id)
for thread in user_threads['data']['mediaData']['threads']:
    for thread_item in thread['thread_items']:
        print(thread_item['post']['caption']['text'])