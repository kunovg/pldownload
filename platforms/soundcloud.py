import requests

class SoundCloud():
    def __init__(self, cliend_id):
        self.cliend_id = cliend_id

    def scrap_playlist(self, url):
        r = requests.get('http://api.soundcloud.com/resolve?client_id={}url={}'.format(self.client_id, url))
        for track in r.json()['tracks']:
            yield {'name': track['title'], 'sc_permalink': track['permalink_url']}

    def get_playlist_name(self, url):
        r = requests.get('http://api.soundcloud.com/resolve?client_id={}url={}'.format(self.client_id, url))
        return r.json()['title']
