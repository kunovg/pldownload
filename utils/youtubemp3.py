import os
import sys
import json
import requests
from queue import Queue
from threading import Thread

class Scrapper(Thread):
    def __init__(self, queue, idvideo, timeout=10):
        Thread.__init__(self)
        self.queue = queue
        self.idvideo = idvideo
        self.timeout = timeout

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.join()

class Mp3Cc(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        Scrapper.__init__(self, queue, idvideo, timeout)
        self.s = {"1": 'gpkio', "2": 'hpbnj', "3": 'macsn', "4": 'hcqwb', "5": 'fgkzc', "6": 'hmqbu', "7": 'kyhxj', "8": 'nwwxj', "9": 'sbist', "10": 'ditrj', "11": 'qypbr', "12": 'trciw', "13": 'sjjec', "14": 'afyzk', "17": 'kzrzi', "18": 'rmira', "19": 'umbbo', "20": 'aigkk', "21": 'qgxhg', "22": 'twrri', "23": 'fkaph', "24": 'xqqqh', "25": 'xrmrw', "26": 'fjhlv', "27": 'ejtbn', "28": 'urynq', "29": 'tjljs', "30": 'ywjkg'}

    def run(self):
        try:
            self.get_link()
        except:
            print("Mp3.CC error:", sys.exc_info()[0])

    def get_link(self):
        url = "https://d.yt-downloader.org/check.php"
        r = requests.get(url, params={"v": self.idvideo, "f": "mp3"})
        json_obj = json.loads(r.text)
        hash_string = json_obj['hash']
        error = ""

        if not json_obj.get('sid'):
            url = "https://d.yt-downloader.org/progress.php"
            r = requests.get(url, params={"id": hash_string})
            json_obj = json.loads(r.text)

            progress = json_obj['progress']
            error = json_obj['error']

            while error == "" and progress != "3":
                url = "https://d.yt-downloader.org/progress.php"
                r = requests.get(url, params={"id": hash_string})
                json_obj = json.loads(r.text)
                progress = json_obj['progress']
                error = json_obj['error']

        sid = json_obj['sid']
        if error == "":
            requests.get("https://www.youtube2mp3.cc/p.php?c=1")
            url = 'http://' + self.s[sid] + '.yt-downloader.org/download.php?id=' + hash_string
            self.queue.put(url)
        else:
            raise Exception('An error ocurred in their server')

class Mp3Org(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        Scrapper.__init__(self, queue, idvideo, timeout)
        self.A = {"a": 870, "b": 906, "c": 167, "d": 119, "e": 130, "f": 899, "g": 248, "h": 123, "i": 627, "j": 706, "k": 694, "l": 421, "m": 214, "n": 561, "o": 819, "p": 925, "q": 857, "r": 539, "s": 898, "t": 866, "u": 433, "v": 299, "w": 137, "x": 285, "y": 613, "z": 635, "_": 638, "&": 639, "-": 880, "/": 687, "=": 721}
        self.r3 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def run(self):
        try:
            self.get_link()
        except:
            print("Mp3.org error:", sys.exc_info()[0])

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
        self.queue.put(url)

class LinkGeneratorWorker(Thread):
    def __init__(self, idsqueue, linksqueue, maxtime):
        Thread.__init__(self)
        self.idsqueue = idsqueue
        self.linksqueue = linksqueue
        self.maxtime = maxtime

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            filepath, mp3name, idvideo, c, t, playlist_queue = self.idsqueue.get()
            tempqueue = Queue()
            threads = [Mp3Cc(tempqueue, idvideo, self.maxtime), Mp3Org(tempqueue, idvideo, self.maxtime)]
            for th in threads:
                th.daemon = True
                th.start()
            try:
                link = tempqueue.get(True, self.maxtime)
                self.linksqueue.put((filepath, mp3name, link, c, t, playlist_queue))
            except:
                playlist_queue.put(True)
                print('Ningun metodo pudo obtener el link en menos de {} segundos'.format(self.maxtime))
            self.idsqueue.task_done()

class LinkDownloaderWorker(Thread):
    def __init__(self, linksqueue):
        Thread.__init__(self)
        self.linksqueue = linksqueue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            filepath, mp3name, link, c, t, playlist_queue = self.linksqueue.get()
            print('{} Link: {}'.format(c, link))
            try:
                completesongname = os.path.join(filepath, '{}.mp3'.format(mp3name))
                b = 0
                while b < 10000:
                    r = requests.get(link, stream=True)
                    with open(completesongname, "wb") as code:
                        for chunk in r.iter_content(1024):
                            if not chunk:
                                break
                            code.write(chunk)
                    b = os.path.getsize(completesongname)
                print('Descargada {} de {}'.format(c, t))
                playlist_queue.put(True)
                if playlist_queue.qsize() == t+1:
                    print('Playlist downloaded')
                    while not playlist_queue.empty():
                        playlist_queue.get()
                        playlist_queue.task_done()
            except:
                pass

            self.linksqueue.task_done()
