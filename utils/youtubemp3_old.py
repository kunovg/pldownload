import sys
import json
import requests
import os
from queue import Queue
from threading import Thread

class Scrapper(Thread):
    def __init__(self, queue, idvideo, iduser, timeout=20):
        Thread.__init__(self)
        self.queue = queue
        self.idvideo = idvideo
        self.timeout = timeout
        self.iduser = iduser

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.join()

class Mp3Cc(Scrapper):
    def __init__(self, queue, idvideo, iduser, timeout=20):
        Scrapper.__init__(self, queue, idvideo, iduser, timeout)

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
            url = 'http://' + s[sid] + '.yt-downloader.org/download.php?id=' + hash_string
            self.queue.put(url)
        raise Exception('An error ocurred in their server')

class Mp3Org(Scrapper):
    def __init__(self, queue, idvideo, iduser, timeout=20):
        Scrapper.__init__(self, queue, idvideo, iduser, timeout)

    def run(self):
        try:
            self.get_link()
        except:
            print("Mp3.org error:", sys.exc_info()[0])

    def get_link(self):
        url = "http://www.youtube-mp3.org/a/pushItem/?item=https%3A//www.youtube.com/watch%3Fv%3D"+self.idvideo+"&el=na&bf=false&r=1451880087412"
        s = _sig(url)
        url += "&s="+str(int(s))

        r = requests.get(url)
        url = "http://www.youtube-mp3.org/a/itemInfo/?video_id="+self.idvideo+"&ac=www&t=grp&r=1451880087759"
        s = _sig(url)
        url += "&s="+str(int(s))
        r = requests.get(url)
        json_r = r.text.split(" = ")[-1]
        json_r = json_r.replace(";", "")
        jsonresponse = json.loads(json_r)
        r_new = jsonresponse['r'].replace('=', "%3D")

        url = "http://www.youtube-mp3.org/get?video_id="+self.idvideo+"&ts_create="+str(jsonresponse['ts_create'])+"&r="+r_new+"&h2="+jsonresponse['h2']
        s = _sig(url)
        url += "&s="+str(int(s))
        self.queue.put(url)

class LinkGeneratorWorker(Thread):
    def __init__(self, idsqueue, linksqueue):
        Thread.__init__(self)
        self.idsqueue = idsqueue
        self.linksqueue = linksqueue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            iduser, idvideo = self.idsqueue.get()
            print(iduser, idvideo)
            tempqueue = Queue()
            threads = [Mp3Cc(tempqueue, idvideo, iduser), Mp3Org(tempqueue, idvideo, iduser)]
            for th in threads:
                th.daemon = True
                th.start()
            try:
                self.linksqueue.put((iduser, tempqueue.get(True, 10)))
            except:
                print('Ningun metodo lo pudo descargar en menos de 10 segundos')
            self.idsqueue.task_done()

class LinkDownloaderWorker(Thread):
    def __init__(self, linksqueue):
        Thread.__init__(self)
        self.linksqueue = linksqueue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            filepath, mp3name, link, c, t = self.linksqueue.get()
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
            if c == t:
                print('Playlist downloaded')
            self.linksqueue.task_done()

def get_sp_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        'Authorization': 'Basic YmEzOTMxOGMzNGUxNDdiNjgwYWY5NzdkMjdiZmIzZTc6NTFiNThiNTQ4NDAzNDYxZjg2MzI1NzM2MTE4NjBlZWY='
    }
    data = {
        'grant_type': 'client_credentials'
    }
    r = requests.post(url, headers=headers, data=data)
    jsontoken = json.loads(r.text)
    print(jsontoken)
    token = jsontoken['access_token']
    return token

def get_sp_tracklist_name(token, user, listaid):
    url = "https://api.spotify.com/v1/users/{}/playlists/{}?fields=name".format(user, listaid)
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    r = requests.get(url, headers=headers)
    jsonresponse = json.loads(r.text)
    return jsonresponse['name']


def get_sp_tracknames(token, user, listaid):
    url = "https://api.spotify.com/v1/users/"+user+"/playlists/"+listaid+"/tracks"
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    offset = 0
    jsonresponse = {'items': [None] * 100}
    tracks = []
    while len(jsonresponse['items']) == 100:
        params = {
            'offset': offset,
        }
        r = requests.get(url, headers=headers, params=params)
        jsonresponse = json.loads(r.text)
        for pl_track in jsonresponse['items']:
            artista = pl_track['track']['artists'][0]['name']
            titulo = pl_track['track']['name']
            song = artista + " - " + titulo
            yield song

        offset = offset+100
    return tracks

b0I = {
    'V': lambda I, B, P: I * B * P,
    'D': lambda I, B: I < B,
    'E': lambda I, B: I == B,
    'B3': lambda I, B: I * B,
    'G': lambda I, B: I < B,
    'v3': lambda I, B: I*B,
    'I3': lambda I, B: I in B,
    'C': lambda I, B: I % B,
    'R3': lambda I, B: I * B,
    'O': lambda I, B: I % B,
    'Z': lambda I, B: I < B,
    'K': lambda I, B: I - B
}
s = {
    "1": 'gpkio',
    "2": 'hpbnj',
    "3": 'macsn',
    "4": 'hcqwb',
    "5": 'fgkzc',
    "6": 'hmqbu',
    "7": 'kyhxj',
    "8": 'nwwxj',
    "9": 'sbist',
    "10": 'ditrj',
    "11": 'qypbr',
    "12": 'trciw',
    "13": 'sjjec',
    "14": 'afyzk',
    "17": 'kzrzi',
    "18": 'rmira',
    "19": 'umbbo',
    "20": 'aigkk',
    "21": 'qgxhg',
    "22": 'twrri',
    "23": 'fkaph',
    "24": 'xqqqh',
    "25": 'xrmrw',
    "26": 'fjhlv',
    "27": 'ejtbn',
    "28": 'urynq',
    "29": 'tjljs',
    "30": 'ywjkg'
}


def _sig(H):
    U = "R3"
    e3 = "B3"
    D3 = "v3"
    N3 = "I3"
    g3 = "V"
    d3 = "C"
    P3 = "O"
    M = ['a', 'c', 'b', 'e', 'd', 'g', 'm', '-', 's', 'o', '.', 'p', '3', 'r', 'u', 't', 'v', 'y', 'n']
    X = [[17, 9, 14, 15, 14, 2, 3, 7, 6, 11, 12, 10, 9, 13, 5], [11, 6, 4, 1, 9, 18, 16, 10, 0, 11, 11, 8, 11, 9, 15, 10, 1, 9, 6]]
    A = {"a": 870, "b": 906, "c": 167, "d": 119, "e": 130, "f": 899, "g": 248, "h": 123, "i": 627, "j": 706, "k": 694, "l": 421, "m": 214, "n": 561, "o": 819, "p": 925, "q": 857, "r": 539, "s": 898, "t": 866, "u": 433, "v": 299, "w": 137, "x": 285, "y": 613, "z": 635, "_": 638, "&": 639, "-": 880, "/": 687, "=": 721}
    r3 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def gs(I, B):
        J = ""
        for i in I:
            J += B[i]
        return J

    def ew(I, B):
        P, J = "K", "indexOf"
        return I[J](B, b0I[P](len(I), len(B))) != -1

    def gh():
        return "www.youtube-mp3.org"

    def fn(I, B):
        P = "E"
        R = 0
        for i in I:
            if b0I[P](i, B):
                return R
            R += 1
        return -1

    L = [1.23413, 1.51214, 1.9141741, 1.5123114, 1.51214, 1.2651]
    F = 1
    try:
        F = L[b0I[P3](1, 2)]
        W = gh()
        S = gs(X[0], M)
        T = gs(X[1], M)
        if(ew(W, S) or ew(W, T)):
            F = L[1]
        else:
            F = L[b0I[d3](5, 3)]
    except:
        pass
    N = 3219
    Y = 0
    for h in H:
        Q = h.lower()
        if fn(r3, Q) > -1:
            N = N+(b0I[g3](int(Q), 121, F))
        else:
            if b0I[N3](Q, A):
                N = N+(b0I[D3](A[Q], F))
        N = b0I[e3](N, 0.1)
        Y += 1
    N = round(b0I[U](N, 1000))
    return N
