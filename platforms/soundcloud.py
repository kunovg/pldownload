import requests

class SoundCloud():
    def __init__(self, client_id):
        self.client_id = client_id

    def scrap_playlist(self, url):
        r = requests.get('http://api.soundcloud.com/resolve?client_id={}&url={}'.format(self.client_id, url))
        for track in r.json()['tracks']:
            yield {'name': track['title'], 'sc_permalink': track['permalink_url']}

    def get_playlist_name(self, url):
        print(url)
        r = requests.get('http://api.soundcloud.com/resolve?client_id={}&url={}'.format(self.client_id, url))
        return r.json()['title']
