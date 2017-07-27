import json
import datetime
import utils.utils as U
from sqlalchemy import Column, create_engine, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

config = json.load(open('config.json'))
ENGINE = create_engine(config['connection_string'])
BASE = declarative_base()
SESSION = sessionmaker(bind=ENGINE)
s = SESSION()

def create():
    """ Crear la base de datos """
    engine = create_engine(config['connection_string'])
    if not database_exists(engine.url):
        create_database(engine.url)
        print('created')
    print(database_exists(engine.url))

def delete_all():
    PlaylistSongAssignation.__table__.drop(ENGINE)
    UserPlaylistAssignation.__table__.drop(ENGINE)
    Downloaded.__table__.drop(ENGINE)
    Error.__table__.drop(ENGINE)
    User.__table__.drop(ENGINE)
    Playlist.__table__.drop(ENGINE)
    Song.__table__.drop(ENGINE)

def create_all():
    """ Crear todas las tablas """
    BASE.metadata.create_all(ENGINE)

class User(BASE):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean(), default=True)
    permissions = Column(JSON)
    created = Column(Date, default=datetime.datetime.now)
    modified = Column(Date, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    playlists = relationship("UserPlaylistAssignation")

class Playlist(BASE):
    __tablename__ = 'playlist'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    source = Column(String(255))
    songs = relationship("PlaylistSongAssignation")

class Song(BASE):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    youtube_id = Column(String(255), unique=True)
    artist = Column(String(255))
    album = Column(String(255))

class Downloaded(BASE):
    __tablename__ = 'downloaded'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    playlist_id = Column(Integer, ForeignKey('playlist.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'), primary_key=True)

class Error(BASE):
    __tablename__ = 'error'
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    playlist_id = Column(Integer, ForeignKey('playlist.id'))
    song_name = Column(String(255))
    playlist_name = Column(String(255))
    description = Column(String(255))
    date = Column(Date)
    solved = Column(Boolean, default=False)

class UserPlaylistAssignation(BASE):
    """ N to M relationship between users and playlists """

    __tablename__ = 'userplaylistassignation'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    playlist_id = Column(Integer, ForeignKey('playlist.id'), primary_key=True)
    uuid = Column(String(36), default=U.gen_uuid)
    playlist = relationship("Playlist")
    last_date = Column(Date)
    last_type = Column(String)

class PlaylistSongAssignation(BASE):
    """ N to M relationship between playlists and songs """

    __tablename__ = 'playlistsongassignation'
    playlist_id = Column(Integer, ForeignKey('playlist.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'), primary_key=True)
    song = relationship("Song")
