import requests
import time
from io import StringIO
from lxml import etree
from lxml.html import parse
from linkgenerators.base import Scrapper

DWNLD_HEADERS = {
    "Connection":"keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://2conv.com/es/downloads/mp3/yt_c1tklzNIdDw/",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"es-419,es;q=0.9,en;q=0.8",
    "Cookie":"_ym_uid=1518677148692238462; _ga=GA1.2.1532096820.1518677148; kadPD=abcde:1:1518678822:1518678222; kadSS=1,1518678822; kadDS=1,1518764622; sid=msvg63iibl63hvfk2hhn0k4824; is_user=1; _gid=GA1.2.1388665685.1522138102; webfont-loaded=true; _ym_isad=1; fcap_2924=%7B%22fcap%22%3A2%2C%22expire%22%3A1522224502%7D; fcap_2750=%7B%22fcap%22%3A1%2C%22expire%22%3A1522224671%7D; is_old_user=1; ap_provider=0; noprpkedvhozafiwrcnt=1; noprpkedvhozafiwrexp=Tue, 27 Mar 2018 20:12:14 GMT; fcap_2720=%7B%22fcap%22%3A5%2C%22expire%22%3A1522224502%7D; convert_count=2; fcap_2753=%7B%22fcap%22%3A4%2C%22expire%22%3A1522224502%7D; fcap_2752=%7B%22fcap%22%3A2%2C%22expire%22%3A1522225795%7D; fcap_2751=%7B%22fcap%22%3A1%2C%22expire%22%3A1522225821%7D; hl=es; user_converts_count=2; ap_shown=2; fcap_2754=%7B%22fcap%22%3A5%2C%22expire%22%3A1522224513%7D; fcap_2912=%7B%22fcap%22%3A1%2C%22expire%22%3A1522225837%7D; fcap_2392=%7B%22fcap%22%3A6%2C%22expire%22%3A1522224687%7D; fcap_2783=%7B%22fcap%22%3A2%2C%22expire%22%3A1522224687%7D; __atuvc=0%7C9%2C0%7C10%2C0%7C11%2C0%7C12%2C10%7C13; __atuvs=5ab9fbf627cd9199009",
}

class TwoConv(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = '2conv'

    def get_link(self):
        requests.post('http://2conv.com/es/convert/',
                      headers={
                          "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                          "Accept-Encoding":"gzip, deflate, br",
                          "Accept-Language":"es-419,es;q=0.9,en;q=0.8",
                          "Cache-Control":"max-age=0",
                          "Connection":"keep-alive",
                          "Content-Type":"application/x-www-form-urlencoded",
                          "Cookie":"_ym_uid=1518677148692238462; _ga=GA1.2.1532096820.1518677148; kadPD=abcde:1:1518678822:1518678222; kadSS=1,1518678822; kadDS=1,1518764622; sid=msvg63iibl63hvfk2hhn0k4824; is_user=1; _gid=GA1.2.1388665685.1522138102; webfont-loaded=true; _ym_isad=1; fcap_2924=%7B%22fcap%22%3A2%2C%22expire%22%3A1522224502%7D; fcap_2750=%7B%22fcap%22%3A1%2C%22expire%22%3A1522224671%7D; is_old_user=1; ap_provider=0; noprpkedvhozafiwrcnt=1; noprpkedvhozafiwrexp=Tue, 27 Mar 2018 20:12:14 GMT; fcap_2720=%7B%22fcap%22%3A5%2C%22expire%22%3A1522224502%7D; adblock=off; convert_count=2; fcap_2753=%7B%22fcap%22%3A4%2C%22expire%22%3A1522224502%7D; fcap_2752=%7B%22fcap%22%3A2%2C%22expire%22%3A1522225795%7D; fcap_2751=%7B%22fcap%22%3A1%2C%22expire%22%3A1522225821%7D; hl=es; user_converts_count=2; ap_shown=2; fcap_2754=%7B%22fcap%22%3A5%2C%22expire%22%3A1522224513%7D; fcap_2912=%7B%22fcap%22%3A1%2C%22expire%22%3A1522225837%7D; fcap_2392=%7B%22fcap%22%3A6%2C%22expire%22%3A1522224687%7D; fcap_2783=%7B%22fcap%22%3A2%2C%22expire%22%3A1522224687%7D; __atuvc=0%7C9%2C0%7C10%2C0%7C11%2C0%7C12%2C10%7C13; __atuvs=5ab9fbf627cd9199009",
                          "Referer": "https://2conv.com/es/",
                          "Upgrade-Insecure-Requests": "1",
                      },
                      data={
                          'url': 'https://www.youtube.com/watch?v=%s' % self.idvideo,
                          'format':'1',
                          'service': 'youtube'
                      })
        time.sleep(10)
        link = "http://2conv.com/es/download/direct/mp3/yt_%s/" % self.idvideo
        s = requests.session()
        s.get(link)
        r = s.get(link, headers={**DWNLD_HEADERS, "Referer": "https://2conv.com/es/download/direct/mp3/yt_%s/" % self.idvideo})
        return {
            "link": r.history[0].headers
        }
