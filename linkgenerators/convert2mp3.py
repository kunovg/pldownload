import requests
from io import StringIO
from lxml import etree
from lxml.html import parse
from linkgenerators.base import Scrapper

class ConvertToMp3(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = 'Convert2mp3.net'

    def get_link(self):
        parser = etree.HTMLParser()

        s = requests.session()
        s.get("http://convert2mp3.net/en/")
        r = s.post("http://convert2mp3.net/en/index.php?p=convert",
            data={
                "url": "https://www.youtube.com/watch?v=%s" % self.idvideo,
                "format": "mp3",
                "9di2n3": "378432450",
            }
        )
        sig = etree.parse(StringIO(r.text), parser) \
            .xpath('//iframe[@id="convertFrame"]')[0].attrib['src']
        r = s.get(sig)
        sig = etree.parse(StringIO(r.text), parser) \
            .xpath('//a')[0].attrib['href']
        r = s.get(sig.replace("p=tags&", "p=complete&"))

        return {'link': etree.parse(StringIO(r.text), parser) \
                        .xpath('//a[contains(@class, "btn-success")]')[0].attrib['href']}
