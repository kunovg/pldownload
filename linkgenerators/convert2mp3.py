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
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Content-Length": "97",
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": "__cfduid=d7e5f3523bdbe7e14daa4819ada1035f81518314670; WSID=1243133755a7fa4af0c5d4HjTD7LfWOOT5urzFEXeD82TL8aBdOV7a7efca77c39e5071479d1833b375671; __PPU_SESSION_1_813021_false=0|0|0|0|0",
                "Origin": "http://convert2mp3.net",
                "Referer": "http://convert2mp3.net/en/index.php",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            },
            data={
                "url": "https://www.youtube.com/watch?v=%s" % self.idvideo,
                "format": "mp3",
                "9di2n3": "378432450",
                "quality": "1",
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
