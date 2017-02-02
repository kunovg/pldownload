import uuid
import json
import pyodbc
import requests
import urllib.parse
import utils.utils as U
from lxml import etree
from io import StringIO

class Connection:
    def __init__(self, driver, server, database, user, password):
        self.connection = pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(
            driver,
            server,
            database,
            user,
            password))
        self.cursor = self.connection.cursor()
        print('Connection Established')

    """/////////////////////////////////"""
    """-------------GETTERS-------------"""
    """/////////////////////////////////"""

    def get_uuid(self, iduser, idplaylist):
        self.cursor.execute('SELECT uuid FROM "playlist_users" where idUser = ? and idPlaylist = ?', iduser, idplaylist)
        res = self.cursor.fetchone()
        return res[0] if res else None

    def get_user_pw(self, username=None, iduser=None):
        self.cursor.execute('SELECT pw FROM "users" where (username = ? OR email = ? OR id = ?)', username, username, iduser)
        res = self.cursor.fetchone()
        return res[0] if res else None

    def get_username(self, iduser):
        self.cursor.execute('SELECT username from "users" where id = ?', iduser)
        return self.cursor.fetchone()[0]

    def get_user_id(self, username=None, email=None, uuid=None):
        query = 'SELECT id FROM "users" where '
        query += 'username = ? and ' if username else 'username IS NOT NULL and '
        query += 'email = ?' if email else 'email IS NOT NULL'
        query += ' INTERSECT SELECT idUser from "playlist_users" where uuid = ?' if uuid else ''
        self.cursor.execute(query, list(filter(None, [username, email, uuid])))
        res = self.cursor.fetchone()
        return res[0] if res else None

    def get_user_playlists(self, iduser):
        self.cursor.execute('SELECT idPlaylist, uuid from "playlist_users" where iduser = ?', iduser)
        return self.cursor.fetchall()

    def get_playlist_total_songs(self, uuid):
        self.cursor.execute('SELECT COUNT(idsong) from "songs_in_user_playlist" where uuid = ?', uuid)
        return self.cursor.fetchone()[0]

    def get_playlist_info(self, idplaylist):
        self.cursor.execute('SELECT name, source, url FROM "playlists" where id = ?', idplaylist)
        return self.cursor.fetchone()

    def get_playlist_url_source_user(self, idplaylist):
        query = 'SELECT pl.url, pl.source, pu.iduser FROM "playlists" as pl, "playlist_users" as pu where pl.id = ? and pu.idPlaylist = ?'
        self.cursor.execute(query, idplaylist, idplaylist)
        return self.cursor.fetchone()

    def get_playlists_id(self, name=None, url=None, source=None, iduser=None, uuid=None):
        query = 'SELECT id FROM "playlists" where '
        query += 'name = ? and ' if name else 'name IS NOT NULL and '
        query += 'url = ? and ' if url else 'url IS NOT NULL and '
        query += 'source = ?' if source else 'source IS NOT NULL'
        if iduser and uuid:
            query += ' INTERSECT SELECT idPlaylist from "playlist_users" where idUser = ? and uuid = ?'
        elif iduser:
            query += ' INTERSECT SELECT idPlaylist from "playlist_users" where idUser = ?'
        elif uuid:
            query += ' INTERSECT SELECT idPlaylist from "playlist_users" where uuid = ?'
        self.cursor.execute(query, list(filter(None, [name, url, source, iduser, uuid])))
        return [c[0] for c in self.cursor.fetchall()]

    def get_song_info(self, songid):
        self.cursor.execute('SELECT youtube_id, songname FROM "songs" where id = ?', songid)
        return self.cursor.fetchone()

    def get_songs_id(self, songname=None, youtube_id=None):
        query = 'SELECT id FROM "songs" where '
        query += 'songname = ? and ' if songname else 'songname IS NOT NULL and '
        query += 'youtube_id = ?' if youtube_id else 'youtube_id IS NOT NULL'
        self.cursor.execute(query, list(filter(None, [songname, youtube_id])))
        return [c[0] for c in self.cursor.fetchall()]

    def get_songs_id_from_uuid(self, uuid):
        self.cursor.execute('SELECT idSong FROM "songs_in_user_playlist" where uuid = ?', uuid)
        return [c[0] for c in self.cursor.fetchall()]

    def get_user_downloaded(self, iduser, idplaylist):
        self.cursor.execute('SELECT idSong FROM "user_downloaded" where iduser = ? and idplaylist = ?', iduser, idplaylist)
        return [c[0] for c in self.cursor.fetchall()]

    """/////////////////////////////////"""
    """-------------SETTERS-------------"""
    """/////////////////////////////////"""

    def insert_error(self, description, idsong=0, iduser=0, playlist="", songname=""):
        try:
            self.cursor.execute('INSERT INTO "errors" (idSong, idUser, playlist, songname, description) values (?, ?, ?, ?, ?)',
                                idsong, iduser, playlist, songname, description)
            self.cursor.commit()
            return True
        except pyodbc.IntegrityError:
            return False

    def insert_user(self, username, password, email):
        try:
            self.cursor.execute('SELECT id from "users" where username = ? or email = ?', username, email)
            if self.cursor.fetchone():
                return False
            self.cursor.execute('INSERT INTO "users" (username, pw, email) values (?, ?, ?)', username, password, email)
            self.cursor.commit()
            return True
        except:
            return False

    def insert_playlist(self, name, url, source):
        self.cursor.execute("SELECT insertpl(?, ?, ?)", url, name, source)
        self.cursor.commit()
        return self.cursor.fetchone()[0]

    def insert_song(self, uuid, songname, youtube_id, need_id=False):
        try:
            self.cursor.execute('INSERT INTO "songs" (songname, youtube_id) values (?, ?) returning id', [songname, youtube_id])
            self.cursor.commit()
            songid = self.cursor.fetchone()[0]
            self.cursor.execute('INSERT INTO "songs_in_user_playlist" values (?, ?)', songid, uuid)
            self.cursor.commit()
            return songid
        except pyodbc.IntegrityError:
            songid = self.get_songs_id(youtube_id=youtube_id)[0]
            self.cursor.execute('SELECT * FROM "songs_in_user_playlist" where idsong = ? and uuid = ?', songid, uuid)
            if not self.cursor.fetchone():
                self.cursor.execute('INSERT INTO "songs_in_user_playlist" values (?, ?)', songid, uuid)
                self.cursor.commit()
            if need_id:
                return self.get_songs_id(youtube_id=youtube_id)[0]
            return False

    def add_user_downloaded(self, iduser, idsong, idplaylist):
        try:
            self.cursor.execute('INSERT INTO "user_downloaded" values (?, ?, ?)', iduser, idplaylist, idsong)
            self.cursor.commit()
            return True
        except pyodbc.IntegrityError:
            return False

    def add_playlist_to_user(self, iduser, idplaylist):
        try:
            self.cursor.execute('INSERT INTO "playlist_users" values (?, ?, ?)', iduser, idplaylist, str(uuid.uuid4()))
            self.cursor.commit()
            return True
        except pyodbc.IntegrityError:
            return False

    """/////////////////////////////////"""
    """-------------CHANGERS-------------"""
    """/////////////////////////////////"""

    def change_user_pw(self, iduser, password):
        self.cursor.execute('UPDATE users SET pw = ? WHERE id = ?', password, iduser)
        self.cursor.commit()

    """/////////////////////////////////"""
    """-------------DELETERS-------------"""
    """/////////////////////////////////"""

    def delete_error(self, idsong):
        self.cursor.execute('DELETE FROM "errors" where idSong = ?', idsong)
        self.cursor.commit()

    def delete_user(self, iduser):
        self.cursor.execute('DELETE FROM "playlist_users" where idUser = ?', iduser)
        self.cursor.execute('DELETE FROM "user_downloaded" where idUser = ?', iduser)
        self.cursor.execute('DELETE FROM "users" where id = ?', iduser)
        self.cursor.commit()

    def delete_playlist(self, uuid):
        self.cursor.execute('DELETE FROM "songs_in_user_playlist" where uuid = ?', uuid)
        self.cursor.execute('DELETE FROM "playlist_users" where uuid = ?', uuid)
        self.cursor.execute('DELETE FROM "user_downloaded" where idPlaylist = ?', self.get_playlists_id(uuid=uuid)[0])
        self.cursor.commit()

    def delete_song(self, idsong):
        self.cursor.execute('DELETE FROM "user_downloaded" where idSong = ?', idsong)
        self.cursor.execute('DELETE FROM "songs_in_user_playlist" where idSong = ?', idsong)
        self.cursor.commit()

    """/////////////////////////////////"""
    """-------------SCRAPPERS-------------"""
    """/////////////////////////////////"""

    def scrap_youtube_playlist(self, url, uuid, need_id=False):
        mostrar_mas = None
        r = requests.get(url)
        parser = etree.HTMLParser()
        if "browse_ajax" in r.url:
            rd = json.loads(r.text)
            tree = etree.parse(StringIO(rd['content_html']), parser)
            mostrar_mas = etree.parse(StringIO(rd['load_more_widget_html']), parser).xpath('//@data-uix-load-more-href')[0] if rd.get('load_more_widget_html') else None
            lista_videos = tree.xpath('//a[contains(@class, "pl-video")]')
        else:
            tree = etree.parse(StringIO(r.text), parser)
            mostrar_mas = tree.xpath('//button//@data-uix-load-more-href')[0] if tree.xpath('//button//@data-uix-load-more-href') else None
            lista_videos = tree.xpath('//a[contains(@class, "pl-video-title-link")]')

        for vid in lista_videos:
            yield self.insert_song(uuid=uuid, songname=str(vid.text.strip()), youtube_id=U.video_id(vid.attrib['href']), need_id=need_id)

        if mostrar_mas:
            url_mostrarmas = 'https://www.youtube.com'+mostrar_mas
            yield from self.scrap_youtube_playlist(url=url_mostrarmas, uuid=uuid)

    def scrap_spotify_playlist(self, spotify_inst, spotify_user, listaid, uuid, need_id=False):
        for cancion in spotify_inst.get_sp_tracknames(user=spotify_user, listaid=listaid):
            try:
                query_s = urllib.parse.urlencode({'search_query': '{} lyrics'.format(cancion)})
                url = "https://www.youtube.com/results?" + query_s
                r = requests.get(url)
                print(url)
                parser = etree.HTMLParser()
                tree = etree.parse(StringIO(r.text), parser)
                lista_videos = tree.xpath('//div[contains(@class, "yt-lockup-thumbnail")]//a[contains(@class, "yt-uix-sessionlink")]')
                video_url = lista_videos[0].xpath("@href")[0]
                id_video = video_url.split("=")[-1]
                yield self.insert_song(uuid=uuid, songname=cancion, youtube_id=id_video, need_id=need_id)
            except:
                self.insert_error(idsong=0, description='url')
                yield 'Error al insertar la cancion: {}'.format(cancion)
