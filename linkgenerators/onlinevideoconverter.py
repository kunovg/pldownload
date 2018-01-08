import requests
from io import StringIO
from lxml import etree
from lxml.html import parse
from linkgenerators.base import Scrapper

class Ovc(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = 'OnlineVideoConverter'

    def get_link(self):
        r = requests.post(
            url='https://www2.onlinevideoconverter.com/webservice',
            headers={
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            },
            data={
                'function': 'validate',
                'args[urlEntryUser]': 'https://www.youtube.com/watch?v=%s' % self.idvideo,
                'args[fromConvert]': 'urlconverter',
                'args[requestExt]': 'mp3',
                'args[nbRetry]': '0',
                'args[audioBitrate]': '0',
                'args[audioFrequency]': '0',
                'args[channel]': 'stereo',
                'args[volume]': '0',
                'args[startFrom]': '-1',
                'args[endTo]': '-1',
            }
        )
        r = requests.get('https://www.onlinevideoconverter.com/es/success?id=%s' % r.json()['result']['dPageId'])
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(r.text), parser)
        return tree.xpath('//a[@id="downloadq"]')[0].attrib['href']
