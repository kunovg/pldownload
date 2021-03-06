import os
import requests
import logging
from threading import Thread
import utils.utils as U

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LinkDownloader(Thread):
    def __init__(self, linksqueue):
        Thread.__init__(self)
        self.linksqueue = linksqueue

    def writePlaylistFile(self, playlist_queue, playlist_path, playlist_name, user_id, playlist_id, finished_download_callback):
        songs_id = []
        with open('{}/{}.m3u'.format(playlist_path, playlist_name), "w+", encoding="utf-8") as playlist_file:
            while not playlist_queue.empty():
                obj = playlist_queue.get()
                if obj:
                    playlist_file.write('{}\n'.format(obj['name']))
                    songs_id.append(obj['id'])
                playlist_queue.task_done()
        # Actualizar cuales canciones adicionales se han descargado y avisar al usuario que termino la descarga
        finished_download_callback(songs_id=songs_id)

    @staticmethod
    def Download(link, playlist_path, mp3name, headers=None):
        mp3name = U.remove_special_characters(mp3name)
        # try:
        completesongname = '/'.join([playlist_path, mp3name])
        b = 0
        print(completesongname)
        iterations = 0
        while b < 1000000 and iterations < 5:
            r = requests.get(link, headers=headers, stream=True)
            if r.status_code == 404:
                logging.warning('{} error 404'.format(link))
                return False
            with open(completesongname, "wb") as code:
                for chunk in r.iter_content(1024):
                    if not chunk:
                        break
                    code.write(chunk)
            b = os.path.getsize(completesongname)
            iterations += 1
        if b > 1000000:
            logging.info('Song %s downloaded' % mp3name)
            return True
        logging.error('Could not download %s with link %s' % (mp3name, link))
        return False
        # except:
        #     return False

    def run(self):
        while True:
            obj = self.linksqueue.get()
            # if obj.get('not_dummy'):
            mp3name = '{}.mp3'.format(obj['name'])
            if self.Download(obj['link'], obj['playlist_path'], mp3name, headers=obj.get('headers')):
                obj['song_download_callback'](obj['playlist_queue'].qsize(), obj['total'])
                obj['playlist_queue'].put({
                    'name': mp3name,
                    'id': obj['id']
                })
            else:
                obj['playlist_queue'].put(False)
            if obj['playlist_queue'].qsize() == obj['total']:
                # Cuando ya se han trabajado todos los items de la playlist
                self.writePlaylistFile(
                    playlist_queue=obj['playlist_queue'],
                    playlist_path=obj['playlist_path'],
                    playlist_name=obj['playlist_name'],
                    user_id=obj['user_id'],
                    playlist_id=obj['playlist_id'],
                    finished_download_callback=obj['finished_download_callback'])
                # Create ZIP
                U.create_zip(
                    file_name=obj['playlist_path'],
                    folder_path=obj['playlist_path'])
                # Borrar la carpeta
                U.delete_folder(obj['playlist_path'])
                logging.info('Playlist {} descargada'.format(obj['playlist_name']))
            self.linksqueue.task_done()
