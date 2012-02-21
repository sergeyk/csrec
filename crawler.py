API_KEY = 'T4FTxiyq8qGEy2asaNGY9S6R0wkrdu04c1CvByBFSbKtD32Jvb'
ENTRY_POINT = 'vogue'
import httplib
import urllib2

class Crawler(object):

    def __init__(self, api_key, entry_point):
        self.q = []
        self.q.append(entry_point)
        self.api_key = api_key

    def crawl(self):
        while not self.q_is_empty():
            username = self.dequeue()
            user_posts = self.get_posts(username)
            appreciators = self.extract_appreciators(user_posts)
            self.enqueue_unseen(appreciators)
            self.store_user_posts(username, user_posts)

    def enqueue_unseen(self, appreciators):
        for appreciator in appreciators:
            if self.not_seen(appreciator):
                self.mark_as_seen(appreciator)
                self.enqueue(appreciator)

    def get_posts(self, username):
        url = 'http://api.tumblr.com/v2/blog/%s.tumblr.com/posts/text?api_key=%s&notes_info=true' % (username, self.api_key)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        response = f.read()
        print response

    def extract_appreciators(self, user_posts):
        """Extracts the usernames of the likers and rebloggers"""
        return []

    def mark_as_seen(self, appreciator):
        pass

    def dequeue(self):
        return self.q.pop(0)

    def enqueue(self, username):
        pass

    def store_user_posts(self, username, post_data):
        pass

    def q_is_empty(self):
        return len(self.q) == 0

if __name__ == "__main__":
    c = Crawler(API_KEY, ENTRY_POINT)
    c.crawl()
