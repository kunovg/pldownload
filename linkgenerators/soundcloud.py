import requests
from base import Scrapper

class ScDownloader(Scrapper):
    def __init__(self, queue, permalink, client_id, timeout=10):
        super().__init__(queue, timeout)
        self.permalink = permalink
        self.client_id = client_id
        self.name = 'SoundCloud'

    def get_link(self):
        r = requests.get('http://api.soundcloud.com/resolve?client_id={}&url={}'.format(self.client_id, self.permalink))
        return '{}?client_id={}'.format(r.json()['stream_url'], self.client_id)
