import re
import time
import json
import urllib
import requests
from lxml import etree
from io import StringIO

class Spotify():
    def __init__(self, client_token):
        self.client_token = client_token
        self.token = None
        self.tokentime = None
        self.expiration = None

    def count_spotify_playlist(self, spotify_user, listaid):
        return len(list(self.get_sp_tracknames(user=spotify_user, listaid=listaid)))

    def token_validation(self):
        if (time.time() - self.tokentime) > self.expiration:
            self.get_sp_token()

    def get_sp_token(self):
        url = "https://accounts.spotify.com/api/token"
        headers = {
            'Authorization': 'Basic {}'.format(self.client_token)
        }
        data = {
            'grant_type': 'client_credentials'
        }
        r = requests.post(url, headers=headers, data=data)
        jsontoken = json.loads(r.text)
        self.token = jsontoken['access_token']
        self.tokentime = time.time()
        self.expiration = jsontoken['expires_in']

    def get_sp_tracklist_name(self, user, listaid):
        self.token_validation()
        url = "https://api.spotify.com/v1/users/{}/playlists/{}?fields=name".format(user, listaid)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        r = requests.get(url, headers=headers)
        jsonresponse = json.loads(r.text)
        return jsonresponse['name']

    def get_sp_tracknames(self, user, listaid):
        self.token_validation()
        url = "https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(user, listaid)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        offset = 0
        jsonresponse = {'items': [None] * 100}
        while len(jsonresponse['items']) == 100:
            params = {'offset': offset}
            r = requests.get(url, headers=headers, params=params)
            jsonresponse = json.loads(r.text)
            for pl_track in jsonresponse['items']:
                artista = pl_track['track']['artists'][0]['name']
                titulo = pl_track['track']['name']
                song = artista + " - " + titulo
                yield song

            offset = offset + 100

    def scrap_playlist(self, spotify_user, listaid):
        for trackname in self.get_sp_tracknames(user=spotify_user, listaid=listaid):
            query_s = urllib.parse.urlencode({'search_query': '%s lyrics' % trackname})
            url = "https://www.youtube.com/results?" + query_s
            r = requests.get(url)
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(r.text), parser)
            lista_videos = tree.xpath('//div[contains(@class, "yt-lockup-thumbnail")]//a[contains(@class, "yt-uix-sessionlink")]')
            video_url = lista_videos[0].xpath("@href")[0]
            id_video = video_url.split("=")[-1]
            yield {'youtube_id': id_video, 'name': trackname}

    @staticmethod
    def get_user_and_id(url):
        user = re.search(r'(?<=user\/|user:)(.*)(?=\/playlist|:playlist)', url).group(0)
        idplaylist = re.search(r'(?<=playlist\/|playlist:)(.*)', url).group(0)
        return user, idplaylist
