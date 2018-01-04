import requests
from base import Scrapper

class Mp3Cc(Scrapper):
    def __init__(self, queue, idvideo, timeout=10):
        super().__init__(queue, timeout)
        self.idvideo = idvideo
        self.name = 'Youtube2mp3.cc'
        self.s = {'1': "fzaqn", '2': "agobe", '3': "topsa", '4': "hcqwb", '5': "gdasz", '6': "iooab", '7': "idvmg", '8': "bjtpp", '9': "sbist", '10': "gxgkr", '11': "njmvd", '12': "trciw", '13': "sjjec", '14': "puust", '15': "ocnuq", '16': "qxqnh", '17': "jureo", '18': "obdzo", '19': "wavgy", '20': "qlmqh", '21': "avatv", '22': "upajk", '23': "tvqmt", '24': "xqqqh", '25': "xrmrw", '26': "fjhlv", '27': "ejtbn", '28': "urynq", '29': "tjljs", '30': "ywjkg"}

    def get_link(self):
        url = "https://d.yt-downloader.org/check.php"
        r = requests.get(url, params={"v": self.idvideo, "f": "mp3"})
        json_obj = r.json()
        hash_string = json_obj['hash']
        error = ""

        if not json_obj.get('sid'):
            url = "https://d.yt-downloader.org/progress.php"
            r = requests.get(url, params={"id": hash_string})
            json_obj = r.json()

            progress = json_obj['progress']
            error = json_obj['error']

            while error == "" and progress != "3":
                url = "https://d.yt-downloader.org/progress.php"
                r = requests.get(url, params={"id": hash_string})
                json_obj = r.json()
                progress = json_obj['progress']
                error = json_obj['error']

        sid = json_obj['sid']
        if error == "":
            requests.get("https://www.youtube2mp3.cc/p.php?c=1")
            return 'http://' + self.s[sid] + '.yt-downloader.org/download.php?id=' + hash_string
        else:
            raise Exception(json_obj)
