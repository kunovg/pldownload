import json
import requests
from linkgenerators.base import Scrapper

class Mp3Org(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = 'Youtube-mp3.org'
        self.A = {"a": 870, "b": 906, "c": 167, "d": 119, "e": 130, "f": 899, "g": 248, "h": 123, "i": 627, "j": 706, "k": 694, "l": 421, "m": 214, "n": 561, "o": 819, "p": 925, "q": 857, "r": 539, "s": 898, "t": 866, "u": 433, "v": 299, "w": 137, "x": 285, "y": 613, "z": 635, "_": 638, "&": 639, "-": 880, "/": 687, "=": 721}
        self.r3 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def _sig(self, H):
        F = 1.51214
        N = 3219
        for h in H:
            Q = h.lower()
            if self.fn(self.r3, Q) > -1:
                N = N + (int(Q) * 121 * F)
            else:
                if Q in self.A:
                    N += (self.A[Q] * F)
            N = N * 0.1
        N = round(N * 1000)
        return N

    def fn(self, I, B):
        R = 0
        for i in I:
            if i == B:
                return R
            R += 1
        return -1

    def get_link(self):
        url = "http://www.youtube-mp3.org/a/pushItem/?item=https%3A//www.youtube.com/watch%3Fv%3D"+self.idvideo+"&el=na&bf=false&r=1451880087412"
        s = self._sig(url)
        url += "&s="+str(int(s))

        r = requests.get(url)
        url = "http://www.youtube-mp3.org/a/itemInfo/?video_id="+self.idvideo+"&ac=www&t=grp&r=1451880087759"
        s = self._sig(url)
        url += "&s="+str(int(s))
        r = requests.get(url)
        json_r = r.text.split(" = ")[-1]
        json_r = json_r.replace(";", "")
        jsonresponse = json.loads(json_r)
        r_new = jsonresponse['r'].replace('=', "%3D")

        url = "http://www.youtube-mp3.org/get?video_id="+self.idvideo+"&ts_create="+str(jsonresponse['ts_create'])+"&r="+r_new+"&h2="+jsonresponse['h2']
        s = self._sig(url)
        url += "&s="+str(int(s))
        return url
