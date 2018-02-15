from queue import Queue
from threading import Thread
from linkgenerators.soundcloud import ScDownloader
from linkgenerators.vubey import Vubey
from linkgenerators.youtubemp3org import Mp3Org
from linkgenerators.youtubetomp3cc import Mp3Cc
from linkgenerators.onlinevideoconverter import Ovc
from linkgenerators.twoconv import TwoConv

class LinkGenerator(Thread):
    def __init__(self, idsqueue, linksqueue, maxtime, sc_client_id):
        Thread.__init__(self)
        self.idsqueue = idsqueue
        self.linksqueue = linksqueue
        self.maxtime = maxtime
        self.sc_client_id = sc_client_id

    def run(self):
        while True:
            obj = self.idsqueue.get()
            tempqueue = Queue()
            if obj.get('youtube_id'):
                threads = [
                    # Deprecated
                    # Mp3Cc(tempqueue, obj['youtube_id'], self.maxtime),
                    # Mp3Org(tempqueue, obj['youtube_id'], self.maxtime),
                    # Vubey(tempqueue, obj['youtube_id'], self.maxtime),
                    Ovc(tempqueue, obj['youtube_id'], self.maxtime),
                    TwoConv(tempqueue, obj['youtube_id'], self.maxtime),
                ]
            elif obj.get('sc_permalink'):
                threads = [ScDownloader(tempqueue, obj['sc_permalink'], self.sc_client_id, self.maxtime)]
            for th in threads:
                th.daemon = True
                th.start()
            try:
                res = tempqueue.get(True, self.maxtime)
                # self.linksqueue.put({**obj, **{'link': link, 'not_dummy': True}})
                self.linksqueue.put({**obj, **res})
            except:
                # obj['playlist_queue'].put(False)
                # self.linksqueue.put(obj)
                self.linksqueue.put({**obj, **{'link': None}})
                print('Ningun metodo pudo obtener el link en menos de {} segundos'.format(self.maxtime))
            self.idsqueue.task_done()
