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
        s = requests.session()
        s.get("https://www.onlinevideoconverter.com/es/mp3-converter")
        r = s.post("https://www2.onlinevideoconverter.com/webservice",
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
        # print(r.json())
        r = s.get('https://www.onlinevideoconverter.com/es/success?id=%s' % r.json()['result']['dPageId'])
        # print(r.)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(r.text), parser)
        return {'link': tree.xpath('//a[@id="downloadq"]')[0].attrib['href']}
