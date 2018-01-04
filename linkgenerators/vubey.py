import re
import requests
from base import Scrapper

class Vubey(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = 'Vubey'

    def get_link(self):
        youtubeid = "https://www.youtube.com/watch?v=" + self.idvideo
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept-Encoding': 'gzip, deflate, br'}
        data = {'videoURL': youtubeid, 'quality': '320', 'submit': 'Convert+To+MP3'}
        r = requests.post('https://vubey.yt/', headers=headers, data=data)
        urlredir = re.search(r'download=(.*?)">', str(r.content)).group(1)
        r = requests.get('https://vubey.yt/?download={}'.format(urlredir), headers=headers)
        while re.search(r'Please wait', str(r.content)):
            r = requests.get('https://vubey.yt/?download={}'.format(urlredir), headers=headers)
        return re.search(r'https:\/\/dl1\.tubeapi\.com.+?(?=\")', str(r.content)).group()
