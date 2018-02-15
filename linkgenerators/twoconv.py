import requests
import time
from io import StringIO
from lxml import etree
from lxml.html import parse
from linkgenerators.base import Scrapper

class TwoConv(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = '2conv'

    def get_link(self):
        requests.post('http://2conv.com/es/convert/',
                      headers={
                          "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                          "Accept-Encoding":"gzip, deflate",
                          "Accept-Language":"es-419,es;q=0.9,en;q=0.8",
                          "Cache-Control":"max-age=0",
                          "Connection":"keep-alive",
                          "Content-Length":"83",
                          "Content-Type":"application/x-www-form-urlencoded",
                          "Cookie":"sid=f1pc7cbfda63cavf8t8isjrta3; is_user=1; adblock=off; _ym_uid=1518677148692238462; _ga=GA1.2.1532096820.1518677148; _gid=GA1.2.2147206384.1518677148; webfont-loaded=true; _ym_isad=1; _ym_visorc_28208921=b; is_old_user=1; ap_provider=1; fcap_2912=%7B%22fcap%22%3A1%2C%22expire%22%3A1518763591%7D; convert_count=2; fcap_2720=%7B%22fcap%22%3A3%2C%22expire%22%3A1518763549%7D; fcap_2655=%7B%22fcap%22%3A2%2C%22expire%22%3A1518763591%7D; hl=es; user_converts_count=3; ap_shown=3; fcap_2754=%7B%22fcap%22%3A4%2C%22expire%22%3A1518764094%7D; fcap_2751=%7B%22fcap%22%3A3%2C%22expire%22%3A1518764133%7D; fcap_2783=%7B%22fcap%22%3A3%2C%22expire%22%3A1518763591%7D; fcap_2392=%7B%22fcap%22%3A6%2C%22expire%22%3A1518763573%7D; kadPD=abcde:1:1518678822:1518678222; kadSS=1,1518678822; kadDS=1,1518764622; fcap_2753=%7B%22fcap%22%3A6%2C%22expire%22%3A1518763549%7D; fcap_2752=%7B%22fcap%22%3A3%2C%22expire%22%3A1518764113%7D; fcap_2750=%7B%22fcap%22%3A4%2C%22expire%22%3A1518763549%7D; fcap_2507=%7B%22fcap%22%3A8%2C%22expire%22%3A1518763549%7D; __atuvc=14%7C7; __atuvs=5a852c9c1e892ccc00d; _gat=1; _gali=convertForm",
                          "Host":"2conv.com",
                          "Origin":"http://2conv.com",
                          "Referer":"http://2conv.com/es/",
                          "Upgrade-Insecure-Requests":"1",
                          "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                      },
                      data={
                          'url': 'https://www.youtube.com/watch?v=%s' % self.idvideo,
                          'format':'1',
                          'service': 'youtube'
                      })
        time.sleep(15)
        return 'http://2conv.com/es/download/direct/mp3/yt_%s' % self.idvideo
