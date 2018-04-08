import json
import re
import requests
from io import StringIO
from lxml import etree
from time import time

from linkgenerators.base import Scrapper

class Mp3Cc(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = 'Youtube2mp3.cc'
        self.s = {
            "1": "odg",
            "2": "ado",
            "3": "jld",
            "4": "tzg",
            "5": "uuj",
            "6": "bkl",
            "7": "fnw",
            "8": "eeq",
            "9": "ebr",
            "10": "asx",
            "11": "ghn",
            "12": "eal",
            "13": "hrh",
            "14": "quq",
            "15": "zki",
            "16": "tff",
            "17": "aol",
            "18": "eeu",
            "19": "kkr",
            "20": "yui",
            "21": "yyd",
            "22": "hdi",
            "23": "ddb",
            "24": "iir",
            "25": "ihi",
            "26": "heh",
            "27": "xaa",
            "28": "nim",
            "29": "omp",
            "30": "eez",
            "31": "rpx",
            "32": "cxq",
            "33": "typ",
            "34": "amv",
            "35": "rlv",
            "36": "xnx",
            "37": "vro",
            "38": "pfg"
        }

    def get_link(self):
        def transform(r):
            n, c = [65, 91, 96, 122, 1], ""
            for t in r:
                e = ord(t)
                if n[0] < e and e < n[1]:
                    c += chr(e - n[4])
                elif n[2] < e and e < n[3]:
                    c += chr(e + n[4])
                elif 48 < e and e < 53:
                    c += str(2 * int(chr(e)))
                elif 45 == e or 95 == e:
                    c += chr(95) if e == 45 else chr(45)
                else:
                    c += chr(e)
            return c


        parser = etree.HTMLParser()
        s = requests.session()
        r = s.get("https://ytmp3.cc")
        tree = etree.parse(StringIO(r.text), parser)
        src = tree.xpath("//script")[1].attrib["src"]
        o = re.search(r"\.js\?[a-z]{1}\=[a-zA-Z0-9\-\_]{4,32}", src).group()[6:]
        k = transform(o)
        r = s.get("https://d.ymcdn.cc/check.php?",
                headers={
                    "Host": "d.ymcdn.cc",
                    "Connection": "keep-alive",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "Accept": "*/*",
                    "Referer": "https://ytmp3.cc/",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
                },
                params={
                    "callback": "jQuery1337_1337",
                    "v": self.idvideo,
                    "f": "mp3",
                    "k": k,
                    "_": int(time() * 1000)
            })

        res = json.loads(r.text.replace("jQuery1337_1337(", "").replace(")", ""))
        url = "https://" + self.s[res["sid"]] + ".ymcdn.cc/" + res["hash"] + "/" + self.idvideo

        return {"link": url}