# -*- coding: utf-8 -*-
import models as m
from sqlalchemy import and_, or_
from datetime import datetime

def create_playlist(user_id, playlist={}, songs=[{}]):
    """ Funcion para agregar una playlist """
    p = m.s.query(m.Playlist).filter(m.Playlist.url == playlist['url']).first()

    # Si la playlists no esta en la DB, se añaden las canciones y luego al usuario
    if p is None:
        p = m.Playlist(**playlist)
        for song in songs:
            if '/channel/' in song.get('youtube_id', '') or '/user/' in song.get('youtube_id', ''):
                continue
            # s = m.s.query(m.Song).filter_by(youtube_id=song['youtube_id']).first()
            s = m.s.query(m.Song).filter(or_(
                m.Song.youtube_id == song.get('youtube_id', ''),
                m.Song.sc_permalink == song.get('sc_permalink', ''))).first()
            s = s if s else m.Song(**song)
            p.songs.append(s)
        m.s.add(p)

    user = m.s.query(m.User).filter_by(id=user_id).first()
    user.playlists.append(p)
    m.s.commit()
    m.s.flush()
    m.s.refresh(p)
    return {
        'id': p.id,
        'url': p.url,
        'name': p.name,
        'source': p.source,
        'total': len(p.songs),
        'missing': len(p.songs)
    }

def unlink_playlist(user_id, playlist_id):
    """ Funcion para quitar una playlist al usuario, las playlists nunca se eliminan """
    user = m.s.query(m.User).filter_by(id=user_id).first()
    playlist = m.s.query(m.Playlist).filter_by(id=playlist_id).first()
    user.playlists.remove(playlist)
    m.s.commit()
    return True

def update_playlist(playlist_id, user_id=None, songs=[{}]):
    """ Funcion para añadir nuevas canciones a una playlist ya existente """
    p = m.s.query(m.Playlist).filter_by(id=playlist_id).first()
    old_yt_ids = [s.youtube_id for s in p.songs]
    new_yt_ids = [s['youtube_id'] for s in songs]
    songs_to_add = [s for s in songs if s['youtube_id'] not in old_yt_ids]
    songs_to_remove = [s for s in p.songs if s.youtube_id not in new_yt_ids]
    for song in songs_to_remove:
        p.songs.remove(song)
    for song in songs_to_add:
        p.songs.append(song)
    m.s.commit()
    return {
        'total': len(p.songs),
        'missing': len(p.songs) + len(songs_to_add) - len(songs_to_remove)
    }

def update_last_date_type(playlist_id, user_id, tipo):
    """ Actualiza las columnas de ultima fecha en que se descargo y tipo """
    r = m.s.query(m.UserPlaylistAssignation).filter_by(user_id=user_id, playlist_id=playlist_id).first()
    r.last_date = datetime.now()
    r.last_type = tipo
    m.s.commit()

def merge_playlists(songs_id, user_id):
    """ Toma canciones de diferentas playlists y genera una nueva  """
    return True

def add_downloaded(user_id, playlist_id, songs_id=[]):
    """ Registra una lista de canciones como descargadas """
    downloaded = m.s.query(m.Downloaded.song_id).filter_by(user_id=user_id, playlist_id=playlist_id).all()
    not_downloaded = set(songs_id) - set([d[0] for d in downloaded])
    for _id in not_downloaded:
        m.s.add(m.Downloaded(user_id=user_id, playlist_id=playlist_id, song_id=_id))
    m.s.commit()

def get_songs(playlistids=[]):
    """ Devuelve una lista de listas con las canciones para los ids de playlists"""
    res = []
    for _id in playlistids:
        p = m.s.query(m.Playlist).filter(m.Playlist.id == _id).first()
        res.append([(obj.song.name, obj.song.youtube_id) for obj in p.songs])
    return res

def get_playlist_information(playlist_id, user_id):
    """ Devuelve canciones e informacion basica de una playlist """
    playlist = m.s.query(m.Playlist).filter_by(id=playlist_id).first()
    uuid = m.s.query(m.UserPlaylistAssignation).filter(
        and_(m.UserPlaylistAssignation.user_id == user_id, m.UserPlaylistAssignation.playlist_id == playlist_id)).first().uuid
    return {
        'id': playlist_id,
        'name': playlist.name,
        'url': playlist.url,
        'source': playlist.source,
        'uuid': uuid,
        'songs': [s.__dict__ for s in playlist.songs],
        'downloaded': m.s.query(m.Downloaded.song_id).filter_by(user_id=user_id, playlist_id=playlist_id).all()
    }
